from django.shortcuts import render,redirect,get_object_or_404,get_list_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm,ContactForm,MyProfileForm,SendMultiMailForm
from .models import Todo,Contact,MyProfile,SendMultiMail
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import re
import csv,logging,xlwt,googletrans

from django.http import HttpResponse,JsonResponse
from googletrans import Translator
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Create your views here.
logger = logging.getLogger(__name__)
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
def exportdatatodo(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}{}.csv"'.format(request.user.username,"_currentwork")
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=True)
    writer = csv.writer(response)
    writer.writerow(['Title', 'Memo', 'Created', 'Datecompleted','Createdby','isImportant'])
    for row in todos:
        writer.writerow([row.title,row.memo,row.created,row.datecompleted,row.user.username,row.important,])
    return response

@login_required
def exportexceldatatodo(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}{}.xls"'.format(request.user.username,"_currentwork")
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('CurrentWork')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns=['Title', 'Memo', 'isImportant']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=True).values_list('title','memo','important')
    for row in todos:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

@login_required
def exportcompledatatodo(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}{}.csv"'.format(request.user.username,"_completedWork")
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=False)
    writer = csv.writer(response)
    writer.writerow(['Title', 'Memo', 'Created', 'Datecompleted','Createdby','isImportant'])
    for row in todos:
        writer.writerow([row.title,row.memo,row.created,row.datecompleted,row.user.username,row.important,])
    return response

@login_required
def exportexcelcompledatatodo(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}{}.xls"'.format(request.user.username,"_completedWork")
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('CompletedWork')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns=['Title', 'Memo', 'isImportant']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=False).values_list('title','memo','important')
    for row in todos:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response






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
        lead=get_object_or_404(User,pk=request.POST['user'])
        try:
            try:
                get_list_or_404(MyProfile,user=request.user,username=request.user.username,lead=lead.username)
                error="Selected User is already your lead!!"
                notduplicateuser=False
            except:
                notduplicateuser=True
            try:
                #get_list_or_404(MyProfile,user=lead,username=lead.username,associate=request.user.username)
                get_list_or_404(MyProfile,user=request.user,username=request.user.username,associate=lead.username)
                error="Selected user is your associate!!"
                notduplicateuser=False
            except:
                logger.error('do nothing')
            if request.user == lead:
                error="You can't add yourself as a lead!!"
                notduplicateuser=False

            if  not (notduplicateuser):
                form=MyProfileForm(request.POST)
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
                    myprofiles =[]
                    leadprofiles=[]
                    associateprofiles=[]
                return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':error})
            form=MyProfileForm(request.POST)
            form2=MyProfileForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = user
            newtodo.username=user.username
            newtodo.lead=lead.username
            newtodo.save()

            newtodo2 = form2.save(commit=False)
            newtodo2.user = lead
            newtodo2.username=lead.username
            newtodo2.associate=request.user.username
            newtodo2.save()
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
                myprofiles =[]
                associateprofiles=[]
                leadprofiles=[]
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
            myprofiles =get_list_or_404(MyProfile,user=request.user,associate=associate.username)
            try:
                form =  MyProfileForm()
                associatedelete=[]
                #associatedelete=get_object_or_404(MyProfile,associate=associate.username,username=request.user.username,user=request.user)
                associatedelete=get_list_or_404(MyProfile,user=request.user,associate=associate.username,username=request.user.username)
                associateleaddelete=get_list_or_404(MyProfile,user=associate,lead=request.user.username,username=associate.username)
                associatedelete[0].delete()
                associateleaddelete[0].delete()
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
                    myprofiles =[]
                    leadprofiles=[]
                    associateprofiles=[]

                return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'success':"Associate deleted successfuly"})
            except:
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
                    myprofiles =[]
                    associateprofiles=[]
                    leadprofiles=[]
                return  render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':"Some error occoured during delettion !"})
        except:
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
                myprofiles =[]
                leadprofiles=[]
                associateprofiles=[]
            form =  MyProfileForm()
            return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'leadprofiles':leadprofiles,'associateprofiles':associateprofiles,'form':form,'error':"Selected user is not your associate!!"})

