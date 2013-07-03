from django.db import connections, connection as default_connection
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.auth import models as auth_models

from forum import models as forum_models
from forum_modules.openidauth import models as openidauth_models


CONSTRAINTS = {
    'auth_user': {
        'DROP': """
            ALTER TABLE auth_user DROP CONSTRAINT auth_user_username_key;
            """,
        'ADD': """
            ALTER TABLE auth_user
                ADD CONSTRAINT auth_user_username_key UNIQUE(username );
            """,
    },
    'forum_node': {
        'DROP': """
            ALTER TABLE forum_node DROP CONSTRAINT parent_id_refs_id_1d7ae97d;
            ALTER TABLE forum_node DROP CONSTRAINT abs_parent_id_refs_id_1d7ae97d;
            ALTER TABLE forum_node DROP CONSTRAINT active_revision_id_refs_id_5a9f972a;
            ALTER TABLE forum_node DROP CONSTRAINT extra_ref_id_refs_id_1d7ae97d;
            ALTER TABLE forum_node DROP CONSTRAINT forum_node_author_id_fkey;
            ALTER TABLE forum_node DROP CONSTRAINT forum_node_last_activity_by_id_fkey;
            ALTER TABLE forum_node DROP CONSTRAINT last_edited_id_refs_id_2d978e9f;
            """,
        'ADD': """
            ALTER TABLE forum_node
                ADD CONSTRAINT parent_id_refs_id_1d7ae97d FOREIGN KEY (parent_id)
                    REFERENCES forum_node (id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT abs_parent_id_refs_id_1d7ae97d FOREIGN KEY (abs_parent_id)
                    REFERENCES forum_node (id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT active_revision_id_refs_id_5a9f972a FOREIGN KEY (active_revision_id)
                    REFERENCES forum_noderevision (id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT extra_ref_id_refs_id_1d7ae97d FOREIGN KEY (extra_ref_id)
                    REFERENCES forum_node (id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT forum_node_author_id_fkey FOREIGN KEY (author_id)
                    REFERENCES forum_user (user_ptr_id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT forum_node_last_activity_by_id_fkey FOREIGN KEY (last_activity_by_id)
                    REFERENCES forum_user (user_ptr_id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            ALTER TABLE forum_node
                ADD CONSTRAINT last_edited_id_refs_id_2d978e9f FOREIGN KEY (last_edited_id)
                    REFERENCES forum_action (id) MATCH SIMPLE
                    ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
            """
    }
}

replacements = {
}


class Column(object):
    def __init__(self, column):
        self.column = column


class Copy(object):
    def __init__(self, field, model=None):
        self.field = field
        self.model = model


class Value(object):
    def __init__(self, value):
        self.value = value


def drop_constraints(table_name):
    """ Drop the constraints associated to the specified table.
    """
    print 'Dropping constraints in \'%s\'.' % table_name
    cursor = default_connection.cursor()
    cursor.execute(CONSTRAINTS[table_name]['DROP'])
    cursor.close()


def add_constraints(table_name):
    """ Restore the constraints associated to the specified table.
    """
    print 'Restoring constraints in \'%s\'.' % table_name
    cursor = default_connection.cursor()
    cursor.execute(CONSTRAINTS[table_name]['ADD'])
    cursor.close()


def perform_sync_sequence(table, sequence_name=None, primary_key='id'):
    """ Synchronize the next ID of a sequence.
    :param table: Name of the table from which to fetch the next ID
    :param sequence_name: Name of the sequence to sync
    :param primary_key: Primary key of the table
    """
    cursor = default_connection.cursor()

    # Get sequence name
    if not sequence_name:
        sequence_name = '%s_%s_seq' % (table, primary_key)

    # Get next ID
    cursor.execute('SELECT MAX(%s) FROM %s' % (primary_key, table))
    (max_id,) = cursor.fetchone()
    if not max_id:
        cursor.close()
        return
    next_id = max_id + 1

    # Update sequence
    cursor.execute('SELECT setval(\'%s\', %d)' % (sequence_name, next_id))
    cursor.close()


