from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm,ContactForm
from .models import Todo,Contact
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import re
# Create your views here.
def signupuser(request):
    if request.method == 'GET':
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})
    else:
        #create a new User
        if request.POST['password1'] == request.POST['password2']:
            if len(request.POST['password1'])<8:
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passowrd length is too short"})
            elif not re.findall('\d',request.POST['password1']):
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passowrd must conain atlease 1 digit 0-9"})
            elif not re.findall('[A-Z]',request.POST['password1']):
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passowrd must conain atlease 1 capital letter"})
            elif not re.findall('[a-z]',request.POST['password1']):
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passowrd must conain atlease 1 small letter"})
            elif not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]',request.POST['password1']):
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passowrd must conain atlease 1 special character"})



            else:
                try:
                    user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                    user.save()
                    login(request,user)
                    return redirect(currenttodos)
                except IntegrityError:
                    return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"User already exists"})
        else:
            #Tell the user the password didn't match
            #println("Passoword didn't match")
            return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Passwod didn't match"})
@login_required
def currenttodos(request):
    #todos=Todo.objects.all()
    #we want user specific database objects
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'todo/currenttodos.html',{'todos':todos})
@login_required
def completedtodos(request):
    #todos=Todo.objects.all()
    #we want user specific database objects
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/completedtodos.html',{'todos':todos})

@login_required
def viewtodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'GET':
        form =  TodoForm(instance=todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form=TodoForm(request.POST,instance=todo)
            form.save()
            return redirect(currenttodos)
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'error':"Bad info passed.Please try again."})

@login_required
def completetodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect(currenttodos)

@login_required
def deletetodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect(currenttodos)

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return render(request,'todo/logout.html')
    else:
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})


def loginuser(request):
    if request.method == 'GET':
        return render(request,'todo/loginuser.html',{'form':AuthenticationForm()})
    else:
        #authenticate function
        user=authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/loginuser.html',{'form':AuthenticationForm(),'error':"Username and Password do not match"})
        else:
            login(request,user)
            return redirect(currenttodos)



def home(request):
    return render(request,'todo/home.html')

def abouttodo(request):
    return render(request,'todo/abouttodo.html')
def portfoliotodo(request):
    return render(request,'todo/portfoliotodo.html')
def contacttodo(request):

    if request.method == 'GET':
        return render(request,'todo/contacttodo.html',{'form':ContactForm()})
    else:
        try:
            form=ContactForm(request.POST)
            form.save()
            todos = Contact.objects.latest('id')
            return render(request,'todo/contacttodo.html',{'form':ContactForm(),'contact':todos})
        except ValueError:
            return render(request,'todo/contacttodo.html',{'form':ContactForm(),'error':"Bad data Passed! Try again."})

    return render(request,'todo/contacttodo.html')

def contacttodos(request):
    #todos=Todo.objects.all()
    #we want user specific database objects
    todos = Contact.objects.latest('id')
    return render(request,'todo/contacttodo.html',{'form':ContactForm(),'contact':todos})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm()})
    else:
        try:
            form=TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect(currenttodos)
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':TodoForm(),'error':"Bad data Passed! Try again."})
