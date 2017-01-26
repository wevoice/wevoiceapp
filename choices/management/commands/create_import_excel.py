from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re
import sys


class Command(BaseCommand):
    help = 'Removes all unused files'

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    def handle(self, *args, **options):
        filecount = 0
        rejectedcount = 0
        for dirpath, dirnames, filenames in os.walk(options['file_path'][0]):
            filenames = [f for f in filenames if not f[0] == '_']
            for filename in filenames:
                if " " in filename:
                    newfilename = filename.replace(" ", "")
                    os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, newfilename))
                    filename = newfilename
                if len(filename.split('.')) > 1 and filename.split('.')[-1] in settings.VALID_SOUND_FORMATS:
                    filename_parts = filename.split('.')
                    filename = filename_parts[-2]
                    filetype = filename_parts[-1]
                    if re.match(r'^[A-Za-z]{2}[-|_][A-Za-z]{2}_', filename):
                        if not re.match(r'^[a-z]{2}-[A-Z]{2}_', filename):
                            newfilename = "%s-%s%s.%s" \
                                          % (filename[0:2].lower(), filename[3:5].upper(), filename[5:], filetype)
                            os.rename(os.path.join(dirpath, "%s.%s"
                                                   % (filename, filetype)), os.path.join(dirpath, newfilename))
                            filename = newfilename
                        try:
                            language = re.match(r'^[a-z]{2}-[A-Z]{2}', filename).group()
                            if len(filename.split(language)) > 0:
                                remainder = re.split(r'(_m_|_f_|_M_|_F_|_u_)', filename.split(language)[1])
                                if len(remainder) > 1:
                                    print("language: %s gender: %s talent: %s"
                                          % (language, remainder[1].strip('_').upper(), remainder[2]))
                                    filecount += 1
                                else:
                                    print("rejected: %s" % filename)
                                    rejectedcount += 1
                            else:
                                print("rejected: %s" % filename)
                                rejectedcount += 1
                        except Exception as file_error:
                            self.print_error(file_error)
                            return '0'
                    else:
                        print("rejected: %s" % filename)
                        rejectedcount += 1
        self.stdout.write(self.style.SUCCESS('Processed %s. Accepted: %s. Rejected: %s'
                                             % (options['file_path'], filecount, rejectedcount)))
