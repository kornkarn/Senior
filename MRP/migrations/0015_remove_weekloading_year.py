# Generated by Django 3.1.7 on 2021-03-10 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MRP', '0014_auto_20210310_1429'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weekloading',
            name='year',
        ),
    ]
