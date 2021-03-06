# Generated by Django 2.2.10 on 2020-03-23 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_servicepackagetype_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceapply',
            name='service_info',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='服务详情'),
        ),
        migrations.AddField(
            model_name='servicerecord',
            name='service_info',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='服务详情'),
        ),
        migrations.AlterField(
            model_name='serviceapply',
            name='data_import',
            field=models.BooleanField(default=False, help_text='勾选以后数据将会自动导入到【维修服务】列表', verbose_name='已导入服务记录'),
        ),
    ]
