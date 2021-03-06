Commands
========

v2 Database Migration
---------------------

Use this command to migrate from a previous database to a new v2 database.

Reset the database
::

    ./manage.py reset_db


Run the migration
::

    ./manage.py migrate_v2 [source database alias]


Development Email Test
----------------------

::

    Usage:
        manage.py development_email_test [app_label].[model] [id] --recipient=[recipient]

    Recipient can be a user id, user email, or one of the following:
        students, educators, professionals, all

    Example:
        manage.py development_email_test forum.question 1 --recipient=1
        manage.py development_email_test forum.question 1 --recipient=user@domain.com
        manage.py development_email_test forum.answer 1 --recipient=all
        manage.py development_email_test forum.answer 1 --recipient=students
        manage.py development_email_test forum.question 1 --recipient=educators
        manage.py development_email_test forum.question 1 --recipient=professionals