@login_required
def exportassociatedatatodo(request):
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
                associatedeletes=get_list_or_404(MyProfile,user=request.user,associate=associate.username,username=request.user.username)
                associatedelete=associatedeletes[0]
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}{}.csv"'.format(associatedelete.user.username,"_completedWork")
                todos = Todo.objects.filter(user=associatedelete.user)
                writer = csv.writer(response)
                writer.writerow(['Title', 'Memo', 'Created', 'Datecompleted','Createdby','isImportant'])
                for row in todos:
                    writer.writerow([row.title,row.memo,row.created,row.datecompleted,row.user.username,row.important,])
                return response
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
        except:
            myprofiles =[]
            form =  MyProfileForm()
            return render(request,'todo/myprofiletodo.html',{'myprofiles':myprofiles,'form':form,'error':"Bad info passed or no user mapped .Please try again."})








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




def sendmailtodo(request):
    if request.method == 'GET':
        form = SendMultiMailForm()
        return render(request,'todo/sendmailtodo.html',{'form':form})
    else:
        error=None
        msg = MIMEMultipart()
        if bool(request.POST['pass']!='') & bool(request.POST['from'] != ''):
            passw=request.POST['pass']
            msg['From']=request.POST['from']
        else:
            msg['From']='stickymemonoreply@gmail.com'
            passw="Sticky@#123"
        msg['Subject']=request.POST['subject']
        body=request.POST['body']
        msg.attach(MIMEText(body, 'plain'))
        tolist=list(request.POST['to'].split(','))
        for to in tolist:
            logger.error(to)
            msg['To'] = to
            message = msg.as_string()
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            try:
                s.login(msg['From'], passw)
            except smtplib.SMTPAuthenticationError:
                return render(request,'todo/sendmailtodo.html',{'error':'Email and password not accepted,Please enter correct details!'})
            try:
                s.sendmail(msg['From'], msg['To'], message)
                msgdict={'sender':msg['From'],'receivers':msg['To'],'subject':msg['Subject'],'body':body}
                form=SendMultiMailForm(data=msgdict)
                form.save()
                logger.error('till not error')
                if form.is_valid():
                    logger.error('saved in db')
                    form.save()
            except smtplib.SMTPRecipientsRefused:
                return render(request,'todo/sendmailtodo.html',{'error':'Receiver mail field is empty!'})
            logger.error("email sent")
            s.quit()
            # open the file to be sent
            # filename = "File_name_with_extension"
            # attachment = open("Path of the file", "rb")
            #
            # # instance of MIMEBase and named as p
            # p = MIMEBase('application', 'octet-stream')
            #
            # # To change the payload into encoded form
            # p.set_payload((attachment).read())
            #
            # # encode into base64
            # encoders.encode_base64(p)
            #
            # p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            #
            # # attach the instance 'p' to instance 'msg'
            # msg.attach(p)
        return render(request,'todo/sendmailtodo.html',{'success':'success','error':error})



def abouttodo(request):
    logger.error(request.method)
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

@login_required
def translatortodo(request):
    translator = Translator()
    available_langugages=googletrans.LANGUAGES
    if request.method == 'POST':
        return render(request,'todo/translatortodo.html',{'available_langugages':available_langugages})
    else:
        return render(request,'todo/translatortodo.html',{'available_langugages':available_langugages})


@csrf_protect
def translatetodo(request):
    fromlangval = request.POST['fromlangval']
    tolangval = request.POST['tolangval']
    lefttext = request.POST['lefttext']
    righttext = request.POST['righttext']
    resulttype = request.POST['resulttype']
    translator = Translator()
    #result = translator.translate(lefttext,src='en',dest=tolangval)
    langsrc = fromlangval
    langdetected = translator.detect(lefttext)
    if(langdetected.lang != fromlangval):
        langsrc=langdetected.lang
    result = translator.translate(lefttext, src=langsrc, dest=tolangval)

    if(resulttype == 'pronunciation'):
        return JsonResponse({'result':result.pronunciation,'langdetected':langdetected.lang})
    else:
        return JsonResponse({'result':result.text,'langdetected':langdetected.lang})
