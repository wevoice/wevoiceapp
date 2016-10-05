from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from forms import LoginForm, SelectionForm, CommentForm, DeleteCommentForm
from django.contrib.auth.models import User
from models import Admin, Client, Talent, Vendor, Language, Selection, Comment, Rating, UserProfile
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
import sys
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
                selection.talent.total_rating = \
                    Rating.objects.filter(talent=selection.talent).aggregate(Sum('rating'))['rating__sum']
                selection.talent.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'), {
                'selection': selection,
                'client': client})
    else:
        return Http404("That page does not exist")


def get_selections(client, status):
    status_filter_dict = {
        'for_approval': 'PREAPPROVED',
        'accepted': 'APPROVED',
        'rejected': 'REJECTED'
    }
    status_filter = None
    if status in ['for_approval', 'accepted', 'rejected']:
        status_filter = status_filter_dict[status]
    all_selections = client.selection_set.filter(status=status_filter)
    selection_types = []
    for type_filter in ["PRO", "HR", "TTS"]:
        currentselections = all_selections.filter(talent__type=type_filter)
        if currentselections.exists():
            selection_types.append({
                'selections': currentselections,
                'type': type_filter
            })
    return selection_types


@login_required
def selections(request, client_name, status, pk=None):
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
    selection_types = get_selections(client, status)

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
        'selection_types': selection_types
    })


class BreakIt(Exception):
    pass


@login_required
def updatedb(request):
    from legacy.models import Talent as OldTalents
    from legacy.models import Client as OldClients
    from legacy.models import Language as OldLanguages
    from legacy.models import Admin as OldAdmin
    from legacy.models import Vendor as OldVendors

    Talent.objects.all().delete()
    Language.objects.all().delete()
    Admin.objects.all().delete()
    Vendor.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.exclude(username=u'william.burton').delete()
    Client.objects.all().delete()
    Selection.objects.all().delete()

    superclient = Client.objects.create(
        name="Welocalize",
        username="localize",
        password="Welo!"
    )

    UserProfile.objects.create(
        user=User.objects.get(username='william.burton'),
        client=superclient
    )

    for oldvendor in OldVendors.objects.all():
        Vendor.objects.create(
            name=oldvendor.name,
            username=oldvendor.username,
            password=oldvendor.password
        )

    for oldlanguage in OldLanguages.objects.all():
        Language.objects.create(
            language=oldlanguage.language
        )

    for oldadmin in OldAdmin.objects.all():
        Admin.objects.create(
            username=oldadmin.username,
            password=oldadmin.password
        )

    for oldtalent in OldTalents.objects.all():
        # The old Talent fields will be used as the new Talent fields.
        vendor, created = Vendor.objects.get_or_create(name=oldtalent.vendor_name)
        language, created = Language.objects.get_or_create(language=oldtalent.language)
        age_range = 3
        if oldtalent.age_range == "16-25":
            age_range = 2
        elif oldtalent.age_range == "26-45":
            age_range = 3
        elif oldtalent.age_range == "46-75":
            age_range = 4

        try:
            newtalent = Talent.objects.create(
                old_talent_id=oldtalent.id,
                welo_id=oldtalent.welo_id,
                vendor=vendor,
                gender=oldtalent.gender,
                age_range=age_range,
                language=language,
                audio_file=None,
                times_rated=None,
                total_rating=None,
                comment=oldtalent.comment,
                rate=oldtalent.rate,
            )
            newtalent.save()
        except Exception as e:
            print_error(e)

        try:
            if oldtalent.vendor_name:
                vendor, created = Vendor.objects.get_or_create(name=oldtalent.vendor_name)
                newtalent.vendor = vendor
                newtalent.save()
        except Exception as e:
            print_error(e)

        try:
            if oldtalent.hr == "y":
                newtalent.type = "HR"
            elif oldtalent.tts == 'y':
                newtalent.type = "TTS"
            else:
                newtalent.type = "PRO"
            newtalent.save()
        except Exception as e:
            print_error(e)

        try:
            newtalent.audio_file = oldtalent.sample_url.split('/')[1]
            newtalent.save()
        except Exception as e:
            print_error(e)
            print(oldtalent.sample_url)

    for oldclient in OldClients.objects.all():
        process_client(oldclient, OldTalents)

    return HttpResponse("All done!")


