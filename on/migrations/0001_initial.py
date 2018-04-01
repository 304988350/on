# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-13 03:18
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('activity_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('activity_type', models.CharField(choices=[('0', '作息'), ('1', '跑步'), ('2', '购书阅读')], max_length=16)),
                ('coefficient', models.DecimalField(decimal_places=2, max_digits=12)),
                ('active_participants', models.IntegerField(default=0)),
                ('max_participants', models.IntegerField(default=0)),
                ('bonus_all', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('description', models.CharField(default='', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='ReadingGoal',
            fields=[
                ('goal_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('activity_type', models.CharField(choices=[('0', '作息'), ('1', '跑步'), ('2', '购书阅读')], default='0', max_length=16)),
                ('goal_type', models.IntegerField(choices=[(0, '自由模式'), (1, '日常模式')], default=1)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('goal_day', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ACTIVE', '进行中'), ('FAILED', '失败'), ('SUCCESS', '成功'), ('PENDING', '等待支付')], default='PENDING', max_length=32)),
                ('mode', models.CharField(choices=[('S', '学生'), ('N', '普通')], default='N', max_length=10)),
                ('guaranty', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('down_payment', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('coefficient', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('bonus', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('none_punch_days', models.IntegerField(default=0)),
                ('book_name', models.CharField(default='无名书籍', max_length=128)),
                ('goal_page', models.IntegerField()),
                ('finish_page', models.IntegerField(default=0, null=True)),
                ('max_return', models.FloatField(null=True)),
                ('is_start', models.BooleanField(default=False)),
                ('price', models.FloatField(default=0)),
                ('imageurl', models.CharField(default='/static/order/demo.png', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReadingPunchRecord',
            fields=[
                ('punch_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('record_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('bonus', models.DecimalField(decimal_places=2, max_digits=12)),
                ('start_page', models.IntegerField(default=0)),
                ('reading_page', models.IntegerField(default=0)),
                ('reading_delta', models.IntegerField(default=0)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='punch', to='on.ReadingGoal')),
            ],
        ),
        migrations.CreateModel(
            name='RunningGoal',
            fields=[
                ('goal_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('activity_type', models.CharField(choices=[('0', '作息'), ('1', '跑步'), ('2', '购书阅读')], default='0', max_length=16)),
                ('goal_type', models.IntegerField(choices=[(0, '自由模式'), (1, '日常模式')], default=1)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('goal_day', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ACTIVE', '进行中'), ('FAILED', '失败'), ('SUCCESS', '成功'), ('PENDING', '等待支付')], default='PENDING', max_length=32)),
                ('mode', models.CharField(choices=[('S', '学生'), ('N', '普通')], default='N', max_length=10)),
                ('guaranty', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('down_payment', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('coefficient', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('bonus', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('none_punch_days', models.IntegerField(default=0)),
                ('goal_distance', models.FloatField(null=True)),
                ('kilos_day', models.FloatField(null=True)),
                ('left_distance', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RunningPunchPraise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('punch_id', models.UUIDField()),
            ],
        ),
        migrations.CreateModel(
            name='RunningPunchRecord',
            fields=[
                ('punch_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('record_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('voucher_ref', models.CharField(max_length=256)),
                ('voucher_store', models.CharField(max_length=512)),
                ('distance', models.FloatField(default=0)),
                ('praise', models.IntegerField(default=0)),
                ('report', models.IntegerField(default=0)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='punch', to='on.RunningGoal')),
            ],
        ),
        migrations.CreateModel(
            name='RunningPunchReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0)),
                ('punch_id', models.UUIDField(default=uuid.uuid4)),
            ],
        ),
        migrations.CreateModel(
            name='SleepingGoal',
            fields=[
                ('goal_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('activity_type', models.CharField(choices=[('0', '作息'), ('1', '跑步'), ('2', '购书阅读')], default='0', max_length=16)),
                ('goal_type', models.IntegerField(choices=[(0, '自由模式'), (1, '日常模式')], default=1)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('goal_day', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ACTIVE', '进行中'), ('FAILED', '失败'), ('SUCCESS', '成功'), ('PENDING', '等待支付')], default='PENDING', max_length=32)),
                ('mode', models.CharField(choices=[('S', '学生'), ('N', '普通')], default='N', max_length=10)),
                ('guaranty', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('down_payment', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('coefficient', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('bonus', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('none_punch_days', models.IntegerField(default=0)),
                ('getup_time', models.TimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SleepingPunchRecord',
            fields=[
                ('punch_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('confirm_time', models.DateTimeField(null=True)),
                ('before_sleep_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('get_up_time', models.DateTimeField(null=True)),
                ('check_time', models.DateTimeField(null=True)),
                ('is_success', models.BooleanField(default=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='punch', to='on.SleepingGoal')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('user_id', models.IntegerField()),
                ('Ticket_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('get_way', models.IntegerField(null=True)),
                ('indate', models.DateTimeField()),
                ('is_use', models.IntegerField(choices=[('0', '未使用'), ('1', '已使用')], default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('sex', models.IntegerField(default=0)),
                ('wechat_id', models.CharField(max_length=255, unique=True)),
                ('nickname', models.CharField(max_length=255)),
                ('headimgurl', models.CharField(max_length=300, validators=[django.core.validators.URLValidator()])),
                ('deposit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('points', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('virtual_balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('all_profit', models.FloatField(default=0)),
                ('today_profit', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserOrder',
            fields=[
                ('order_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('owner_name', models.CharField(max_length=64, null=True)),
                ('owner_phone', models.CharField(max_length=13, null=True)),
                ('user_id', models.IntegerField(default=100100)),
                ('address', models.CharField(max_length=255, null=True)),
                ('status', models.CharField(choices=[('N', '已下单'), ('S', '已发货'), ('E', '已收件')], default='N', max_length=32)),
                ('postal_code', models.CharField(max_length=255, null=True)),
                ('postal_name', models.CharField(max_length=64, null=True)),
                ('order_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('delivery_time', models.DateTimeField(null=True)),
                ('confirm_time', models.DateTimeField(null=True)),
                ('order_money', models.FloatField(default=0)),
                ('order_name', models.CharField(default='未填写', max_length=255)),
                ('order_image', models.CharField(default='/static/order/demo.png', max_length=255)),
                ('order_count', models.IntegerField(default=1)),
                ('remarks', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finish_times', models.IntegerField(default=0)),
                ('join_times', models.IntegerField(default=0)),
                ('finish_days', models.IntegerField(default=0)),
                ('all_coefficient', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserRefund',
            fields=[
                ('refund_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_id', models.CharField(max_length=255)),
                ('total_fee', models.IntegerField(default=1)),
                ('refund_fee', models.IntegerField(default=1)),
                ('goal_id', models.UUIDField(default=uuid.UUID('4eec0e70-6d6a-4586-8a5c-ed15db7afdfc'))),
                ('openid', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('create_time', models.DateTimeField(auto_created=True)),
                ('relation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.UUIDField()),
                ('friend_id', models.UUIDField()),
                ('group_id', models.IntegerField(null=True)),
                ('remark', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSettlement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('goal_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('bonus', models.FloatField(default=0)),
                ('generate_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal_id', models.UUIDField(default=uuid.uuid4)),
                ('ticket_type', models.CharField(choices=[('D', '延时'), ('NS', '免签')], max_length=32)),
                ('number', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserTicketUseage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal_id', models.UUIDField(default=uuid.uuid4)),
                ('ticket_type', models.CharField(choices=[('D', '延时'), ('NS', '免签')], max_length=32)),
                ('useage_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserTrade',
            fields=[
                ('trade_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_info', models.CharField(max_length=255)),
                ('openid', models.CharField(max_length=255)),
                ('goal_id', models.UUIDField(default=uuid.uuid4)),
                ('trade_type', models.CharField(max_length=255)),
                ('trade_state', models.CharField(max_length=255)),
                ('bank_type', models.CharField(max_length=255, null=True)),
                ('total_fee', models.IntegerField()),
                ('cash_fee', models.IntegerField()),
                ('fee_type', models.CharField(max_length=255, null=True)),
                ('transaction_id', models.CharField(max_length=255)),
                ('out_trade_id', models.CharField(max_length=255)),
                ('time_end', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserWithdraw',
            fields=[
                ('trade_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('openid', models.CharField(max_length=255)),
                ('amount', models.IntegerField(default=0)),
                ('partner_trade_no', models.CharField(max_length=255, null=True)),
                ('payment_no', models.CharField(max_length=255, null=True)),
                ('finish_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='on.UserInfo')),
                ('phone', models.CharField(max_length=13, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userticket',
            unique_together=set([('goal_id', 'ticket_type')]),
        ),
        migrations.AddField(
            model_name='userrecord',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='record', to='on.UserInfo'),
        ),
        migrations.AlterUniqueTogether(
            name='sleepinggoal',
            unique_together=set([('user_id', 'activity_type', 'status', 'start_time')]),
        ),
        migrations.AlterUniqueTogether(
            name='runningpunchreport',
            unique_together=set([('punch_id', 'user_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='runningpunchpraise',
            unique_together=set([('punch_id', 'user_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='runninggoal',
            unique_together=set([('user_id', 'activity_type', 'status', 'start_time')]),
        ),
        migrations.AlterUniqueTogether(
            name='readinggoal',
            unique_together=set([('user_id', 'activity_type', 'status', 'start_time')]),
        ),
        migrations.AlterUniqueTogether(
            name='activity',
            unique_together=set([('activity_type', 'description')]),
        ),
    ]