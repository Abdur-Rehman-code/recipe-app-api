"""
Django command to wait for the database to be available.
"""

from django.core.management.base import BaseCommand

from psycopg2 import OperationalError as psycopg2Error

from django.db.utils import OperationalError

import time , os


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Entery point for command."""

        self.stdout.write('Waiting for database...')

    
        # print(f"HOST {os.environ.get('DB_HOST')} NAME {os.environ.get('DB_NAME')} USER {os.environ.get('DB_USER')} PASS {os.environ.get('DB_PASS')}")

        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except(psycopg2Error, OperationalError):
                self.stdout.write('Database is unavailable, waiting for 1 sec')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available!'))
