from django.http import Http404
from django.shortcuts import render
import models


def index(request):
    latest_question_list = models.Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'choices.html', context)


def detail(request, question_id):
    try:
        question = models.Question.objects.get(pk=question_id)
    except models.Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'detail.html', {'question': question})

