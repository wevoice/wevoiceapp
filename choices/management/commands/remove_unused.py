from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from choices.models import Talent
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Removes all unused files'

    def handle(self, *args, **options):
        filecount = 0
        for talent in Talent.objects.all():
            if os.path.exists(talent.audio_file.path):
                pass
            else:
                print("Missing file for: " + talent.welo_id)

        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                if filename.split('.')[-1] == 'mp3':
                    filecount += 1
                    try:
                        Talent.objects.get(audio_file=filename)
                    except Talent.DoesNotExist:
                        audio_file = dirpath + filename
                        os.remove(audio_file)
                        filecount -= 1
                        print('Removed: ' + filename)
                    except UnicodeDecodeError:
                        print('Unicode Error, Could not remove: ' + filename)
        self.stdout.write(self.style.SUCCESS('Successfully updated %s. Total talents: %s Total files: %s'
                                             % (settings.MEDIA_ROOT, Talent.objects.all().count(), filecount)))
