# Generated by Django 2.2.10 on 2020-03-23 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200323_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurancecompany',
            name='desc',
            field=models.CharField(max_length=200, null=True, verbose_name='显示名称'),
        ),
    ]
