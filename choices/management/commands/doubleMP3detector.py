from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from choices.models import Talent, Selection
from . import remove_unused
import os
import os.path
import string
import sys
import sha as shafunction
from choices.models import Talent, Selection
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('remove_unused')
        final_list = self.detect_doubles(settings.MEDIA_ROOT)
        for key in final_list.keys():
            n = 0
            for filename in final_list[key]:
                if n > 0:
                    talent_sample = filename.split('/')[-1]
                    try:
                        talent_object = Talent.objects.get(audio_file=talent_sample)
                        print("deleted: " + talent_object.welo_id)
                        if talent_object and talent_object.selection_set.all().count() > 0:
                            main_talent = Talent.objects.get(audio_file=final_list[key][n].split('/')[-1])
                            selections_list = []
                            for s in talent_object.selection_set.all():
                                selections_list.append([main_talent, s.client, s.status])
                            talent_object.delete()
                            for sl in selections_list:
                                try:
                                    new_s = Selection(sl[0], sl[1], sl[2])
                                    new_s.save()
                                except Exception as error:
                                    self.print_error(error)
                        else:
                            talent_object.delete()
                    except Talent.DoesNotExist:
                        pass
                    except Exception as e:
                        self.print_error(e)
                else:
                    print filename
                n += 1
            print "\n"
        self.stdout.write(self.style.SUCCESS('Successfully updated "%s"' % settings.MEDIA_ROOT))

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
            if fileName.split('.')[-1] == 'mp3':
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
        try:
            data = None
            with open(filepath, 'rb', 0) as f:
                while True:
                    chunk = f.read(65536)
                    if chunk:
                        data = chunk
                    else:
                        break
            digest = shafunction.new()
            digest.update(data)
        except Exception as file_error:
            self.print_error(file_error)
            return '0'
        else:
            return digest.hexdigest()

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
