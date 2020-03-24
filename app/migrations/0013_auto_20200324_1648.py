# Generated by Django 2.2.10 on 2020-03-24 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20200323_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='wxuser',
            name='current_amounts',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='请到[积分/余额-->余额变更]添加记录', max_digits=10, null=True, verbose_name='当前余额'),
        ),
        migrations.AlterField(
            model_name='insuranceapply',
            name='changed_times',
            field=models.CharField(blank=True, choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')], default='0', max_length=100, null=True, verbose_name='过户次数'),
        ),
        migrations.AlterField(
            model_name='insuranceapply',
            name='data_import',
            field=models.BooleanField(default=False, help_text='勾选以后数据将会自动导入到【投保记录】列表', verbose_name='已导入投保记录'),
        ),
        migrations.AlterField(
            model_name='insuranceapply',
            name='insurance_company',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='保险公司'),
        ),
        migrations.AlterField(
            model_name='insuranceapply',
            name='insurance_dsxr',
            field=models.CharField(blank=True, choices=[('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')], help_text='发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。', max_length=100, null=True, verbose_name='第三责任险'),
        ),
        migrations.AlterField(
            model_name='insuranceapply',
            name='service_type',
            field=models.IntegerField(blank=True, choices=[(1, '车辆续保'), (2, '保险分期'), (3, '车辆贷款')], help_text='1-->车辆续保, 2-->保险分期, 3-->车辆贷款', null=True, verbose_name='类别'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='insurance_dsxr',
            field=models.CharField(blank=True, choices=[('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')], help_text='发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。', max_length=100, null=True, verbose_name='第三责任险'),
        ),
        migrations.AlterField(
            model_name='serviceapply',
            name='data_import',
            field=models.BooleanField(default=False, help_text='勾选以后数据将会自动导入到【维修服务】列表', verbose_name='已导入维修服务'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='current_credits',
            field=models.BigIntegerField(blank=True, default=0, help_text='请到[积分/余额-->积分变更]添加记录', null=True, verbose_name='当前积分'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='gender',
            field=models.SmallIntegerField(blank=True, choices=[(1, '男'), (2, '女'), (0, '未知')], help_text='0-->未知, 1-->男, 2-->女', null=True, verbose_name='性别'),
        ),
        migrations.CreateModel(
            name='CreditChangeRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credits', models.BigIntegerField(null=True, verbose_name='积分变更')),
                ('current_credits', models.BigIntegerField(blank=True, null=True, verbose_name='变更后积分')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name='备注')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='credit_change_record_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='credit_change_record_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联账号')),
            ],
            options={
                'verbose_name': '积分变更记录',
                'verbose_name_plural': '积分变更记录',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='AmountChangeRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amounts', models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='金额变更')),
                ('current_amounts', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='变更后余额')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name='备注')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='amount_change_record_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='amount_change_record_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联账号')),
            ],
            options={
                'verbose_name': '余额变更记录',
                'verbose_name_plural': '余额变更记录',
                'ordering': ['-id'],
            },
        ),
    ]
