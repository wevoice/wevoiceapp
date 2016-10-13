import os
from django.http import Http404


def validate_audiofile_extension(value):
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp3']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Only mp3 files are supported.')


def validate_imagefile_extension(value):
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Only png files are supported.')


def validate_user_is_authorized(current_user, client_name):
    if current_user.userprofile.client.username == client_name:
        pass
    elif current_user.is_superuser:
        pass
    else:
        raise Http404("You are not authorized to view this account")
