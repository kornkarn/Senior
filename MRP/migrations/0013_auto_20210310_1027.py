# Generated by Django 3.1.7 on 2021-03-10 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MRP', '0012_inv_po_po_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='po',
            name='po_number',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
    ]
