from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from forms import LoginForm, SelectionForm, CommentForm, DeleteCommentForm
from models import Client, Talent, Selection, Comment, Rating
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.files import File
from django.conf import settings
import os


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
                    elif user.userprofile.vendor:
                        return HttpResponseRedirect('/admin')
                    else:
                        raise Http404("That user not found")

                else:
                    # An inactive account was used - no logging in!
                    return HttpResponse("Sorry, this WeVoice account has been disabled.")
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
    client = get_client(client_name)
    return render(request, 'index.html', {
        'client': client,
    })


@login_required
def delete_comment(request, client_name, pk):
    client = get_client(client_name)
    selection = get_object_or_404(Selection, pk=pk)
    if request.method == "POST":
        form = DeleteCommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.get(id=form.cleaned_data['comment_id'])
            comment.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'), {
            'selection': selection,
            'client': client})
    else:
        raise Http404("That page does not exist")


@login_required
def add_comment(request, client_name, pk):
    client = get_client(client_name)
    selection = get_object_or_404(Selection, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['text'] != '':
                author = request.user.userprofile
                comment_text = form.cleaned_data['text']
                comment = Comment(author=author, text=comment_text, post=selection)
                comment.save()
            if form.cleaned_data['rating'] != '':
                Rating.objects.update_or_create(
                    rater=request.user.userprofile,
                    talent=selection.talent,
                    defaults={'rating': form.cleaned_data['rating']}
                )
                selection.talent.times_rated = int(Rating.objects.filter(talent=selection.talent).count())
                selection.talent.total_rating = Rating.objects.filter(talent=selection.talent).aggregate(Sum('rating'))['rating__sum']
                selection.talent.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'), {
                'selection': selection,
                'client': client})
    else:
        return Http404("That page does not exist")


@login_required
def for_approval(request, client_name, pk=None):
    comment_form = None
    delete_comment_form = None
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
            else:
                raise Http404()
    else:
        form = SelectionForm

    client = get_client(client_name)
    selections = Selection.objects.filter(client=client).filter(status='PREAPPROVED')
    pro_selections = selections.filter(talent__hr="n").filter(talent__tts="n")
    home_selections = selections.filter(talent__hr="y")
    tts_selections = selections.filter(talent__tts="y")

    if pk:
        pk = int(pk)
        comment_form = CommentForm
        delete_comment_form = DeleteCommentForm

    return render(request, 'for_approval.html', {
        'client': client,
        'form': form,
        'comment_form': comment_form,
        'delete_comment_form': delete_comment_form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections,
        'pk': pk
    })


@login_required
def accepted(request, client_name, pk=None):
    comment_form = None
    delete_comment_form = None
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=form.cleaned_data['client_id'])
            talent = Talent.objects.get(id=form.cleaned_data['talent_id'])
            talent_selection = Selection.objects.filter(client=client).filter(talent=talent)[0]
            if request.POST.get('submit') == 'REJECT':
                talent_selection.status = 'REJECTED'
                talent_selection.save()
            elif request.POST.get('submit') == 'FOR APPROVAL':
                talent_selection.status = 'PREAPPROVED'
                talent_selection.save()
            elif request.POST.get('submit') == 'ACCEPT':
                pass
            else:
                raise Http404()
    else:
        form = SelectionForm

    client = get_client(client_name)
    selections = Selection.objects.filter(client=client).filter(status='APPROVED')
    pro_selections = selections.filter(talent__hr="n").filter(talent__tts="n")
    home_selections = selections.filter(talent__hr="y")
    tts_selections = selections.filter(talent__tts="y")

    if pk:
        pk = int(pk)
        comment_form = CommentForm
        delete_comment_form = DeleteCommentForm

    return render(request, 'accepted.html', {
        'client': client,
        'form': form,
        'comment_form': comment_form,
        'delete_comment_form': delete_comment_form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections,
        'pk': pk,
    })


@login_required
def rejected(request, client_name, pk=None):
    comment_form = None
    delete_comment_form = None
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            client = Client.objects.get(id=form.cleaned_data['client_id'])
            talent = Talent.objects.get(id=form.cleaned_data['talent_id'])
            talent_selection = Selection.objects.filter(client=client).filter(talent=talent)[0]
            if request.POST.get('submit') == 'REJECT':
                pass
            elif request.POST.get('submit') == 'FOR APPROVAL':
                talent_selection.status = 'PREAPPROVED'
                talent_selection.save()
            elif request.POST.get('submit') == 'ACCEPT':
                talent_selection.status = 'APPROVED'
                talent_selection.save()
            else:
                raise Http404()
    else:
        form = SelectionForm

    if pk:
        pk = int(pk)
        comment_form = CommentForm
        delete_comment_form = DeleteCommentForm

    client = get_client(client_name)
    selections = Selection.objects.filter(client=client).filter(status='REJECTED')
    pro_selections = selections.filter(talent__hr="n").filter(talent__tts="n")
    home_selections = selections.filter(talent__hr="y")
    tts_selections = selections.filter(talent__tts="y")

    return render(request, 'rejected.html', {
        'client': client,
        'form': form,
        'comment_form': comment_form,
        'delete_comment_form': delete_comment_form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections,
        'pk': pk
    })


