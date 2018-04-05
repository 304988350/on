# import logging

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import decimal
from on.activities.reading.views import show_reading_goal
from on.activities.running.views import show_running_goal
from on.activities.sleeping.views import show_sleeping_goal
from on.models import Activity, Goal, RunningGoal, SleepingGoal, ReadingGoal, RunningPunchRecord
from on.user import UserInfo, UserRecord, FoolsDay, UserInvite
from on.views import oauth
from on.temp.push_template import do_push
from on.wechatconfig import get_wechat_config
from datetime import timedelta, date, datetime
import django.utils.timezone as timezone

goal_mapping = {
    RunningGoal.get_activity(): show_running_goal,
    SleepingGoal.get_activity(): show_sleeping_goal,
    ReadingGoal.get_activity(): show_reading_goal,

}

"""
每天凌晨遍历每个goal，检查该目标下的打卡记录是否完整；
首先设立一个字典，用于更新每个目标拿到的扣除的钱。

对于每个目标而言，
（日常模式）如果昨日的打卡完成了，则更新一下目标的进度
（日常模式）如果昨日的打卡未完成
    若用户目标下有对应的免签券，则自动使用；
    否则将数据库中的打卡时间设置为前一天晚上10点，
"""


# logger = logging.getLogger("app")


# 展示用户的目标列表
@oauth
def show_goals(request):
    user = request.session['user']
    sub_models = get_son_models(Goal)
    all_goals = []
    status = True
    for sub_model_key in sub_models:
        all_goals += sub_models[sub_model_key].objects.filter(user_id=user.user_id)
    payed_goals = [goal for goal in all_goals if goal.status != 'PENDING']
    if payed_goals == []:
        status = False
    # 检测用户是否激活愚人节活动
    if FoolsDay.objects.check_user(user.user_id):
        fools = 1
    else:
        fools = 0
        # 判断用户是否参与了愚人节活动
        # 判断用户是否参与了愚人节活动
    if FoolsDay.objects.join_in_fools(user_id=user.user_id):
        join = 1
    else:
        join = 0
    join_num = FoolsDay.objects.filter(is_no_join=1)
    # user_start_time = RunningGoal.objects.get(user_id=user.user_id).start_time
    # a = user_start_time.strftime("%Y-%m-%d")
    # user_end_time = (user_start_time + timedelta(days=1)).strftime("%Y-%m-%d")
    # if len(RunningPunchRecord.objects.filter(goal_id=user., record_time__range=(a, user_end_time))) > 0:
    #     first_day_record = 1
    # else:
    #     first_day_record = 0
    return render(request, 'goal/index.html',
                  {'goals': payed_goals, "status": status, "fools": fools, "join": join, "join_num": len(join_num)})


# 获取某个模型的所有子模型
def get_son_models(model):
    all_sub_models = {}
    for sub_model in model.__subclasses__():
        all_sub_models[sub_model.__name__] = sub_model
    return all_sub_models


# 展示某个特定的目标
@oauth
def show_specific_goal(request, pk):
    goal_type = request.GET.get('activity_type')
    return goal_mapping[goal_type](request, pk)


# 展示特殊娱乐活动页面
@oauth
def show_activity(request):
    pass


# 展示分享页
@oauth
def show_goal_share(request, pk):
    user = request.session['user']
    wechat_config = get_wechat_config(request)
    sub_models = get_son_models(Goal)
    goal = None
    for sub_model_key in sub_models:
        query = sub_models[sub_model_key].objects.filter(user_id=user.user_id).filter(goal_id=pk)
        if query:
            goal = query[0]
            break
    if goal:
        # 跑步自由模式
        if goal.activity_type == RunningGoal.get_activity() and goal.goal_type == 0:
            goal_intro = "在{0}天内累计跑步{1}km".format(goal.goal_day, goal.goal_distance)
        elif goal.activity_type == RunningGoal.get_activity():
            goal_intro = "在{0}天内每天跑步{1}km".format(goal.goal_day, goal.kilos_day)
        elif goal.activity_type == ReadingGoal.get_activity():
            goal_intro = "在30天内阅读完书籍《{0}》".format(goal.book_name)
        elif goal.activity_type == SleepingGoal.get_activity():
            goal_intro = "在{0}天内每天早上{1}前起床".format(goal.goal_day, goal.getup_time.strftime("%H:%M"))
        else:
            goal_intro = ""
        return render(request,
                      'goal/share.html',
                      {
                          "WechatJSConfig": wechat_config,
                          "goal_intro": goal_intro,
                          "activity": goal.activity_type
                      })
    else:
        return HttpResponseNotFound


"""
# 展示目标结束页面，可能是失败也可能是成功
def show_goal_finish(request, pk):
    user = request.session['user']
    sub_models = get_son_models(Goal)
    goals = []
    for sub_model_key in sub_models:
        goals += sub_models[sub_model_key].objects.filter(goal_id=pk).filter(user_id=user.user_id)
    return render(request, "goal/finish.html")
"""


