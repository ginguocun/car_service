# Generated by Django 2.2.10 on 2020-03-07 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicepackage',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='是否有效'),
        ),
        migrations.AddField(
            model_name='servicepackagetype',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='是否有效'),
        ),
    ]