@login_required
def updatedb(request):
    # Populate client many to many field (dropdown multi-select)  on talent table
    # for client in Client.objects.all():
    #     for talent in Talent.objects.all():
    #         if hasattr(talent, client.username) and getattr(talent, client.username) == "y":
    #             talent.client_set.add(client)
    #             talent.save()
    #             print(talent.welo_id + client.username)

    # Populate vendor fk (dropdown single select) field on talent table
    # for vendor in Vendor.objects.all():
    #     for talent in Talent.objects.all():
    #         if talent.vendor_name == vendor.name:
    #             # talent.vendor_fk = vendor
    #             # talent.save()
    #             print(talent.welo_id + ": " + vendor.name)

    # Populate client and vendor fk (dropdown single select) and status fields on selection table
    # for client in Client.objects.filter(username='kornferry'):

    # for client in Client.objects.all():
    #     protalents_for_approval, hometalents_for_approval, ttstalents_for_approval = None, None, None
    #     pro_accepted_talents, home_accepted_talents, tts_accepted_talents = None, None, None
    #     pro_rejected_talents, home_rejected_talents, tts_rejected_talents = None, None, None
    #     try:
    #         protalents_for_approval, hometalents_for_approval, ttstalents_for_approval = get_talents_for_approval(client.username)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = protalents_for_approval[0]
    #         for talent in protalents_for_approval:
    #             try:
    #                 Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = protalents_for_approval[0]
    #         for talent in hometalents_for_approval:
    #             try:
    #                 Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = protalents_for_approval[0]
    #         for talent in ttstalents_for_approval:
    #             try:
    #                 Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #
    #     try:
    #         pro_accepted_talents, home_accepted_talents, tts_accepted_talents = get_accepted_talents(client.username)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_accepted_talents[0]
    #         for talent in pro_accepted_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="APPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_accepted_talents[0]
    #         for talent in home_accepted_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="APPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_accepted_talents[0]
    #         for talent in tts_accepted_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="APPROVED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #
    #     try:
    #         pro_rejected_talents, home_rejected_talents, tts_rejected_talents = get_rejected_talents(client.username)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_rejected_talents[0]
    #         for talent in pro_rejected_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="REJECTED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_rejected_talents[0]
    #         for talent in home_rejected_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="REJECTED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)
    #     try:
    #         querytest = pro_rejected_talents[0]
    #         for talent in tts_rejected_talents:
    #             try:
    #                 Selection.objects.create(talent=Talent.objects.get(welo_id=talent.talent), client=client, status="REJECTED")
    #             except Exception as e:
    #                 print(e)
    #     except Exception as e:
    #         print(e)

    for talent in Talent.objects.all():
        try:
            with open(os.path.join(settings.MEDIA_ROOT, talent.sample_url.split('/')[1]), 'rb') as doc_file:
                talent.audio_file.save('sample_' + talent.sample_url.split('/')[1], File(doc_file), save=True)
                talent.save()
        except Exception as e:
            print(e)

    return HttpResponse("All done!")


def get_client(client_name):
    try:
        client = Client.objects.get(username=client_name)
    except Client.DoesNotExist:
        raise Http404("That client does not exist")
    return client


def get_talent(talent_welo_id):
    try:
        talent = Talent.objects.get(welo_id=talent_welo_id)
    except Client.DoesNotExist:
        raise Http404("That talent does not exist")
    return talent


def get_talents_for_approval(client_name):

    proresults, homeresults, ttsresults = None, None, None

    proquery = "SELECT * FROM talent " \
        "WHERE pre_approved='y' AND %s='y' AND hr='n' AND tts='n' " \
        "AND NOT EXISTS (SELECT * FROM %s WHERE talent.welo_id=%s.talent) " \
        "ORDER BY language" % (client_name, client_name, client_name)
    homequery = "SELECT * FROM talent " \
        "WHERE pre_approved='y' AND %s='y' AND hr='y' AND tts='n' " \
        "AND NOT EXISTS (SELECT * FROM %s WHERE talent.welo_id=%s.talent) " \
        "ORDER BY language" % (client_name, client_name, client_name)
    ttsquery = "SELECT * FROM talent " \
        "WHERE pre_approved='y' AND %s='y' AND hr='n' AND tts='y' " \
        "AND NOT EXISTS (SELECT * FROM %s WHERE talent.welo_id=%s.talent) " \
        "ORDER BY language" % (client_name, client_name, client_name)

    try:
        proresults = Talent.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = Talent.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = Talent.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults


def get_accepted_talents(client_name):

    proresults, homeresults, ttsresults = None, None, None

    proquery = "SELECT * FROM %s " \
        "WHERE accepted='y' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='n' AND talent.tts='n') " \
        "ORDER BY language" % (client_name, client_name)
    homequery = "SELECT * FROM %s " \
        "WHERE accepted='y' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='y' AND talent.tts='n') " \
        "ORDER BY language" % (client_name, client_name)
    ttsquery = "SELECT * FROM %s " \
        "WHERE accepted='y' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='n' AND talent.tts='y') " \
        "ORDER BY language" % (client_name, client_name)
    try:
        proresults = Talent.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = Talent.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = Talent.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults


def get_rejected_talents(client_name):

    proresults, homeresults, ttsresults = None, None, None

    proquery = "SELECT * FROM %s " \
        "WHERE accepted='n' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='n' AND talent.tts='n') " \
        "ORDER BY language" % (client_name, client_name)
    homequery = "SELECT * FROM %s " \
        "WHERE accepted='n' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='y' AND talent.tts='n') " \
        "ORDER BY language" % (client_name, client_name)
    ttsquery = "SELECT * FROM %s " \
        "WHERE accepted='n' " \
        "AND EXISTS (SELECT * FROM talent WHERE %s.talent=talent.welo_id AND talent.hr='n' AND talent.tts='y') " \
        "ORDER BY language" % (client_name, client_name)
    try:
        proresults = Talent.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = Talent.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = Talent.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults
