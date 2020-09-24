from django.shortcuts import render,redirect,get_object_or_404,get_list_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm,ContactForm,MyProfileForm
from .models import Todo,Contact,MyProfile
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
def getassociatestatustodo(request,associateusername):
    try:
        get_list_or_404(MyProfile,user=request.user,associate=associateusername,username=request.user.username)
    except:
        currentwork=[]
        completedwork=[]
        return render(request,'todo/getassociatestatustodo.html',{'currentwork':currentwork,'completedwork':completedwork,'error':"Sorry, selected user is not your associate!!"})
    associate=get_object_or_404(User,username=associateusername)
    currentwork=Todo.objects.filter(user=associate,datecompleted__isnull=True)
    completedwork=Todo.objects.filter(user=associate,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/getassociatestatustodo.html',{'currentwork':currentwork,'completedwork':completedwork})


@login_required
def myprofiletodo(request):
    user = request.user
    if request.method == 'GET':
        try:
            myprofiles=get_list_or_404(MyProfile,user=request.user)
            try:
                leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
            except:
                leadprofiles=[]
            try:
                associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
            except:
                associateprofiles=[]
        except:
            leadprofiles=[]
            associateprofiles=[]
            myprofiles=[]
        form =  MyProfileForm()
        return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form})
    else:
        try:
            lead=get_object_or_404(User,pk=request.POST['user']).username
            try:
                get_list_or_404(MyProfile,lead=lead,user=request.user,username=request.user.username)

                notduplicateuser=True
            except:
                notduplicateuser=False
            if   notduplicateuser:
                form=MyProfileForm(request.POST)

                try:
                    myprofiles =myprofiles=get_list_or_404(MyProfile,user=request.user)
                    try:
                        leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
                    except:
                        leadprofiles=[]
                    try:
                        associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
                    except:
                        associateprofiles=[]
                except:
                    myprofiles =[]
                return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':"Selected User is already your lead!!"})
            form=MyProfileForm(request.POST)
            form2=MyProfileForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = user
            newtodo.username=user.username
            newtodo.lead=lead
            newtodo.save()

            newtodo2 = form2.save(commit=False)
            newtodo2.user = get_object_or_404(User,pk=request.POST['user'])
            newtodo2.username=lead
            newtodo2.associate=user.username
            newtodo2.save()
            try:
                myprofiles =myprofiles=get_list_or_404(MyProfile,user=request.user)
                try:
                    leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
                except:
                    leadprofiles=[]
                try:
                    associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
                except:
                    associateprofiles=[]
            except:
                myprofiles =[]
            return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'success':"User added successfuly"})
        except ValueError:
            return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':"Bad info passed.Please try again."})


@login_required
def removeassociatetodo(request):
    user = request.user
    if request.method == 'GET':
        try:
            myprofiles=get_list_or_404(MyProfile,user=request.user)
            try:
                leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
            except:
                leadprofiles=[]
            try:
                associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
            except:
                associateprofiles=[]
        except:
            leadprofiles=[]
            associateprofiles=[]
            myprofiles=[]
        form =  MyProfileForm()
        return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form})
    else:
        try:
            associate=get_object_or_404(User,pk=request.POST['user'])
            myprofiles =get_list_or_404(MyProfile,user=request.user)
            try:
                form =  MyProfileForm()
                associatedelete=[]
                associatedelete=get_object_or_404(MyProfile,associate__isnull=False,associate=associate.username,username=request.user.username,user=request.user)
                associatedelete.delete()
                try:
                    myprofiles =myprofiles=get_list_or_404(MyProfile,user=request.user)
                    try:
                        leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
                    except:
                        leadprofiles=[]
                    try:
                        associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
                    except:
                        associateprofiles=[]
                except:
                    myprofiles =[]

                return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'success':"Associate deleted successfuly"})
            except:
                try:
                    myprofiles =myprofiles=get_list_or_404(MyProfile,user=request.user)
                    try:
                        leadprofiles=get_list_or_404(MyProfile,lead__isnull=False,user=request.user)
                    except:
                        leadprofiles=[]
                    try:
                        associateprofiles=get_list_or_404(MyProfile,associate__isnull=False,user=request.user)
                    except:
                        associateprofiles=[]
                except:
                    myprofiles =[]
                return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':"Selected user is not your associate !"})
        except ValueError:
            return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'form':form,'error':"Bad info passed.Please try again."})





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
