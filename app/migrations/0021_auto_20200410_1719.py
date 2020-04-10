# Generated by Django 2.2.10 on 2020-04-10 17:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_msgsendrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditchangerecord',
            name='change_type',
            field=models.SmallIntegerField(choices=[(1, '消费获取'), (2, '活动获取'), (3, '支付抵扣'), (4, '其他')], default=1, verbose_name='变更类型'),
        ),
        migrations.CreateModel(
            name='PayedRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应收金额')),
                ('total_payed', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='实收金额')),
                ('amount_payed', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='余额抵扣')),
                ('credit_payed', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='积分抵扣')),
                ('credit_change', models.BigIntegerField(default=0, verbose_name='积分变更')),
                ('cash_payed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='现金支付')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name='备注')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='income_record_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='income_record_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Customer', verbose_name='关联客户')),
                ('related_store', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.StoreInfo', verbose_name='维修门店')),
            ],
            options={
                'verbose_name': '收银记录',
                'verbose_name_plural': '收银记录',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='amountchangerecord',
            name='related_payed_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.PayedRecord', verbose_name='关联收银记录'),
        ),
        migrations.AddField(
            model_name='creditchangerecord',
            name='related_payed_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.PayedRecord', verbose_name='关联收银记录'),
        ),
    ]