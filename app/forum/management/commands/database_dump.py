import logging
from optparse import make_option
from subprocess import Popen, PIPE
from os import remove
from datetime import datetime

from django.core.management.base import BaseCommand
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from forum.settings import djsettings as settings


TEMP_DIR = 'tmp'

# Obtain logger
logger = logging.getLogger('forum.management.commands.database_dump')

# Obtain S3 connection
connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--db', action='store', dest='db_name', help='PostgreSQL database name.', type='string'),
        make_option('--output', action='store', dest='output', help='Dump filename.', type='string'),
        make_option('--upload', action='store', dest='upload', help='Whether to upload (yes/no).', type='string'),
    )

    def handle(self, *args, **options):
        # Whether to upload to S3 or not
        upload = options.get('upload')
        if upload is None or upload == 'yes':
            upload = True
        else:
            upload = False

        # Get database name
        database_name = options.get('db_name')
        if not database_name:
            database = settings.DATABASES.get('default')
            if not database:
                print 'Database not configured.'
                return

            database_name = database.get('NAME')
            if not database_name:
                print 'Database name not found in settings.'
                return

        # Get dump file name
        dump_filename = options.get('output')
        if not dump_filename:
            dump_filename = '%s_%s.sql' % (datetime.now().strftime('%Y-%m-%d_%H:%M'), database_name)
        dump_file_path = '/'.join([TEMP_DIR, dump_filename])

        # Execute pg_dump command
        print 'Dumping...'
        command = ['sudo', 'su', '-', 'postgres', '-c', 'pg_dump %s' % database_name]
        dump_pipe = Popen(command, stdout=open(dump_file_path, 'w'), stderr=PIPE)

        # Handle messages
        message = dump_pipe.stderr.read()
        if message:
            remove(dump_filename)
            logger.error(message)
            raise Exception(message)

        logger.info('Database \'%s\' dumped to \'%s\'.' % (database_name, dump_filename))

        # Upload to S3
        if upload:
            bucket = connection.get_bucket('careervillage-backup')
            print 'Currently stored dumps:'
            list = bucket.list()
            if list:
                for key in list:
                    print ' - %s' % key.key
            else:
                print 'No dumps made.'

            key = Key(bucket)
            key.key = dump_filename
            print 'Uploading...'
            key.set_contents_from_filename(dump_file_path)

            logger.info('Dump \'%s\' uploaded to storage.' % dump_filename)
