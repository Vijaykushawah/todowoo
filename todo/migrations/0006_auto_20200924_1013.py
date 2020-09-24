# Generated by Django 3.1.1 on 2020-09-24 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_myprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myprofile',
            name='child_id',
        ),
        migrations.RemoveField(
            model_name='myprofile',
            name='parent_id',
        ),
        migrations.AddField(
            model_name='myprofile',
            name='associate',
            field=models.CharField(default='Associate', max_length=100),
        ),
        migrations.AddField(
            model_name='myprofile',
            name='lead',
            field=models.CharField(default='Lead', max_length=100),
        ),
        migrations.AlterField(
            model_name='myprofile',
            name='username',
            field=models.CharField(default='username', max_length=100),
        ),
    ]
