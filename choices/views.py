from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from forms import LoginForm, SelectionForm, CommentForm, DeleteCommentForm
from models import Client, Talent, Selection, Comment, Rating
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from datetime import datetime
from .validators import validate_user_is_authorized


def url_redirect(request):
    return HttpResponseRedirect('/')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.data['username'], password=form.data['password'])
            if user:
                # Is the account active? It could have been disabled.
                if user.is_active:
                    # If the account is valid and active, we can log the user in.
                    # We'll send the user back to the homepage.
                    login(request, user)
                    if user.userprofile.client:
                        return HttpResponseRedirect(reverse('index', args=(user.userprofile.client.username,)))
                    elif user.is_staff or user.is_superuser or user.userprofile.vendor:
                        return HttpResponseRedirect('/admin')
                    else:
                        raise Http404("That user not found")

                else:
                    # An inactive account was used - no logging in!
                    return HttpResponse("Sorry, this Voiceover Portal account has been disabled.")
            else:
                # Bad login details were provided. So we can't log the user in.
                print("Invalid login details: {0}, {1}".format(form.data['username'], form.data['password']))
                return HttpResponse("Invalid login details supplied.")
    else:
        if request.user.is_authenticated():
            logout(request)
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def index(request, client_name):
    validate_user_is_authorized(request.user, client_name)
    client = get_client(client_name)
    return render(request, 'index.html', {
        'client': client,
    })


@login_required
def delete_comment(request):
    if request.method == "POST":
        form = DeleteCommentForm(request.POST)
        if form.is_valid():
            client = get_object_or_404(Client, pk=form.cleaned_data['client_id'])
            comment = get_object_or_404(Comment, pk=form.cleaned_data['comment_id'])
            selection = get_object_or_404(Selection, pk=form.cleaned_data['selection_id'])
            comment.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'), {
                'selection': selection,
                'client': client})
        else:
            raise Http404("That page does not exist")
    else:
        raise Http404("That page does not exist")


@login_required
def add_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            client = get_object_or_404(Client, pk=form.cleaned_data['client_id'])
            selection = get_object_or_404(Selection, pk=form.cleaned_data['selection_id'])
            if form.cleaned_data['text'] != '':
                author = request.user
                comment_text = form.cleaned_data['text']
                comment = Comment(author=author, text=comment_text, selection=selection)
                comment.save()
            if form.cleaned_data['rating'] != '':
                Rating.objects.update_or_create(
                    rater=request.user,
                    talent=selection.talent,
                    defaults={'rating': form.cleaned_data['rating']}
                )
                selection.talent.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'), {
                'selection': selection,
                'client': client})
    else:
        return Http404("That page does not exist")


@login_required
def selections(request, client_name, status, pk=None):
    validate_user_is_authorized(request.user, client_name)
    comment_form, delete_comment_form, selection_types = (None, None, None)
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=form.cleaned_data['client_id'])
            talent = Talent.objects.get(id=form.cleaned_data['talent_id'])
            talent_selection = Selection.objects.filter(client=client).filter(talent=talent)[0]
            if request.POST.get('submit') == 'ACCEPT':
                talent_selection.status = 'APPROVED'
                talent_selection.save()
            elif request.POST.get('submit') == 'REJECT':
                talent_selection.status = 'REJECTED'
                talent_selection.save()
            elif request.POST.get('submit') == 'FOR APPROVAL':
                talent_selection.status = 'PREAPPROVED'
                talent_selection.save()
            else:
                raise Http404()
    else:
        form = SelectionForm

    client = get_client(client_name)
    no_selections, selection_types = get_selections(client, status)

    if pk and int(pk) > 0:
        pk = int(pk)
        selection = get_selection(pk)
        selection.last_modified = datetime.now()
        selection.save()
        comment_form = CommentForm
        delete_comment_form = DeleteCommentForm

    return render(request, 'selections.html', {
        'client': client,
        'form': form,
        'comment_form': comment_form,
        'delete_comment_form': delete_comment_form,
        'pk': pk,
        'status': status,
        'no_selections': no_selections,
        'selection_types': selection_types
    })


def get_selections(client, status):
    no_selections = False
    status_filter_dict = {
        'for_approval': 'PREAPPROVED',
        'accepted': 'APPROVED',
        'rejected': 'REJECTED'
    }
    status_filter = None
    if status in ['for_approval', 'accepted', 'rejected']:
        status_filter = status_filter_dict[status]
    all_selections = client.selection_set.filter(status=status_filter).order_by('talent__language')
    if all_selections.count() == 0:
        no_selections = True
    selection_types = []
    for type_filter in ["PRO", "HR", "TTS"]:
        currentselections = all_selections.filter(talent__type=type_filter)
        if currentselections.exists():
            selection_types.append({
                'selections': currentselections,
                'type': type_filter
            })
    return no_selections, selection_types


def get_client(client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return client


def get_selection(pk):
    try:
        selection = Selection.objects.get(pk=pk)
    except Selection.DoesNotExist:
        raise Http404("That selection does not exist")
    return selection
