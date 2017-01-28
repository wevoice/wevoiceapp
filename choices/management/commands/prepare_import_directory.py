from django.core.management.base import BaseCommand
import os
import os.path
import sys

from django.core.management import call_command


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            call_command('flatten_files', options['file_path'][0])
            call_command('find_duplicates', options['file_path'][0])
            call_command('create_import_excel', options['file_path'][0])
        except Exception as e:
            self.print_error(e)

        self.stdout.write(self.style.SUCCESS('Successfully prepared import set'))

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