def get_columns(connection, table):
    """ Get a dictionary containing the names of the columns in the table as keys and their positions as values.
    """
    cursor = connection.cursor()
    cursor.execute('SELECT column_name, ordinal_position FROM information_schema.columns \
                    WHERE table_name = \'%s\'' % table)

    columns = {}
    for column_name, ordinal_position in cursor.fetchall():
        columns[column_name] = ordinal_position - 1

    return columns


def prepare_pairing(connection, table, pairing):
    """ Prepare pairing for its use.
    """
    columns = get_columns(connection, table)

    new_pairing = []

    for field, source in pairing:
        # Get column position from column name
        if isinstance(source, Column):
            if type(source.column) == str:
                source.column = columns[source.column]

        new_pairing.append((field, source))

    return new_pairing


def perform_import(connection, table, model, pairing, processors=None, from_parent=None, sync_sequence=True):
    """ Import data from a table.
    :param connection: Database connection
    :param table: Name of the table from which to fetch rows
    :param model: Destination model
    :param pairing: Dictionary containing source and field name in the model
    :param processors: Processors
    :param from_parent: Used with model inheritance
    :param sync_sequence: Whether to perform sync sequence
    """
    print 'Importing %s.%s objects.' % (model._meta.app_label, model.__name__)

    # Prepare pairing
    pairing = prepare_pairing(connection, table, pairing)

    # Delete existing objects
    model.objects.all().delete()

    # Perform import
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM %s' % table)

    while True:
        # Fetch row
        row = cursor.fetchone()
        if row is None:
            break

        # New object
        obj_id = row[0]
        if from_parent:
            obj = from_parent.objects.get(id=obj_id)
            obj.__class__ = model
        else:
            obj = model()
            obj.id = obj_id

        # Set rest of fields
        for field, source in pairing:
            # Get value
            if source is None:
                continue
            elif isinstance(source, Column):
                value = row[source.column]
            elif isinstance(source, Copy):
                if source.model:
                    try:
                        value = getattr(source.model.objects.get(id=obj_id), source.field)
                    except source.model.DoesNotExist:
                        continue
                else:
                    value = getattr(obj, source.field)
            elif isinstance(source, Value):
                value = source.value
            else:
                value = source(connection, obj_id)

            # Call processor
            if processors:
                processor = processors.get(field)
                if processor:
                    value = processor(value)

            # Set value
            setattr(obj, field, value)

        # Save
        if forum_models.BaseModel in model.__bases__:
            obj.save(full_save=True)
        else:
            obj.save()

    # Close cursor
    cursor.close()

    # Sync sequence
    if sync_sequence:
        perform_sync_sequence(table)


def perform_raw_import(connection, table, pairing,
                       destination_table=None, destination_connection=default_connection,
                       processors=None, sync_sequence=True):
    """ Perform RAW import from a table in the source database to a table in the default database.
    :param connection: Source database connection
    :param table: Source table
    :param pairing: Pairing
    :param destination_table: Destination table
    :param destination_connection: Destination database connection
    :param processors: Processors
    :param sync_sequence: Whether to perform sync sequence
    """
    if not destination_table:
        destination_table = table

    print '[RAW] Importing from table \'%s\' to table \'%s\'.' % (table, destination_table)

    # Prepare pairing
    pairing = prepare_pairing(connection, table, pairing)

    # Source
    source_cursor = connection.cursor()
    source_cursor.execute('SELECT * FROM %s' % table)

    # Destination
    destination_cursor = destination_connection.cursor()
    destination_cursor.execute('DELETE FROM %s' % destination_table)

    while True:
        # Fetch row
        row = source_cursor.fetchone()
        if row is None:
            break

        # Get ID
        obj_id = row[0]

        # Get values
        values = []
        columns = []
        for destination, source in pairing:
            if source is None:
                continue
            elif isinstance(source, Column):
                value = row[source.column]
            elif isinstance(source, Value):
                value = source.value
            else:
                value = source(connection, obj_id)

            # Call processor
            if processors:
                processor = processors.get(destination)
                if processor:
                    value = processor(value)

            values.append(value)
            columns.append(destination)

        # Execute insertion
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (destination_table,
                                                     ', '.join(columns),
                                                     ', '.join(['%s'] * len(values)))
        destination_cursor.execute(query, values)

    # Close cursor
    source_cursor.close()
    destination_cursor.close()

    # Sync sequence
    if sync_sequence:
        perform_sync_sequence(table)


