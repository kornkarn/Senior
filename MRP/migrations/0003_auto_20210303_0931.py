# Generated by Django 3.1.7 on 2021-03-03 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MRP', '0002_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemical',
            name='uom',
            field=models.CharField(choices=[('litre', 'litre'), ('grams', 'grams'), ('unit', 'unit')], default='litre', max_length=100),
        ),
        migrations.AddField(
            model_name='chemical',
            name='vendor_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='MRP.vendor'),
        ),
    ]