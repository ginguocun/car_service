# Generated by Django 2.2.10 on 2020-04-24 21:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_auto_20200421_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_code', models.SmallIntegerField(null=True, unique=True, verbose_name='等级编号')),
                ('level_name', models.CharField(max_length=100, null=True, unique=True, verbose_name='等级名称')),
                ('desc', models.TextField(blank=True, max_length=1000, null=True, verbose_name='等级描述')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '客户等级',
                'verbose_name_plural': '客户等级',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.CustomerLevel', verbose_name='客户等级'),
        ),
    ]
