# Generated by Django 2.2.10 on 2020-04-21 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_auto_20200416_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceapply',
            name='reserve_address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='服务地点'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='served_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Superior', verbose_name='维修人员'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='reserve_address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='服务地点'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='vehicle_mileage',
            field=models.IntegerField(help_text='未知可填写为0', null=True, verbose_name='当前行驶公里数'),
        ),
    ]