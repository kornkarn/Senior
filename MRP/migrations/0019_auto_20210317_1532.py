# Generated by Django 3.1.7 on 2021-03-17 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MRP', '0018_auto_20210317_1037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inv_chemical',
            name='date',
        ),
        migrations.AddField(
            model_name='inv_chemical',
            name='month',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='inv_chemical',
            name='year',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
