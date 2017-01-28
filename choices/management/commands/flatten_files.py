#!/usr/bin/python

from django.core.management.base import BaseCommand
import os
from os.path import exists, splitext
from os.path import join as join_path


class Command(BaseCommand):
    help = 'Creates an Excel sheet to be used for import'
    talentdata = []

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        """Move all files in subdirs to here, then delete subdirs.
           Conflicting files are renamed, with 1 appended to their name."""
        here = options['file_path'][0]
        for root, dirs, files in os.walk(here, topdown=False):
            if root != here:
                for name in files:
                    source = join_path(root, name)
                    if name[0] == '.' or name[0] == '_':
                        os.remove(source)
                    else:
                        target = self.handle_duplicates(join_path(here, name))
                        os.rename(source, target)

            for name in dirs:
                os.rmdir(join_path(root, name))
        self.stdout.write(self.style.SUCCESS('Processed %s.' % options['file_path']))

    def handle_duplicates(self, target):
        base, ext = splitext(target)
        count = 0
        while exists(target):
            count += 1
            target = base + 'count' + ext
        return target
