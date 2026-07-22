from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task


def get_current_language(request):
    language = request.session.get('django_language', 'en')
    if language not in ('en', 'ja'):
        language = 'en'
    return language


# Create your views here.
def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'], due_at=make_aware(parse_datetime(request.POST['due_at'])),priority=request.POST['priority'])
        task.save()
        completed = task.completed
    
    tasks = Task.objects.all()

    if request.GET.get('refine') == 'completed':
        tasks = tasks.filter(completed=True)
    elif request.GET.get('refine') == 'not_completed':
        tasks = tasks.filter(completed=False)

    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    current_language = get_current_language(request)
    context = {
        'tasks': tasks,
        'current_language': current_language,
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not exist')

    current_language = get_current_language(request)
    context = {
        'task': task,
        'current_language': current_language,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.priority = request.POST['priority']
        task.save()
        return redirect(detail, task_id)
    
    current_language = get_current_language(request)
    context = {
        'task': task,
        'current_language': current_language,
    }
    return render(request, "todo/edit.html", context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)


def switch_language(request, language_code):
    if language_code not in ('en', 'ja'):
        raise Http404('Language is not supported')

    request.session['django_language'] = language_code
    request.session.save()

    next_url = request.GET.get('next') or '/'
    if not next_url.startswith('/'):
        next_url = '/'
    return redirect(next_url)
