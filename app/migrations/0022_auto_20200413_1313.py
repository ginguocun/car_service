# Generated by Django 2.2.10 on 2020-04-13 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20200410_1719'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partnerapply',
            options={'ordering': ['-id'], 'verbose_name': '城市合伙人申请', 'verbose_name_plural': '城市合伙人申请'},
        ),
        migrations.RemoveField(
            model_name='servicerecord',
            name='served_by',
        ),
        migrations.AddField(
            model_name='customer',
            name='is_partner',
            field=models.BooleanField(default=False, verbose_name='是合伙人'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='related_partner',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_partner': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Customer', verbose_name='城市合伙人'),
        ),
        migrations.AddField(
            model_name='partnerapply',
            name='is_confirmed',
            field=models.BooleanField(default=False, help_text='勾选此项，城市合伙人信息将自动与客户信息关联', verbose_name='申请成功'),
        ),
        migrations.AddField(
            model_name='partnerapply',
            name='related_customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Customer', verbose_name='关联客户'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='item_count',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='数量'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='item_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='单价（元）'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='served_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Superior', verbose_name='维修人员'),
        ),
        migrations.AddField(
            model_name='servicerecord',
            name='related_partner',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_partner': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Customer', verbose_name='城市合伙人'),
        ),
        migrations.AlterField(
            model_name='amountchangerecord',
            name='amounts',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='金额变更（元）'),
        ),
        migrations.AlterField(
            model_name='amountchangerecord',
            name='current_amounts',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='变更后余额（元）'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='current_amounts',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='请到[积分/余额-->余额变更]添加记录', max_digits=10, null=True, verbose_name='当前余额（元）'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='ic_payback_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='返费金额（元）'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='payback_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='已返金额（元）'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='车船税（元）'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='含税总保费（元）'),
        ),
        migrations.AlterField(
            model_name='oilpackage',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='价格（元）'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='amount_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='余额抵扣（元）'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='cash_payed',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='现金支付（元）'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='credit_change',
            field=models.BigIntegerField(default=0, help_text='现金支付，每满20元获得1积分', verbose_name='积分获得'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='credit_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='积分抵扣（元）'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='total_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='实收金额（元）'),
        ),
        migrations.AlterField(
            model_name='payedrecord',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应收金额（元）'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='成本（元）'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='小计（元）'),
        ),
        migrations.AlterField(
            model_name='servicepackage',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='价格（元）'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='is_served',
            field=models.BooleanField(default=False, help_text='若服务已经完成，请勾选此项', verbose_name='服务已完成'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='总成本（元）'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='total_payed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='实收金额（元）'),
        ),
        migrations.AlterField(
            model_name='servicerecord',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='应收金额（元）'),
        ),
    ]
