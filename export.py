# # Example of a model in your legacy app:
#
# class OldNotes(models.Model):
#    title = models.CharField(max_length=256)
#    text = models.TextField()
#

# # Example of a model in one of your new apps, awesomeapp:
#
# HEADER_LEN = 256
# class AwesomeNotes(models.Model):
#    header = models.CharField(max_length=HEADER_LEN)
#    body = models.TextField()
#

from apps.legacy.models import OldNotes
from apps.awesomeapp.models import AwesomeNotes, HEADER_LEN

for old_note in OldNotes.objects.all():
    # The old note title is transformed and used
    # as the awesome note header.
    header = old_note.title.upper()[:HEADER_LEN]
    body = old_note.text
    AwesomeNotes.objects.create(header=header, body=body)