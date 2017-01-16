from django.core.management.base import BaseCommand, CommandError
from choices.models import Talent
import os
import sys
import hashlib


class Command(BaseCommand):
    help = 'Calculates sha for last chunk of audio_files and saves to Talent object'

    def handle(self, *args, **options):
        for talent in Talent.objects.all():
            if os.path.exists(talent.audio_file.path):
                current_file_sha = self.current_file_sha(talent.audio_file)
                talent.audio_file_sha = current_file_sha
                talent.save()

    def current_file_sha(self, current_file):
        sha = hashlib.sha1()
        current_file.seek(0)
        try:
            data = None
            while True:
                chunk = current_file.read(65536)
                if chunk:
                    data = chunk
                else:
                    break
            sha.update(data)
            sha1 = sha.hexdigest()
            current_file.seek(0)
        except Exception as file_error:
            self.print_error(file_error)
            return '0'
        else:
            return sha1

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
