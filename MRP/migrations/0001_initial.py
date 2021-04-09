# Generated by Django 3.1.7 on 2021-02-26 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chemical',
            fields=[
                ('part_num', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('chem_name', models.CharField(max_length=200)),
                ('leadtime', models.IntegerField()),
                ('std_packing', models.FloatField()),
                ('onhand', models.IntegerField()),
                ('chem_price', models.FloatField()),
                ('chem_class', models.IntegerField()),
            ],
        ),
    ]