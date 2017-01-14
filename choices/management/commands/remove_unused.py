from django.core.management.base import BaseCommand, CommandError
from choices.models import Talent
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Removes all unused files'

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        for dirpath, dirnames, filenames in os.walk(options['file_path'][1]):
            for filename in filenames:
                try:
                    talent = Talent.objects.get(audio_file=filename)
                except Talent.DoesNotExist:
                    audio_file = dirpath + filename
                    os.remove(audio_file)
                    print('Removed: ' + filename)
                except UnicodeDecodeError:
                    print('Unicode Error, Could not remove: ' + filename)
            for talent in Talent.objects.all():
                if os.path.isfile(dirpath + str(talent.audio_file)):
                    pass
                else:
                    print("Missing file for: " + talent.welo_id)




            self.stdout.write(self.style.SUCCESS('Successfully updated "%s"' % options['file_path']))