def perform_m2m_import(connection, table,
                       parent_model, m2m_field, child_model,
                       parent_column=Column(1), child_column=Column(2),
                       parent_processor=None, child_processor=None):
    """ Import data from a many to many relationship table.
    :param connection: Database connection
    :param table: Name of the table from which to fetch rows
    :param parent_model: Model that contains the ManyToManyField
    :param m2m_field: Name of the ManyToManyField
    :param child_model: Model to which the ManyToManyField references
    :param parent_column: Column corresponding to the IDs of parent_model
    :param child_column: Column corresponding to the IDs of child_model
    :param parent_processor: Processor for the field in the parent model
    :param child_processor: Processor for the field in the child model
    """
    print 'Importing \'%s\' relationship of %s.%s and %s.%s objects.' % (
            m2m_field, parent_model._meta.app_label, parent_model.__name__,
            child_model._meta.app_label, child_model.__name__)

    if not isinstance(parent_column, Column) and not isinstance(child_column, Column):
        return

    # Get columns positions by their names
    columns = get_columns(connection, table)
    if type(parent_column.column) == str:
        parent_column.column = columns[parent_column.column]
    if type(child_column) == str:
        child_column.column = columns[child_column]

    # Get cursor
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM %s' % table)

    while True:
        # Fetch row
        row = cursor.fetchone()
        if row is None:
            break

        # Get parent
        parent_value = row[parent_column.column]
        if parent_processor:
            parent_value = parent_processor(parent_value)
        parent = parent_model.objects.get(pk=parent_value)

        # Save child
        child_value = row[child_column.column]
        if child_processor:
            child_value = child_processor(child_value)
        getattr(parent, m2m_field).add(child_model.objects.get(pk=child_value))

    # Close cursor
    cursor.close()

    # Sync sequence
    perform_sync_sequence(table)


def import_django_content_type(connection):
    perform_import(connection, 'django_content_type', ContentType, [
        ('name', Column(1)),
        ('app_label', Column(2)),
        ('model', Column(3)),
    ])


def import_django_site(connection):
    perform_import(connection, 'django_site', Site, [
        ('domain', Column(1)),
        ('name', Column(2)),
    ])


def import_auth_permission(connection):
    perform_import(connection, 'auth_permission', auth_models.Permission, [
        ('name', Column(1)),
        ('content_type_id', Column(2)),
        ('codename', Column(3)),
    ])


def import_auth_group(connection):
    perform_import(connection, 'auth_group', auth_models.Group, [
        ('name', Column(1)),
    ])


def import_auth_group_permissions(connection):
    perform_m2m_import(connection, 'auth_group_permissions',
                       auth_models.Group, 'permissions', auth_models.Permission)


def get_real_name(connection, obj_id):
    cursor = connection.cursor()
    cursor.execute('SELECT real_name FROM forum_user WHERE user_ptr_id=%s LIMIT 1' % obj_id)
    (real_name,) = cursor.fetchone()
    cursor.close()
    return real_name


def infer_first_name(connection, obj_id):
    real_name = get_real_name(connection, obj_id)
    split = real_name.split()
    if len(split) >= 2:
        return ' '.join(split[:-1])
    else:
        return ''


def infer_last_name(connection, obj_id):
    real_name = get_real_name(connection, obj_id)
    split = real_name.split()
    if split:
        return split[-1]
    else:
        return ''


def username_processor(username):
    return username.lower()


def import_auth_user(connection):
    drop_constraints('auth_user')

    perform_import(connection, 'auth_user', auth_models.User, [
        ('first_name', infer_first_name),
        ('last_name', infer_last_name),

        ('email', Column('email')),
        ('password', Column('password')),
        ('is_staff', Column(6)),
        ('is_active', Column(7)),
        ('is_superuser', Column(8)),
        ('last_login', Column(9)),
        ('date_joined', Column(10)),

        ('username', Copy('email')),
    ], processors={
        'username': username_processor,
    })


