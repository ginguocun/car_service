# Generated by Django 2.2.10 on 2020-04-15 14:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20200414_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='payedrecord',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='已确认'),
        ),
        migrations.AddField(
            model_name='payedrecord',
            name='payed_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='支付日期'),
        ),
        migrations.AddField(
            model_name='payedrecord',
            name='related_insurance_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.InsuranceRecord', verbose_name='关联保险'),
        ),
        migrations.AddField(
            model_name='payedrecord',
            name='related_service_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.ServiceRecord', verbose_name='关联服务'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='related_store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.StoreInfo', verbose_name='关联门店'),
        ),
    ]
