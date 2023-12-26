from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import CreateTaskForm
from .models import Task
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    title = "Home"
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'Username already exists.'
                })
        else:
            return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'Password does not match'
                })

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })
   
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'Username and password did not match'
            })
        else:
            login(request, user)
            return redirect('tasks')

@login_required      
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html',{'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': CreateTaskForm()
        })
    if request.method == 'POST':
        try:
            form = CreateTaskForm(request.POST)
            newTask = form.save(commit=False)
            newTask.user = request.user
            newTask.save()
            return redirect('tasks')
        except:
            return render(request, 'create_task.html', {
                'form': CreateTaskForm(),
                'error': 'Please provide all the fields'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = CreateTaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, pk=task_id)
            form = CreateTaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Bad data passed in. Try again.'})
        
@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
       try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            task.datecompleted = timezone.now()
            task.save()
            return redirect('tasks')
       except ValueError:
            pass
    
    if request.method == 'GET':
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    if request.method == 'POST':
       try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            task.delete()
            return redirect('tasks')
       except ValueError:
            pass
    
    if request.method == 'GET':
        return redirect('tasks')

@login_required
def completed_tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'completed_tasks.html',{'tasks': tasks})      