def import_auth_user_groups(connection):
    perform_m2m_import(connection, 'auth_user_groups',
                       auth_models.User, 'groups', auth_models.Group)


def import_auth_user_user_permissions(connection):
    perform_m2m_import(connection, 'auth_user_user_permissions',
                       auth_models.User, 'user_permissions', auth_models.Permission)


def infer_user_type(connection, obj_id):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM forum_cohort_educators WHERE user_id=%s LIMIT 1' % obj_id)
    if cursor.fetchone():
        cursor.close()
        return forum_models.User.TYPE_EDUCATOR
    else:
        cursor.execute('SELECT * FROM forum_cohort_students WHERE user_id=%s LIMIT 1' % obj_id)
        if cursor.fetchone():
            cursor.close()
            return forum_models.User.TYPE_STUDENT
        else:
            node_query = 'SELECT * FROM forum_node WHERE author_id=%s AND node_type=\'%s\' LIMIT 1'

            cursor.execute(node_query % (obj_id, 'question'))
            asked = cursor.fetchone() is None

            cursor.execute(node_query % (obj_id, 'answer'))
            answered = cursor.fetchone() is None

            if asked and not answered:
                cursor.close()
                return forum_models.User.TYPE_STUDENT
            else:
                cursor.close()
                return forum_models.User.TYPE_PROFESSIONAL


def import_forum_user(connection):
    perform_raw_import(connection, 'forum_user', [
        ('user_ptr_id', Column(0)),

        ('type', infer_user_type),

        ('is_approved', Column(1)),
        ('email_isvalid', Column(2)),

        ('reputation', Column(3)),
        ('gold', Column(4)),
        ('silver', Column(5)),
        ('bronze', Column(6)),
        ('referral_count', Value(0)),

        ('last_seen', Column(7)),
        ('website', Column(9)),
        ('location', Column(10)),
        ('date_of_birth', Column(11)),
        ('about', Column(12)),
        ('headline', Value('')),
        ('industry', Value('')),

        ('facebook_uid', None),
        ('facebook_email', None),
        ('facebook_access_token', None),
        ('facebook_access_token_expires_on', None),

        ('linkedin_uid', None),
        ('linkedin_email', None),
        ('linkedin_access_token', None),
        ('linkedin_access_token_expires_on', None),
        ('linkedin_photo_url', None),
    ], sync_sequence=False)


def import_forum_userproperty(connection):
    perform_import(connection, 'forum_userproperty', forum_models.user.UserProperty, [
        ('user_id', Column(1)),
        ('key', Column(2)),
        ('value', Column(3)),
    ])


def import_forum_badge(connection):
    perform_import(connection, 'forum_badge', forum_models.Badge, [
        ('type', Column(1)),
        ('cls', Column(2)),
        ('awarded_count', Column(3)),
    ])


def import_forum_tag(connection):
    print 'Importing forum.Tag objects and registering duplicates.'

    # Get cursor
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM forum_tag')

    # Delete current tags
    forum_models.Tag.objects.all().delete()

    # Create replacements dictionary
    replacements['forum_tag'] = {}

    while True:
        # Fetch row
        row = cursor.fetchone()
        if row is None:
            break

        # Unpack row
        obj_id, name, created_by_id, created_at, used_count = row
        try:
            slug = forum_models.Tag.make_slug(name)
            tag = forum_models.Tag.objects.get(slug=slug)
        except forum_models.Tag.DoesNotExist:
            tag = None

        # Save tag
        if tag:
            replacements['forum_tag'][obj_id] = tag.id
        else:
            tag = forum_models.Tag(id=obj_id, name=name,
                                   created_by_id=created_by_id, created_at=created_at,
                                   used_count=used_count)
            tag.save(full_save=True)

    cursor.close()

    # Sync sequence
    perform_sync_sequence('forum_tag')


def tag_id_processor(tag_id):
    if tag_id in replacements['forum_tag'].keys():
        return replacements['forum_tag'][tag_id]
    else:
        return tag_id


def import_forum_markedtag(connection):
    perform_import(connection, 'forum_markedtag', forum_models.MarkedTag, [
        ('tag_id', Column(1)),
        ('user_id', Column(2)),
        ('reason', Column(3)),
    ], processors={
        'tag_id': tag_id_processor,
    })


