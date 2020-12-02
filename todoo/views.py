from django.shortcuts import render,get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
from .forms import Todoform
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method=='GET':
        return render(request,'signup.html',{'form':UserCreationForm})
    else:
            if request.POST['password1'] == request.POST['password2']:
                try:
                    user=User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                    user.save()
                    login(request,user)
                    return redirect('currenttodos')
                except IntegrityError:
                    return render(request, 'signup.html', {'form': UserCreationForm,'error':'Username already exists'})
            else:
                return render(request, 'signup.html', {'form': UserCreationForm,'error':'Passwords are not matching'})
@login_required()
def logoutuser(request):
    if request.method=='POST':
        logout(request)
        return redirect('home')
def loginuser(request):
    if request.method=='GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm(),'error':'username and password does not match'})
        else:
            login(request,user)
            return redirect('currenttodos')

@login_required()
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'createtodo.html', {'form': Todoform()})
    else:
        form = Todoform(request.POST)
        newtodo = form.save(commit=False)
        newtodo.user = request.user
        newtodo.save()
        return redirect('currenttodos')

@login_required()
def currenttodos(request):
    todos = Todo.objects.filter(user = request.user,datecompleted__isnull=True)
    return render(request,'currenttodos.html',{'todos':todos})

@login_required()
def completedtodos(request):
    todos = Todo.objects.filter(user = request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'completedtodos.html',{'todos':todos})

@login_required()
def viewtodo(request,todo_id):
    todo = get_object_or_404(Todo,pk=todo_id,user = request.user)
    if request.method == 'GET':
        form = Todoform(instance=todo)
        return render(request,'viewtodo.html',{'todo':todo,'form':form,})
    else:
        form = Todoform(request.POST,instance=todo)
        form.save()
        return redirect('currenttodos')

@login_required()
def completetodo(request,todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == 'POST':
        todo.datecompleted= timezone.now()
        todo.save()
        return redirect('currenttodos')
@login_required()
def deletetodo(request,todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')