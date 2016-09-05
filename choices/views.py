import hashlib
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from forms import LoginForm
from models import Client


def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        client = None
        if form.is_valid():
            try:
                client = Client.objects.get(username=form.data['username'])
            except Client.DoesNotExist:
                return render(request, 'index.html', {'form': form})
            request.session['registered'] = client.username
            return HttpResponseRedirect('/' + client.username)
    else:
        form = LoginForm()
    return render(request, 'index.html', {'form': form})


def detail(request, client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return render(request, 'detail.html', {'client': client})


def for_approval(request, client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return render(request, 'for_approval.html', {'client': client})


def accepted(request, client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return render(request, 'accepted.html', {'client': client})


def rejected(request, client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return render(request, 'rejected.html', {'client': client})