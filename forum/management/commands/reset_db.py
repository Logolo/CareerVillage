from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from optparse import make_option
import psycopg2 as Database


class Command(BaseCommand):

    help = "Resets a database"

    def handle(self, *args, **options):
        """
        Resets a database.

        Note: Transaction wrappers are in reverse as a work around for
        autocommit, anybody know how to do this the right way?
        """
        db = settings.DATABASES["default"]
        conn_params = {
            'database': 'template1',
        }
        conn_params.update(db['OPTIONS'])
        if 'autocommit' in conn_params:
            del conn_params['autocommit']
        if db['USER']:
            conn_params['user'] = db['USER']
        if db['PASSWORD']:
            conn_params['password'] = db['PASSWORD']
        if db['HOST']:
            conn_params['host'] = db['HOST']
        if db['PORT']:
            conn_params['port'] = db['PORT']
        connection = Database.connect(**conn_params)
        connection.set_client_encoding('UTF8')
        connection.set_isolation_level(0)
        cursor = connection.cursor()
        drop_query = 'DROP DATABASE %s' % db["NAME"]
        try:
            cursor.execute(drop_query)
        except Database.ProgrammingError, e:
            print str(e)
        create_query = ("CREATE DATABASE %s WITH OWNER = %s ENCODING = 'UTF8' TEMPLATE = template0;" %
                        (db["NAME"], db["USER"]))
        cursor.execute(create_query)

        call_command('syncdb', all=True, interactive=False)
        call_command('migrate', fake=True)
        #call_command('populate')


