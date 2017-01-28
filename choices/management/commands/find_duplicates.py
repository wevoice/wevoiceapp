from django.core.management.base import BaseCommand
from django.conf import settings
import os
import os.path
import sys
import hashlib


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        # call_command('remove_unused')
        final_list = self.detect_doubles(unicode(options['file_path'][0], 'utf-8'))
        for key in final_list.keys():
            n = 0
            for filename in sorted(final_list[key]):
                if n > 0:
                    os.remove(filename)
                    print "removed duplicate: " + filename
                else:
                    print "original: " + filename
                n += 1
            print "\n"
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicates'))

    def detect_doubles(self, directory):
        fileslist = {}
        # Group all files by sha of sample in the fileslist dictionary

        directory = os.path.abspath(directory)
        os.path.walk(directory, self.callback, fileslist)

        # Remove keys (filesample) in the dictionary which have only 1 file
        for (filesample, listoffiles) in fileslist.items():
            if len(listoffiles) == 1:
                del fileslist[filesample]
        return fileslist

    def callback(self, fileslist, directory, files):
        for fileName in files:
            if fileName.split('.')[-1] in settings.VALID_SOUND_FORMATS:
                filepath = os.path.join(directory, fileName)
                if os.path.isfile(filepath):
                    filesample = self.files_sha(filepath)
                    if filesample in fileslist:
                        fileslist[filesample].append(filepath)
                    else:
                        fileslist[filesample] = [filepath]

    def files_sha(self, filepath):
        """ Compute SHA (Secure Hash Algorythm) of a target_file.
            Input : filepath : full path and name of file (eg. 'c:\windows\emm386.exe')
            Output : string : contains the hexadecimal representation of the SHA of the target_file.
                              returns '0' if file could not be read (file not found, no read rights...)
        """
        sha = hashlib.sha1()
        try:
            data = None
            with open(filepath, 'rb', 0) as f:
                while True:
                    chunk = f.read(65536)
                    if chunk:
                        data = chunk
                    else:
                        break
            sha.update(data)
            sha1 = sha.hexdigest()
        except Exception as file_error:
            self.print_error(file_error)
            return '0'
        else:
            return sha1

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
