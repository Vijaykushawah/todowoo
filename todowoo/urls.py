"""todowoo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from todo import views
from django.views.generic import TemplateView

urlpatterns = [

    path('accounts/', include('allauth.urls')),
    #path('',TemplateView.as_view(template_name='todo/loginuser.html')),

    path('admin/', admin.site.urls),
    #Auth
    path('signup/',views.signupuser,name='signupuser'),
    #Signup
    #Logout
    path('logout/',views.logoutuser,name='logoutuser'),
    path('login/',views.loginuser,name='loginuser'),
    #Todo
    path('',views.home,name='home'),
    path('create/',views.createtodo,name='createtodo'),
    path('current/',views.currenttodos,name='currenttodos'),
    path('completed/',views.completedtodos,name='completedtodos'),
    path('todo/<int:todo_pk>',views.viewtodo,name='viewtodo'),
    path('todo/<int:todo_pk>/complete',views.completetodo,name='completetodo'),
    path('todo/<int:todo_pk>/delete',views.deletetodo,name='deletetodo'),
    path('about/',views.abouttodo,name='abouttodo'),
    path('portfolio/',views.portfoliotodo,name='portfoliotodo'),
    path('contact/',views.contacttodo,name='contacttodo'),
    path('myprofile/',views.myprofiletodo,name='myprofiletodo'),
    path('removeassociate/',views.removeassociatetodo,name='removeassociatetodo'),
    path('getassociatestatus/<str:associateusername>',views.getassociatestatustodo,name='getassociatestatustodo'),
    path('exportdata/',views.exportdatatodo,name='exportdatatodo'),
    path('exportexceldata/',views.exportexceldatatodo,name='exportexceldatatodo'),
    path('exportcompledata/',views.exportcompledatatodo,name='exportcompledatatodo'),
    path('exportexcelcompledata/',views.exportexcelcompledatatodo,name='exportexcelcompledatatodo'),
    path('exportassociatedata/',views.exportassociatedatatodo,name='exportassociatedatatodo'),
    path('translator/',views.translatortodo,name='translatortodo'),
    path('translate/',views.translatetodo,name='translatetodo'),
    path('sendmail/',views.sendmailtodo,name='sendmailtodo'),

]