def import_forum_node(connection):
    drop_constraints('forum_node')

    perform_import(connection, 'forum_node', forum_models.Node, [
        # NodeContent
        ('title', Column(1)),
        ('tagnames', Column(2)),
        ('author_id', Column(3)),
        ('body', Column(4)),

        # Node
        ('node_type', Column(5)),
        ('parent_id', Column(6)),
        ('abs_parent_id', Column(7)),

        ('added_at', Column(8)),
        ('score', Column(9)),

        ('state_string', Column(10)),
        ('last_edited_id', Column(11)),

        ('last_activity_by_id', Column(12)),
        ('last_activity_at', Column(13)),

        ('active_revision_id', Column(14)),

        ('extra', Column(15)),
        ('extra_ref', Column(16)),
        ('extra_count', Column(17)),

        ('marked', Column(18)),
    ])


def import_forum_noderevision(connection):
    perform_import(connection, 'forum_noderevision', forum_models.NodeRevision, [
        # NodeContent
        ('title', Column(1)),
        ('tagnames', Column(2)),
        ('author_id', Column(3)),
        ('body', Column(4)),

        # NodeRevision
        ('node_id', Column(5)),
        ('summary', Column(6)),
        ('revision', Column(7)),
        ('revised_at', Column(8)),
    ])


def import_forum_action(connection):
    perform_import(connection, 'forum_action', forum_models.Action, [
        ('user_id', Column(1)),
        ('real_user_id', Column(2)),
        ('ip', Column(3)),
        ('node_id', Column(4)),
        ('action_type', Column(5)),
        ('action_date', Column(6)),
        ('extra', Column(7)),
        ('canceled', Column(8)),
        ('canceled_by_id', Column(9)),
        ('canceled_at', Column(10)),
        ('canceled_ip', Column(11)),
    ])

    add_constraints('forum_node')


def update_tagnames():
    """ Update the value of the tagnames field in the Node objects.
    """
    print 'Updating tagnames field in forum.Node objects.'

    for node in forum_models.Node.objects.all():
        tags = node.tags.all()
        if tags:
            node.tagnames = u' '.join([tag.name for tag in tags])
            node.save()


def import_forum_node_tags(connection):
    perform_m2m_import(connection, 'forum_node_tags',
                       forum_models.Node, 'tags', forum_models.Tag,
                       child_processor=tag_id_processor)
    update_tagnames()


def import_forum_actionrepute(connection):
    perform_import(connection, 'forum_actionrepute', forum_models.ActionRepute, [
        ('action_id', Column(1)),
        ('date', Column(2)),
        ('user_id', Column(3)),
        ('value', Column(4)),
        ('by_canceled', Column(5)),
    ])


def import_forum_award(connection):
    perform_import(connection, 'forum_award', forum_models.Award, [
        ('user_id', Column(1)),
        ('badge_id', Column(2)),
        ('node_id', Column(3)),

        ('awarded_at', Column(4)),

        ('trigger_id', Column(5)),
        ('action_id', Column(6)),
    ])


def import_forum_flag(connection):
    perform_import(connection, 'forum_flag', forum_models.Flag, [
        ('user_id', Column(1)),
        ('node_id', Column(2)),
        ('reason', Column(3)),
        ('action_id', Column(4)),
        ('flagged_at', Column(5)),
    ])


def import_forum_keyvalue(connection):
    perform_import(connection, 'forum_keyvalue', forum_models.KeyValue, [
        ('key', Column(1)),
        ('value', Column(2)),
    ])


def import_forum_nodestate(connection):
    perform_import(connection, 'forum_nodestate', forum_models.NodeState, [
        ('node_id', Column(1)),
        ('state_type', Column(2)),
        ('action_id', Column(3)),
    ])


def import_forum_vote(connection):
    perform_import(connection, 'forum_vote', forum_models.Vote, [
        ('user_id', Column(1)),
        ('node_id', Column(2)),
        ('value', Column(3)),
        ('action_id', Column(4)),
        ('voted_at', Column(5))
    ])