def finish_tem(openid, url, activate, finish_time, earn_money, earn_time, balance):
    data = {
        "touser": openid,
        "template_id": "AGL7ztiilHdjd4-5UDIscJOMlUdUGWr2gXvRJiy_ulQ",
        "url": url,
        "topcolor": "#FF0000",
        "data": {
            "first": {
                "value": "您好，有一笔活动收入结算成功",
                "color": "#173177"
            },
            "keyword1": {
                "value": activate,
                "color": "#173177"
            },
            "keyword2": {
                "value": finish_time,
                "color": "#173177"
            },
            "keyword3": {
                "value": earn_money,
                "color": "#173177"
            },
            "keyword4": {
                "value": earn_time,
                "color": "#173177"
            },
            "keyword5": {
                "value": balance,
                "color": "#173177"
            },
            "remark": {
                "value": "点击详情，查看个人中心",
                "color": "#173177"
            },
        }
    }
    return data


# 结束目标任务
def delete_goal(request):
    try:
        user = request.session['user']
        if request.method == "POST":
            # 删除当前的目标活动并退还钱
            activity_type = request.POST['goal_type']
            goal_id = request.POST['goal']
            delete_map = {
                RunningGoal.get_activity(): RunningGoal,
                ReadingGoal.get_activity(): ReadingGoal,
                SleepingGoal.get_activity(): SleepingGoal
            }
            for goal_type in delete_map.keys():
                if activity_type == goal_type:
                    goal_class = delete_map[goal_type]
                    goal = goal_class.objects.get(goal_id=goal_id)
                    # 增加用户的完成次数
                    # if goal.status == "SUCCESS":
                    UserRecord.objects.finish_goal(user=user)
                    # 用户触发，如果挑战成功则删除目标，退还押金
                    # 判断用户是否挑战成功
                    # if goal.refund_to_user(user.wechat_id):

                    # 更新用户的押金
                    UserInfo.objects.update_deposit(user_id=user.user_id,
                                                    pay_delta=-(goal.guaranty + goal.down_payment))
                    # 更新目前的奖金池
                    obj = Activity.objects.get(activity_type=goal.activity_type)
                    obj.bonus_all -= (goal.guaranty + goal.down_payment)
                    obj.save()

                    # 获取邀请了多少好友
                    num = UserInvite.objects.filter(user_id=request.session["user"].user_id).count()
                    # 用户获取收益的百分比
                    add_up = num * 0.5 + 1
                    if add_up >= 10:
                        add_up = 10
                    # 查询用户的额外收益
                    extra = UserInfo.objects.get(user_id=user.user_id)

                    # 查询用户当前的额外收益
                    Run = RunningGoal.objects.get(user_id=user.user_id)
                    extra_earn = Run.extra_earn
                    print(extra_earn)
                    price = decimal.Decimal(Run.guaranty) + decimal.Decimal(Run.down_payment) + decimal.Decimal(
                        Run.bonus * decimal.Decimal(add_up)) + decimal.Decimal(extra.extra_money)
                    # 将用户获取的收益存入余额
                    # 查询现在用户的保证金跟底金
                    UserInfo.objects.save_balance(user_id=user.user_id, price=price)
                    # openid = str(UserInfo.objects.get(user_id=user.user_id).wechat_id)
                    # 删除用户的目标
                    goal_class.objects.delete_goal(goal_id)
                    openid = user.wechat_id
                    url = 'http://wechat.onmytarget.cn/user/index'
                    activate = "跑步"
                    finish_time = timezone.now().strftime('%Y-%m-%d %H:%M')
                    earn_money = str(goal.guaranty + goal.down_payment)
                    earn_time = (goal.start_time + timedelta(days=goal.goal_day)).strftime('%Y-%m-%d %H:%M')
                    balance = str(UserInfo.objects.get(user_id=user.user_id).balance)
                    # 发送模板提醒
                    data = finish_tem(openid, url, activate, finish_time, earn_money, earn_time, balance)
                    do_push(data)
                    return JsonResponse({'status': 200})
            '''
            if activity_type == RunningGoal.get_activity():
                # 获取相应的goal,准备退款给用户
                goal = RunningGoal.objects.get(goal_id=goal_id)
                # 增加用户的完成次数
                if goal.status == "SUCCESS":
                    UserRecord.objects.finish_goal(user=user)
                if goal.refund_to_user(user.wechat_id):
                    RunningGoal.objects.delete_goal(goal_id)
                    return JsonResponse({'status': 200})
                else:
                    return JsonResponse({'status':403})
            elif activity_type == SleepingGoal.get_activity():
                goal = SleepingGoal.objects.get(goal_id=goal_id)
                UserRecord.objects.finish_goal(user=user)
                if goal.refund_to_user(user.wechat_id):
                    SleepingGoal.objects.delete_goal(goal_id)
                    return JsonResponse({'status': 200})
                else:
                    return JsonResponse({'status': 403})
            elif activity_type == ReadingGoal.get_activity():
                goal = ReadingGoal.objects.get(goal_id=goal_id)
                UserRecord.objects.finish_goal(user=user)
                if goal.refund_to_user(user.wechat_id):
                    ReadingGoal.objects.delete_goal(goal_id)
                    return JsonResponse({'status': 200})
                else:
                    return JsonResponse({'status': 403})
'''
        else:
            return JsonResponse({'status': 404})
    except Exception:
        return HttpResponseNotFound
    else:
        return JsonResponse({'status': 200})


