from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from forms import LoginForm, SelectionForm, CommentForm, DeleteCommentForm
from django.contrib.auth.models import User
from models import Admin, Client, Talent, Vendor, Language, Selection, Comment, Main, Rating, UserProfile
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


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
                selection.talent.total_rating = \
                    Rating.objects.filter(talent=selection.talent).aggregate(Sum('rating'))['rating__sum']
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
    pro_selections = selections.filter(talent__type="PRO")
    home_selections = selections.filter(talent__type="HR")
    tts_selections = selections.filter(talent__type="TTS")

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
    pro_selections = selections.filter(talent__type="PRO")
    home_selections = selections.filter(talent__type="HR")
    tts_selections = selections.filter(talent__type="TTS")

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
    pro_selections = selections.filter(talent__type="PRO")
    home_selections = selections.filter(talent__type="HR")
    tts_selections = selections.filter(talent__type="TTS")

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
    from legacy.models import Talent as OldTalents
    from legacy.models import Client as OldClients
    from legacy.models import Language as OldLanguages
    from legacy.models import Admin as OldAdmin
    from legacy.models import Main as OldMain
    from legacy.models import Vendor as OldVendors
    from django.conf import settings
    from django.core.files import File
    import os

    Talent.objects.all().delete()
    Client.objects.all().delete()
    Language.objects.all().delete()
    Admin.objects.all().delete()
    Main.objects.all().delete()
    Vendor.objects.all().delete()
    Selection.objects.all().delete()
    UserProfile.objects.all().delete()

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

    for oldmain in OldMain.objects.all():
        Main.objects.create(
            talent=oldmain.talent,
            client=oldmain.client,
            gender=oldmain.gender,
            age_range=oldmain.age_range,
            language=oldmain.language,
            sample_url=oldmain.sample_url,
            accepted=oldmain.accepted,
            comment=oldmain.comment
        )

    for oldlanguage in OldLanguages.objects.all():
        Language.objects.create(
            language=oldlanguage.language
        )

    for oldadmin in OldAdmin.objects.all():
        Admin.objects.create(
            username=oldadmin.username,
            password =oldadmin.password
        )

    for oldtalent in OldTalents.objects.all():
        # The old Talent fields will be used as the new Talent fields.
        vendor, created = Vendor.objects.get_or_create(name=oldtalent.vendor_name)

        try:
            newtalent = Talent.objects.create(
                old_talent_id=oldtalent.id,
                welo_id=oldtalent.welo_id,
                vendor=vendor,
                gender=oldtalent.gender,
                age_range=oldtalent.age_range,
                language=oldtalent.language,
                sample_url=oldtalent.sample_url,
                audio_file=None,
                times_rated=None,
                total_rating=None,
                comment=oldtalent.comment,
                rate=oldtalent.rate,
            )
            newtalent.save()
        except Exception as e:
            print(e)

        try:
            if oldtalent.vendor_name:
                vendor, created = Vendor.objects.get_or_create(name=oldtalent.vendor_name)
                newtalent.vendor = vendor
                newtalent.save()
        except Exception as e:
            print(e)

        try:
            if oldtalent.hr == "y":
                newtalent.type = "HR"
            elif oldtalent.tts == 'y':
                newtalent.type = "TTS"
            else:
                newtalent.type = "PRO"
            newtalent.save()
        except Exception as e:
            print(e)

        try:
            with open(os.path.join(settings.MEDIA_ROOT, oldtalent.sample_url.split('/')[1]), 'rb') as doc_file:
                newtalent.audio_file.save('sample_' + newtalent.sample_url.split('/')[1], File(doc_file), save=True)
                newtalent.save()
        except Exception as e:
            print(e)

    for oldclient in OldClients.objects.all():
        try:
            if oldclient.username == "demo_client":
                test = "test"
            newclient = Client.objects.create(
                name=oldclient.name,
                username=oldclient.username,
                password=oldclient.password
            )
            newuser, created = User.objects.get_or_create(
                first_name=oldclient.name,
                last_name="Admin",
                username=oldclient.username,
                password=oldclient.password
            )
            UserProfile.objects.create(
                user=newuser,
                client=newclient
            )
        except Exception as e:
            print(e)



        protalents_for_approval, hometalents_for_approval, ttstalents_for_approval = None, None, None
        pro_accepted_talents, home_accepted_talents, tts_accepted_talents = None, None, None
        pro_rejected_talents, home_rejected_talents, tts_rejected_talents = None, None, None

        try:
            protalents_for_approval, hometalents_for_approval, ttstalents_for_approval = \
                get_talents_for_approval(oldclient.username, OldTalents)
        except Exception as e:
            print(e)
        try:
            querytest = protalents_for_approval[0]
            for oldtalent in protalents_for_approval:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="PREAPPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = protalents_for_approval[0]
            for oldtalent in hometalents_for_approval:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="PREAPPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = protalents_for_approval[0]
            for oldtalent in ttstalents_for_approval:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="PREAPPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)

        try:
            pro_accepted_talents, home_accepted_talents, tts_accepted_talents = get_accepted_talents(
                oldclient.username, OldTalents)
        except Exception as e:
            print(e)
        try:
            querytest = pro_accepted_talents[0]
            for oldtalent in pro_accepted_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="APPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = pro_accepted_talents[0]
            for oldtalent in home_accepted_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="APPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = pro_accepted_talents[0]
            for oldtalent in tts_accepted_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="APPROVED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)

        try:
            pro_rejected_talents, home_rejected_talents, tts_rejected_talents = get_rejected_talents(
                newclient.username, OldTalents)
        except Exception as e:
            print(e)
        try:
            querytest = pro_rejected_talents[0]
            for oldtalent in pro_rejected_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="REJECTED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = pro_rejected_talents[0]
            for oldtalent in home_rejected_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="REJECTED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
        except Exception as e:
            print(e)
        try:
            querytest = pro_rejected_talents[0]
            for oldtalent in tts_rejected_talents:
                try:
                    talent = None
                    if hasattr(oldtalent, 'welo_id'):
                        talent = Talent.objects.get(welo_id=oldtalent.welo_id)
                    elif hasattr(oldtalent, 'talent'):
                        talent = Talent.objects.get(welo_id=oldtalent.talent)
                    Selection.objects.get_or_create(talent=talent, client=newclient, status="REJECTED")
                except Exception as e:
                    print(e)
                    if hasattr(oldtalent, 'welo_id'):
                        print("welo_id: " + oldtalent.welo_id + "client: " + newclient.name)
                    elif hasattr(oldtalent, 'talent'):
                        print("talent: " + oldtalent.talent + "client: " + newclient.name)
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
    except Talent.DoesNotExist:
        raise Http404("That talent does not exist")
    return talent


def get_talents_for_approval(client_name, TalentObject):

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
        proresults = TalentObject.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = TalentObject.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = TalentObject.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults


def get_accepted_talents(client_name, TalentObject):

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
        proresults = TalentObject.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = TalentObject.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = TalentObject.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults


def get_rejected_talents(client_name, TalentObject):

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
        proresults = TalentObject.objects.raw(proquery)
    except Exception as e:
        print(e)

    try:
        homeresults = TalentObject.objects.raw(homequery)
    except Exception as e:
        print(e)

    try:
        ttsresults = TalentObject.objects.raw(ttsquery)
    except Exception as e:
        print(e)
    return proresults, homeresults, ttsresults
