# Generated by Django 2.2.10 on 2020-03-12 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200307_2247'),
    ]

    operations = [
        migrations.CreateModel(
            name='OilPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True, unique=True, verbose_name='名称')),
                ('desc', models.CharField(blank=True, max_length=200, null=True, verbose_name='介绍')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='价格')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '机油套餐',
                'verbose_name_plural': '机油套餐',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='changed_times',
            field=models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')], default='0', max_length=100, null=True, verbose_name='过户次数'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_ck',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，造成本车乘客（非驾驶员）的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。', max_length=100, null=True, verbose_name='车上人员责任险-乘客'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_company',
            field=models.ForeignKey(blank=True, limit_choices_to={'display': True, 'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='insurance_apply_check_by', to='app.InsuranceCompany', verbose_name='由谁联系'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_cshx',
            field=models.BooleanField(default=False, help_text='无明显碰撞痕迹的车身划痕损失，保险公司将按照条款规定赔偿。例如车辆停放期间，被人用尖锐物划伤。', verbose_name='车身划痕损失险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_csx',
            field=models.BooleanField(default=True, help_text='发生保险事故时，补偿您自己车辆的损失。例如车辆发生碰撞、倾覆、火灾、爆炸，或被外界物体倒塌、坠物砸坏，以及与别人车辆发生碰撞，造成自己的车辆受损等，保险公司将按照条款赔偿您的车辆维修费用', verbose_name='机动车辆损失险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_dqx',
            field=models.BooleanField(default=False, help_text='如果车辆被盗窃、抢劫、抢夺，经公安机关立案证明，保险公司将按条款规定赔偿。', verbose_name='盗抢险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_dsxr',
            field=models.CharField(choices=[('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')], help_text='发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。', max_length=100, null=True, verbose_name='第三责任险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_fdjss',
            field=models.BooleanField(default=False, help_text='车辆在使用过程中，因发动机进水后导致的发动机的直接损毁，保险公司将按条款规定赔偿。', verbose_name='发动机涉水损失险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_hw',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，致使保险车辆所载货物遭受直接损毁，依法应由被保险人承担的经济赔偿责任，保险人负责赔偿。', max_length=100, null=True, verbose_name='车上货物责任险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_pl',
            field=models.BooleanField(default=False, help_text='如果发生挡风玻璃或车窗玻璃单独破碎，保险公司按实际损失进行赔偿。例如被高空坠物或飞石击碎挡风玻璃或车窗玻璃。', verbose_name='玻璃单独破碎险'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_sj',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，造成本车驾驶员本人的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。', max_length=100, null=True, verbose_name='车上人员责任险-司机'),
        ),
        migrations.AddField(
            model_name='insuranceapply',
            name='insurance_zrss',
            field=models.BooleanField(default=False, help_text='因本车电器、线路、油路、供油系统、供气系统、车载货物等自身发生问题，或者车辆运转摩擦引起火灾，造成本车的损失，以及为减少本车损失所支出的必要合理的施救费用，保险公司将按条款规定赔偿。', verbose_name='自燃损失险'),
        ),
        migrations.AddField(
            model_name='insurancecompany',
            name='display',
            field=models.BooleanField(default=True, verbose_name='用户是否可选'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_ck',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，造成本车乘客（非驾驶员）的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。', max_length=100, null=True, verbose_name='车上人员责任险-乘客'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_cshx',
            field=models.BooleanField(default=False, help_text='无明显碰撞痕迹的车身划痕损失，保险公司将按照条款规定赔偿。例如车辆停放期间，被人用尖锐物划伤。', verbose_name='车身划痕损失险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_csx',
            field=models.BooleanField(default=True, help_text='发生保险事故时，补偿您自己车辆的损失。例如车辆发生碰撞、倾覆、火灾、爆炸，或被外界物体倒塌、坠物砸坏，以及与别人车辆发生碰撞，造成自己的车辆受损等，保险公司将按照条款赔偿您的车辆维修费用', verbose_name='机动车辆损失险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_dqx',
            field=models.BooleanField(default=False, help_text='如果车辆被盗窃、抢劫、抢夺，经公安机关立案证明，保险公司将按条款规定赔偿。', verbose_name='盗抢险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_dsxr',
            field=models.CharField(choices=[('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')], help_text='发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。', max_length=100, null=True, verbose_name='第三责任险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_fdjss',
            field=models.BooleanField(default=False, help_text='车辆在使用过程中，因发动机进水后导致的发动机的直接损毁，保险公司将按条款规定赔偿。', verbose_name='发动机涉水损失险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_hw',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，致使保险车辆所载货物遭受直接损毁，依法应由被保险人承担的经济赔偿责任，保险人负责赔偿。', max_length=100, null=True, verbose_name='车上货物责任险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_pl',
            field=models.BooleanField(default=False, help_text='如果发生挡风玻璃或车窗玻璃单独破碎，保险公司按实际损失进行赔偿。例如被高空坠物或飞石击碎挡风玻璃或车窗玻璃。', verbose_name='玻璃单独破碎险'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_sj',
            field=models.CharField(blank=True, choices=[('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')], help_text='发生意外事故，造成本车驾驶员本人的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。', max_length=100, null=True, verbose_name='车上人员责任险-司机'),
        ),
        migrations.AddField(
            model_name='insurancerecord',
            name='insurance_zrss',
            field=models.BooleanField(default=False, help_text='因本车电器、线路、油路、供油系统、供气系统、车载货物等自身发生问题，或者车辆运转摩擦引起火灾，造成本车的损失，以及为减少本车损失所支出的必要合理的施救费用，保险公司将按条款规定赔偿。', verbose_name='自燃损失险'),
        ),
        migrations.AddField(
            model_name='storeinfo',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='照片'),
        ),
        migrations.AlterField(
            model_name='insurancerecord',
            name='insurance_company',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.InsuranceCompany', verbose_name='保险公司'),
        ),
        migrations.AddField(
            model_name='serviceapply',
            name='oil_package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.OilPackage', verbose_name='机油套餐'),
        ),
    ]
