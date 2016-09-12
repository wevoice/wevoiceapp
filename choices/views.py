from django.db import connection
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from forms import LoginForm, SelectionForm
from models import Client, Talent, Vendor, Selection
from django.core.urlresolvers import reverse


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                client = Client.objects.get(username=form.data['username'])
            except Client.DoesNotExist:
                return render(request, 'index.html', {'form': form})
            request.session['registered'] = client.username
            return HttpResponseRedirect(reverse('index', args=(client.username,)))

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def index(request, client_name):
    client = get_client(client_name)
    return render(request, 'index.html', {'client': client})


def for_approval(request, client_name):
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

    return render(request, 'for_approval.html', {
        'client': client,
        'form': form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections
    })


def accepted(request, client_name):
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

    return render(request, 'accepted.html', {
        'client': client,
        'form': form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections
    })


def rejected(request, client_name):
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

    client = get_client(client_name)
    selections = Selection.objects.filter(client=client).filter(status='REJECTED')
    pro_selections = selections.filter(talent__hr="n").filter(talent__tts="n")
    home_selections = selections.filter(talent__hr="y")
    tts_selections = selections.filter(talent__tts="y")

    return render(request, 'rejected.html', {
        'client': client,
        'form': form,
        'pro_selections': pro_selections,
        'home_selections': home_selections,
        'tts_selections': tts_selections
    })


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
    for client in Client.objects.all():
        try:
            protalents_for_approval, hometalents_for_approval, ttstalents_for_approval = get_talents_for_approval(
                client.username)
            for talent in protalents_for_approval:
                Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
            for talent in hometalents_for_approval:
                Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
            for talent in ttstalents_for_approval:
                Selection.objects.create(talent=talent, client=client, status="PREAPPROVED")
        except:
            print(client)


        # try:
        #     pro_accepted_talents, home_accepted_talents, tts_accepted_talents = get_accepted_talents(client.username)
        #     for talent in pro_accepted_talents:
        #         Selection.objects.create(talent=talent, client=client, status="APPROVED")
        #     for talent in home_accepted_talents:
        #         Selection.objects.create(talent=talent, client=client, status="APPROVED")
        #     for talent in tts_accepted_talents:
        #         Selection.objects.create(talent=talent, client=client, status="APPROVED")
        # except:
        #     print('Hit an error')


        # try:
        #     pro_rejected_talents, home_rejected_talents, tts_rejected_talents = get_rejected_talents(client.username)
        #     for talent in pro_rejected_talents:
        #         Selection.objects.create(talent=talent, client=client, status="REJECTED")
        #     for talent in home_rejected_talents:
        #         Selection.objects.create(talent=talent, client=client, status="REJECTED")
        #     for talent in tts_rejected_talents:
        #         Selection.objects.create(talent=talent, client=client, status="REJECTED")
        # except:
        #     print(client)



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
    return Talent.objects.raw(proquery), Talent.objects.raw(homequery), Talent.objects.raw(ttsquery)


def get_accepted_talents(client_name):
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
    return Talent.objects.raw(proquery), Talent.objects.raw(homequery), Talent.objects.raw(ttsquery)


def get_rejected_talents(client_name):
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
    return Talent.objects.raw(proquery), Talent.objects.raw(homequery), Talent.objects.raw(ttsquery)
