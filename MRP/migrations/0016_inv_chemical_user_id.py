# Generated by Django 3.1.7 on 2021-03-17 07:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MRP', '0015_remove_weekloading_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='inv_chemical',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]