def import_forum_questionsubscription(connection):
    perform_import(connection, 'forum_questionsubscription', forum_models.QuestionSubscription, [
        ('user_id', Column(1)),
        ('question_id', Column(2)),
        ('auto_subscription', Column(3)),
        ('last_view', Column(4))
    ])


def import_forum_subscriptionsettings(connection):
    perform_import(connection, 'forum_subscriptionsettings', forum_models.SubscriptionSettings, [
        ('user_id', Column(1)),

        ('enable_notifications', Column(2)),

        ('member_joins', Column(3)),
        ('new_question', Column(4)),
        ('new_question_watched_tags', Column(5)),
        ('subscribed_questions', Column(6)),

        ('all_questions', Column(7)),
        ('all_questions_watched_tags', Column(8)),
        ('questions_viewed', Column(9)),

        ('notify_answers', Column(10)),
        ('notify_reply_to_comments', Column(11)),
        ('notify_comments_own_post', Column(12)),
        ('notify_comments', Column(13)),
        ('notify_accepted', Column(14)),

        ('send_digest', Column(15)),
    ])


def import_forum_validationhash(connection):
    perform_import(connection, 'forum_validationhash', forum_models.ValidationHash, [
        ('hash_code', Column(1)),
        ('seed', Column(2)),
        ('expiration', Column(3)),
        ('type', Column(4)),
        ('user_id', Column(5)),
    ])


def import_forum_authkeyuserassociation(connection):
    perform_import(connection, 'forum_authkeyuserassociation', forum_models.AuthKeyUserAssociation, [
        ('key', Column(1)),
        ('provider', Column(2)),
        ('user_id', Column(3)),
        ('added_at', Column(4)),
    ])


def import_forum_cohort(connection):
    perform_import(connection, 'forum_cohort', forum_models.Cohort, [
        ('name', Column(1)),
        ('created_at', Column(2)),
        ('kickoff_date', Column(3)),
    ])


def import_forum_cohort_educators(connection):
    perform_m2m_import(connection, 'forum_cohort_educators',
                       forum_models.Cohort, 'educators', forum_models.User)


def import_forum_cohort_students(connection):
    perform_m2m_import(connection, 'forum_cohort_students',
                       forum_models.Cohort, 'students', forum_models.User)


def import_forum_openidassociation(connection):
    perform_import(connection, 'forum_openidassociation', openidauth_models.OpenIdAssociation, [
        ('server_url', Column(1)),
        ('handle', Column(2)),
        ('secret', Column(3)),
        ('issued', Column(4)),
        ('lifetime', Column(5)),
        ('assoc_type', Column(6)),
    ])


def import_forum_openidnonce(connection):
    perform_import(connection, 'forum_openidnonce', openidauth_models.OpenIdNonce, [
        ('server_url', Column(1)),
        ('timestamp', Column(2)),
        ('salt', Column(3)),
    ])