# 创建一个目标任务
# @helper.json_render
@csrf_exempt
def create_goal(request):
    user = request.session['user']
    if request.POST:
        reality = request.POST['reality']
        deserve = request.POST["deserve"]
        down_num = request.POST["down_num"]
        guaranty = float(request.POST["guaranty"])
        down_payment = float(request.POST["down_payment"])
        extra_earn = 0
        average = float(down_payment) / int(down_num)
        print("每次要扣除的金额{}".format(average))
        print(average, "int(down_payment)/int(down_num)int(down_payment)/int(down_num)")
        activate_deposit = guaranty + down_payment
        print(activate_deposit)
        # 日志记录用户支付的钱数
        # logger.info("[Money] User {0} Pay {1} To Create A Goal".format(user.user_id, guaranty + down_payment))
        activity = request.POST["activity"]
        coefficient = float(request.POST["coefficient"])
        mode = request.POST["mode"]
        goal_day = int(request.POST["goal_day"])
        goal_type = request.POST["goal_type"]
        activity_type = Activity.objects.get(activity_id=activity).activity_type
        # activate_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 日常模式的结束时间
        # end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+timedelta(days=7)
        if activity_type == RunningGoal.get_activity():
            # activate = "跑步"
            distance = request.POST["distance"]
            nosign = request.POST["nosign"]
            rem = 0
            try:
                run = RunningGoal.objects.get(user_id=user.user_id)
            except Exception as e:
                # logger.info("用户活动记录不存在")
                rem = 1
                goal = RunningGoal.objects.create_goal(user_id=user.user_id,
                                                       runningtype=goal_type,
                                                       guaranty=guaranty,
                                                       down_payment=down_payment,
                                                       activate_deposit=activate_deposit,
                                                       coefficient=coefficient,
                                                       mode=mode,
                                                       goal_day=goal_day,
                                                       distance=distance,
                                                       nosign=nosign,
                                                       extra_earn=extra_earn,
                                                       average=average,
                                                       reality_price=reality,
                                                       deserve_price=deserve,
                                                       down_num=down_num)
                return JsonResponse({'status': 200, 'goal': goal.goal_id, "rem": rem})
            else:
                if run.status != "ACTIVE":
                    rem = 1
                    goal = RunningGoal.objects.create_goal(user_id=user.user_id,
                                                           runningtype=goal_type,
                                                           guaranty=guaranty,
                                                           down_payment=down_payment,
                                                           activate_deposit=activate_deposit,
                                                           coefficient=coefficient,
                                                           mode=mode,
                                                           goal_day=goal_day,
                                                           distance=distance,
                                                           nosign=nosign,
                                                           extra_earn=extra_earn,
                                                           average=average,
                                                           reality_price=reality,
                                                           deserve_price=deserve,
                                                           down_num=down_num)
                    return JsonResponse({'status': 200, 'goal': goal.goal_id, "rem": rem})
                else:
                    rem = 0
                    return JsonResponse({'status': 403, "rem": rem})
        elif activity_type == SleepingGoal.get_activity():
            nosign = request.POST["nosign"]
            delay = request.POST["delay"]
            getuptime = request.POST["getuptime"]
            goal = SleepingGoal.objects.create_goal(user_id=user.user_id,
                                                    guaranty=guaranty,
                                                    down_payment=down_payment,
                                                    coefficient=coefficient,
                                                    mode=mode,
                                                    goal_day=goal_day,
                                                    getuptime=getuptime,
                                                    nosign=nosign,
                                                    delay=delay,
                                                    )
            response_data = {'status': 200, 'goal': goal.goal_id}
            return JsonResponse(response_data)
        elif activity_type == ReadingGoal.get_activity():
            maxreturn = request.POST["maxreturn"]
            bookname = request.POST["bookname"]
            goalpage = request.POST["goalpage"]
            bookprice = request.POST["bookprice"]
            imageurl = request.POST["imageurl"]
            goal = ReadingGoal.objects.create_goal(user_id=user.user_id,
                                                   guaranty=guaranty,
                                                   max_return=maxreturn,
                                                   book_name=bookname,
                                                   goal_page=goalpage,
                                                   price=bookprice,
                                                   imageurl=imageurl)
            response_data = {'status': 200, 'goal': goal.goal_id}
            return JsonResponse(response_data)
    else:
        return HttpResponseNotFound
