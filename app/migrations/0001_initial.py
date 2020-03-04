# Generated by Django 2.2.10 on 2020-03-04 19:27

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='WxUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('openid', models.CharField(blank=True, help_text='微信OpenID', max_length=100, null=True, unique=True, verbose_name='微信OpenID')),
                ('avatar_url', models.URLField(blank=True, help_text='头像', null=True, verbose_name='头像')),
                ('nick_name', models.CharField(blank=True, help_text='昵称', max_length=100, null=True, unique=True, verbose_name='昵称')),
                ('gender', models.SmallIntegerField(blank=True, choices=[(1, '男'), (2, '女'), (0, '未知')], help_text='性别', null=True, verbose_name='性别')),
                ('language', models.CharField(blank=True, help_text='语言', max_length=100, null=True, verbose_name='语言')),
                ('city', models.CharField(blank=True, help_text='城市', max_length=200, null=True, verbose_name='城市')),
                ('province', models.CharField(blank=True, help_text='省份', max_length=200, null=True, verbose_name='省份')),
                ('country', models.CharField(blank=True, help_text='国家', max_length=200, null=True, verbose_name='国家')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='真实姓名')),
                ('date_of_birth', models.DateField(blank=True, help_text='出生日期', null=True, verbose_name='出生日期')),
                ('desc', models.TextField(blank=True, help_text='描述', max_length=2000, null=True, verbose_name='描述')),
                ('mobile', models.CharField(blank=True, help_text='手机号不可重复', max_length=100, null=True, unique=True, verbose_name='手机号')),
                ('current_credits', models.BigIntegerField(blank=True, default=0, help_text='当前积分', null=True, verbose_name='当前积分')),
                ('is_partner', models.BooleanField(default=False, help_text='是合伙人', verbose_name='是合伙人')),
                ('is_client', models.BooleanField(default=True, help_text='是客户', verbose_name='是客户')),
                ('is_manager', models.BooleanField(default=False, help_text='是管理员', verbose_name='是管理员')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BelongTo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='名称', max_length=200, null=True, unique=True, verbose_name='名称')),
            ],
            options={
                'verbose_name': '归属渠道',
                'verbose_name_plural': '归属渠道',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CarInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_number', models.CharField(blank=True, help_text='车牌', max_length=100, null=True, unique=True, verbose_name='车牌')),
                ('car_brand', models.CharField(blank=True, help_text='汽车品牌', max_length=255, null=True, verbose_name='汽车品牌')),
                ('car_model', models.CharField(blank=True, help_text='汽车型号', max_length=255, null=True, verbose_name='汽车型号')),
                ('car_price', models.IntegerField(blank=True, help_text='购买价格万', null=True, verbose_name='购买价格/万')),
                ('bought_date', models.DateField(blank=True, help_text='购买日期', null=True, verbose_name='购买日期')),
                ('desc', models.TextField(blank=True, help_text='描述', max_length=1000, null=True, verbose_name='描述')),
                ('is_confirmed', models.BooleanField(default=False, help_text='已审核', verbose_name='已审核')),
                ('is_active', models.BooleanField(default=True, help_text='有效', verbose_name='有效')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, help_text='审核人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='car_info_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, help_text='创建人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='car_info_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
            ],
            options={
                'verbose_name': '车辆信息',
                'verbose_name_plural': '车辆信息',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='InsuranceCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='保险出单公司', max_length=200, null=True, unique=True, verbose_name='保险出单公司')),
            ],
            options={
                'verbose_name': '保险出单公司',
                'verbose_name_plural': '保险出单公司',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='UserLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_code', models.SmallIntegerField(blank=True, help_text='等级编号', null=True, unique=True, verbose_name='等级编号')),
                ('level_name', models.CharField(help_text='等级名称', max_length=100, null=True, unique=True, verbose_name='等级名称')),
                ('desc', models.TextField(blank=True, help_text='等级描述', max_length=1000, null=True, verbose_name='等级描述')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '用户等级',
                'verbose_name_plural': '用户等级',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Superior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='名字不可重复', max_length=100, null=True, unique=True, verbose_name='名字')),
                ('mobile', models.CharField(blank=True, help_text='手机号不可重复', max_length=100, null=True, unique=True, verbose_name='手机号')),
                ('desc', models.TextField(blank=True, help_text='描述', max_length=1000, null=True, verbose_name='描述')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, help_text='审核人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='superior_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, help_text='创建人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='superior_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('user', models.ForeignKey(help_text='关联账号', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='关联账号')),
            ],
            options={
                'verbose_name': '管理人员',
                'verbose_name_plural': '管理人员',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='InsuranceRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateField(help_text='签单日期', null=True, verbose_name='签单日期')),
                ('insurance_date', models.DateField(blank=True, help_text='保单开始日期', null=True, verbose_name='保单开始日期')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, help_text='总价', max_digits=10, null=True, verbose_name='总价')),
                ('tax', models.DecimalField(blank=True, decimal_places=2, help_text='车船税', max_digits=10, null=True, verbose_name='车船税')),
                ('has_payback', models.BooleanField(default=False, verbose_name='是否已返费')),
                ('payback_percent', models.PositiveSmallIntegerField(blank=True, help_text='已返费率', null=True, verbose_name='已返费率')),
                ('payback_amount', models.DecimalField(blank=True, decimal_places=2, help_text='已返金额', max_digits=10, null=True, verbose_name='已返金额')),
                ('is_payed', models.BooleanField(default=True, help_text='已支付', verbose_name='已支付')),
                ('notes', models.TextField(blank=True, help_text='备注', max_length=1000, null=True, verbose_name='备注')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('belong_to', models.ForeignKey(blank=True, help_text='归属渠道', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.BelongTo', verbose_name='归属渠道')),
                ('car', models.ForeignKey(blank=True, help_text='车辆信息', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.CarInfo', verbose_name='车辆信息')),
                ('confirmed_by', models.ForeignKey(blank=True, help_text='审核人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='insurance_record_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, help_text='创建人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='insurance_record_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('insurance_company', models.ForeignKey(blank=True, help_text='保险公司', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.InsuranceCompany', verbose_name='保险公司')),
                ('receiver', models.ForeignKey(blank=True, help_text='验车人', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Superior', verbose_name='验车人')),
            ],
            options={
                'verbose_name': '投保记录',
                'verbose_name_plural': '投保记录',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='名字', max_length=255, null=True, verbose_name='名字')),
                ('mobile', models.CharField(help_text='手机', max_length=255, null=True, verbose_name='手机')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('datetime_updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmed_by', models.ForeignKey(blank=True, help_text='审核人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='审核人员')),
                ('created_by', models.ForeignKey(blank=True, help_text='创建人员', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_created_by', to=settings.AUTH_USER_MODEL, verbose_name='创建人员')),
                ('related_superior', models.ForeignKey(blank=True, help_text='客户归属', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Superior', verbose_name='客户归属')),
                ('related_user', models.ForeignKey(blank=True, help_text='关联用户', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_related_user', to=settings.AUTH_USER_MODEL, verbose_name='关联用户')),
            ],
            options={
                'verbose_name': '客户列表',
                'verbose_name_plural': '客户列表',
                'ordering': ['-id'],
                'unique_together': {('name', 'mobile')},
            },
        ),
        migrations.AddField(
            model_name='carinfo',
            name='customer',
            field=models.ForeignKey(help_text='客户', null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Customer', verbose_name='客户'),
        ),
        migrations.AddField(
            model_name='wxuser',
            name='user_level',
            field=models.ForeignKey(blank=True, help_text='用户等级', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.UserLevel', verbose_name='用户等级'),
        ),
        migrations.AddField(
            model_name='wxuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
