# Generated by Django 3.1.1 on 2020-09-24 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0008_auto_20200924_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myprofile',
            name='associate',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='myprofile',
            name='lead',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
