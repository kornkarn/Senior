# Generated by Django 3.1.7 on 2021-03-10 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MRP', '0013_auto_20210310_1027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weekloading',
            name='date',
        ),
        migrations.AddField(
            model_name='weekloading',
            name='week',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='weekloading',
            name='year',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