def process_client(oldclient, oldtalents):

    newclient = create_client_objects(oldclient)

    try:
        oldtalents.objects.raw("SELECT * FROM talent WHERE %s='y'" % oldclient.username)[0]
    except Exception as e:
        print_error(e)
    else:
        process_talent_types(
            status="PREAPPROVED",
            oldclient=oldclient,
            oldtalents=oldtalents,
            newclient=newclient,
            process_function=get_talents_for_approval
        )
    finally:
        try:
            oldtalents.objects.raw("SELECT * FROM %s" % oldclient.username)[0]
        except Exception as e:
            print_error(e)
            if oldclient:
                print(oldclient.username + ": " + "APPROVED")
        else:
            process_talent_types(
                status="APPROVED",
                oldclient=oldclient,
                oldtalents=oldtalents,
                newclient=newclient,
                process_function=get_accepted_talents
            )
        try:
            oldtalents.objects.raw("SELECT * FROM %s" % oldclient.username)[0]
        except Exception as e:
            print_error(e)
            if oldclient:
                print(oldclient.username + ": " + "REJECTED")
        else:
            process_talent_types(
                status="REJECTED",
                oldclient=oldclient,
                oldtalents=oldtalents,
                newclient=newclient,
                process_function=get_rejected_talents
            )


def create_client_objects(oldclient):
    try:
        if oldclient.username == "demo_client":
            print("test")
        newclient = Client.objects.create(
            name=oldclient.name,
            username=oldclient.username,
            password=oldclient.password
        )
        newuser = User.objects.get_or_create(
            first_name=oldclient.name,
            last_name="Admin",
            username=oldclient.username,
            password=oldclient.password
        )
        UserProfile.objects.get_or_create(
            user=newuser[0],
            client=newclient
        )
        return newclient
    except Exception as e:
        print(e)


def process_talent_types(status, oldclient, oldtalents, newclient, process_function):
    try:
        protalents, hometalents, ttstalents = process_function(oldclient.username, oldtalents)
    except Exception as e:
        print_error(e)
    else:
        process_type(protalents, newclient, status, talenttype="protalents")
        process_type(hometalents, newclient, status, talenttype="hometalents")
        process_type(ttstalents, newclient, status, talenttype="ttstalents")


def process_type(talent_type, newclient, status, talenttype=None):
    try:
        talent_type[0]
    except Exception as e:
        print_error(e)
        if hasattr(newclient, "username"):
            print(newclient.username + ": " + status + ": " + talenttype)
        else:
            print(str(newclient))
    else:
        for talent_old in talent_type:
            try:
                talent = None
                if hasattr(talent_old, 'welo_id'):
                    talent = Talent.objects.get(welo_id=talent_old.welo_id)
                elif hasattr(talent_old, 'talent'):
                    talent = Talent.objects.get(welo_id=talent_old.talent)
                if newclient:
                    Selection.objects.get_or_create(talent=talent, client=newclient, status=status)
                else:
                    print("No newclient found")
            except Exception as e:
                if hasattr(talent_old, 'welo_id'):
                    print_error(e)
                    print("welo_id: " + talent_old.welo_id + "client: " + newclient.username)
                elif hasattr(talent_old, 'talent'):
                    print_error(e)
                    print("talent: " + talent_old.talent + "client: " + newclient.username)


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


def print_error(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(e, exc_type, fname, exc_tb.tb_lineno)


def get_talents_for_approval(client_name, talentobject):

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
        proresults = talentobject.objects.raw(proquery)
    except Exception as e:
        print_error(e)

    try:
        homeresults = talentobject.objects.raw(homequery)
    except Exception as e:
        print_error(e)

    try:
        ttsresults = talentobject.objects.raw(ttsquery)
    except Exception as e:
        print_error(e)
    return proresults, homeresults, ttsresults


def get_accepted_talents(client_name, talentobject):

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
        proresults = talentobject.objects.raw(proquery)
    except Exception as e:
        print_error(e)

    try:
        homeresults = talentobject.objects.raw(homequery)
    except Exception as e:
        print_error(e)

    try:
        ttsresults = talentobject.objects.raw(ttsquery)
    except Exception as e:
        print_error(e)
    return proresults, homeresults, ttsresults


def get_rejected_talents(client_name, talentobject):

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
        proresults = talentobject.objects.raw(proquery)
    except Exception as e:
        print_error(e)

    try:
        homeresults = talentobject.objects.raw(homequery)
    except Exception as e:
        print_error(e)

    try:
        ttsresults = talentobject.objects.raw(ttsquery)
    except Exception as e:
        print_error(e)
    return proresults, homeresults, ttsresults
