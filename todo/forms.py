from django.forms import ModelForm
from .models import Todo,Contact


class TodoForm(ModelForm):
    class Meta:
        model=Todo
        fields=['title','memo','important']

class ContactForm(ModelForm):
    class Meta:
        model=Contact
        fields = '__all__'