def merge_users(connection, keeping_order):
    """ Merge duplicate users with the same email address.

    Determine which user stays according to the keeping_order. This means that if the order is '-reputation' the user
    with greatest reputation is the one in which duplicates are merged into. To preserve the user that joined first
    use 'date_joined' as keeping_order.
    """
    # Get database cursor
    cursor = connection.cursor()

    # Find duplicate users by their emails
    cursor.execute('SELECT lower(email) AS l_email FROM auth_user GROUP BY l_email HAVING COUNT(id) > 1;')

    while True:
        # Fetch row
        row = cursor.fetchone()
        if row is None:
            break

        # Get email
        (email,) = row

        # Find master user and its duplicates
        users = list(forum_models.User.objects.filter(email__iexact=email).order_by(keeping_order))

        master = users[0]
        duplicates = users[1:]

        # Merge
        if duplicates:
            # Display merge
            print 'Merging %s into %s.' % (', '.join([user.email for user in duplicates]), master.email)

            # Perform merge
            for duplicate in duplicates:

                # Add reputation to the master's reputation
                master.reputation += duplicate.reputation
                master.save()

                # forum_userproperty
                # Ignored

                # forum_tag
                for tag in duplicate.created_tags.all():
                    tag.created_by = master
                    tag.save()

                # forum_markedtag
                for markedtag in duplicate.tag_selections.filter(reason='good'):
                    try:
                        _markedtag = master.tag_selections.get(tag=markedtag.tag)
                    except forum_models.MarkedTag.DoesNotExist:
                        _markedtag = forum_models.MarkedTag(tag=markedtag.tag, user=master)

                    _markedtag.reason = 'good'
                    _markedtag.save()

                # forum_node
                for node in duplicate.nodes.all():
                    node.author = master
                    node.save()

                # forum_action
                for action in duplicate.actions.all():
                    action.user = master
                    action.save()
                for action in duplicate.proxied_actions.all():
                    action.real_user = master
                    action.save()

                # forum_actionrepute
                for actionrepute in duplicate.reputes.all():
                    actionrepute.user = master
                    actionrepute.save()

                # forum_award
                for award in duplicate.award_set.exclude(
                        badge_id__in=master.award_set.values_list('badge_id', flat=True).query):
                    award.user = master
                    award.save()

                # forum_flag
                for flag in duplicate.flags.exclude(node_id__in=master.flags.values_list('node_id', flat=True).query):
                    flag.user = master
                    flag.save()

                # forum_vote
                for vote in duplicate.votes.exclude(node_id__in=master.votes.values_list('node_id', flat=True).query):
                    vote.user = master
                    vote.save()

                # forum_questionsubscription
                for questionsubscription in duplicate.questionsubscription_set.exclude(
                        question_id__in=master.questionsubscription_set.values_list('question_id', flat=True).query):
                    questionsubscription.user = master
                    questionsubscription.save()

                # forum_subscriptionsettings
                # Ignored

                # forum_validationhash
                # Ignored

                # forum_authkeyuserassociation
                for authkeyuserassociation in duplicate.auth_keys.all():
                    authkeyuserassociation.user = master
                    authkeyuserassociation.save()

                # forum_cohort_educators
                for cohort in duplicate.educator_of.all():
                    cohort.educators.add(master)

                # forum_cohort_students
                for cohort in duplicate.student_of.all():
                    cohort.students.add(master)

                # Delete duplicate
                print 'Deleting duplicate %s.' % duplicate.username
                duplicate.delete()
        else:
            print 'Nothing to merge.'

    add_constraints('forum_user')


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get source database alias
        try:
            alias = args[0]
        except IndexError:
            print 'Migrate to a v2 database.'
            print 'Usage: manage.py migrate_v2 [source database alias]'
            return

        # Get source database connection
        connection = connections[alias]

        # Django/Auth
        # import_django_content_type(connection)
        # import_django_site(connection)
        # import_auth_permission(connection)
        # import_auth_group(connection)
        # import_auth_group_permissions(connection)
        import_auth_user(connection)  # (drops auth_user constraints)
        # import_auth_user_groups(connection)
        # import_auth_user_user_permissions(connection)

        # Forum
        # I - Ignored when merging
        # N - Does not have a related user
        # Y - Has a related user
        import_forum_user(connection)
        import_forum_userproperty(connection)  # I
        import_forum_badge(connection)  # N
        import_forum_tag(connection)  # Y
        import_forum_markedtag(connection)  # Y
        import_forum_node(connection)  # Y (drops forum_node constraints)
        import_forum_noderevision(connection)  # N
        import_forum_action(connection)  # Y (restores forum_node constraints)
        import_forum_node_tags(connection)  # N
        import_forum_actionrepute(connection)  # Y
        import_forum_award(connection)  # Y
        import_forum_flag(connection)  # Y
        import_forum_keyvalue(connection)  # N
        import_forum_nodestate(connection)  # N
        import_forum_vote(connection)  # Y
        import_forum_questionsubscription(connection)  # Y
        import_forum_subscriptionsettings(connection)  # I
        import_forum_validationhash(connection)  # I
        import_forum_authkeyuserassociation(connection)  # Y
        import_forum_cohort(connection)  # N
        import_forum_cohort_educators(connection)  # Y
        import_forum_cohort_students(connection)  # Y

        # OpenID Auth (forum_modules.openid_auth)
        import_forum_openidassociation(connection)
        import_forum_openidnonce(connection)

        # Merge users
        merge_users(connection, '-reputation')  # (restores auth_user constraints)
