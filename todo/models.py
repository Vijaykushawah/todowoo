from django.db import models
from django.contrib.auth.models import User
from django import forms
# Create your models here.


class Todo(models.Model):
    title=models.CharField(max_length=100)
    memo=models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.title

def clean_password1(self):
  password1 = self.cleaned_data['password1']
  if len(password1) < 4:
      raise forms.ValidationError("password is too short")
  return password

class Contact(models.Model):
    contact_name = models.CharField(max_length=100,default="name")
    contact_email = models.EmailField(blank=True)
    contact_content = models.TextField(blank=True)

class MyProfile(models.Model):
    username = models.CharField(max_length=100,default="username")
    lead= models.CharField(max_length=100,null=True,blank=True)
    associate= models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.username
class SendMultiMail(models.Model):
    sender= models.EmailField(blank=True)
    receivers = models.TextField(max_length=200,blank=True)
    subject = models.TextField(max_length=200,blank=True)
    body =  models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    schedule = models.DateTimeField(null=True)
