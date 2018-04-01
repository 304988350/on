import time
import re
import requests
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.utils import timezone
from wechatpy.utils import random_string

from on.models import RunningGoal, RunningPunchRecord, SleepingGoal, SleepingPunchRecord, ReadingGoal, \
    ReadingPunchRecord
from on.temp.push_template import do_push
from on.temp.template_map import template
from on.user import UserTicket, UserRecord, UserInfo
from on.wechatconfig import mediaApiClient
import os


def punch_success(openid, url, first, punch_time, punch_day, days):
    punch = {
        "touser": openid,
        "template_id": "Pd6cbEhAgyaDH3yAJOtiyIpjSLnaw7g04Q14dhsbw7w",
        "url": url,
        "topcolor": "#FF0000",
        "data": {
            "first": {
                "value": first,
                "color": "#173177"
            },
            "keyword1": {
                "value": punch_time,
                "color": "#173177"
            },
            "keyword2": {
                "value": punch_day,
                "color": "#173177"
            },
            "keyword3": {
                "value": days,
                "color": "#173177"
            },
            "remark": {
                "value": "坚持下去，改变就从现在开始",
                "color": "#173177"
            },
        }
    }
    return punch


# 举报模板提醒
def report_tem(openid, url, content, nickname):
    data = {
        "touser": openid,
        "template_id": "U4UwUUHXqj2EsM3L2x4cOBsLDbQNxZi8OXJdBtd_q2w",
        "url": url,
        "topcolor": "#FF0000",
        "data": {
            "first": {
                "value": "当举报审核通过，被举报人或当日直接记为未完成",
                "color": "#173177"
            },
            "keyword1": {
                "value": content,
                "color": "#173177"
            },
            "keyword2": {
                "value": nickname,
                "color": "#173177"
            },
            "remark": {
                "value": '感谢您的举报',
                "color": "#173177"
            },
        }
    }
    return data


# 跑步签到时上传图片
def running_sign_in_api(request):
    user = request.session["user"]
    """
    跑步签到后端 API
    :param request:
    :return:
    """
    """获取对应的目标的goal id"""
    goal_id = request.GET.get('goal', ' ')
    distance = float(request.GET.get('distance', 0))
    goal = RunningGoal.objects.get(goal_id=goal_id)

    """存储一段话"""
    document = request.GET.get("document", " ")
    # """获取User的WechatID"""
    user_wechat_id = request.session['user'].wechat_id
    """存储图片"""
    mediaid = request.GET.get('serverId', ' ')
    apiLink = mediaApiClient.get_url(mediaid)
    response = requests.get(apiLink)
    # User 名字加随机字符串
    fileName = user_wechat_id + "_" + "{}".format(user.user_id)+ "_" + random_string(16) + ".jpg"
    # 文件的实际存储路径
    """将打卡记录存储到数据库中,增加一段话"""
    punch = RunningPunchRecord.objects.create_record(goal, response.content, filename=fileName, distance=distance,
                                                     document=document)
    goal.add_distance += distance
    goal.save()
    """增加用户的完成天数"""
    UserRecord.objects.update_finish_day(user=user)
    times = UserRecord.objects.get(user=user)
    if punch:
        if goal.goal_type == 1:
            first = "在{}天内，每日完成{}公里".format(goal.goal_day, goal.kilos_day)
        else:
            first = "在{}天内，一共完成{}公里".format(goal.goal_day, goal.goal_distance)
        # 发送打卡成功模板提醒
        punch_time = time.strftime('%m月%d日', time.localtime(time.time()))
        end_time = (timezone.now() + timedelta(days=goal.goal_day)).strftime('%m月%d日')
        url = 'http://wechat.onmytarget.cn/'
        # first = "在{}天内，每日完成{}公里".format(goal.goal_day, goal.kilos_day)
        days = '{}/{}'.format(times.finish_days, goal.goal_day)
        punch_day = "{}-{}".format(goal.start_time.strftime('%m月%d日'), end_time)
        data = punch_success(user.wechat_id, url, first, punch_time, punch_day, days)
        print("{}用户开始打卡".format(user.user_id))
        do_push(data)
    return HttpResponse(200)


# 重新上传打卡图片
def upload_again(request):
    user = request.session["user"]
    if request.method == "GET":
        punch_id = request.GET.get("punch_id")
        mediaid = request.GET.get('serverId', ' ')
        document = request.GET.get("document", " ")
        distance = request.GET.get("distance", " ")
        apiLink = mediaApiClient.get_url(mediaid)
        response = requests.get(apiLink)
        user_wechat_id = user.wechat_id
        # User 名字加随机字符串
        fileName = user_wechat_id + "_" + "{}".format(user.user_id) + "_" + random_string(16) + ".jpg"
        # 文件存储的实际路径
        filePath = os.path.join(settings.MEDIA_DIR, fileName)
        # 引用所使用的路径
        refPath = os.path.join(settings.MEDIA_ROOT, fileName)
        # 写入文件内容
        with open(filePath, 'wb') as f:
            f.write(response.content)
        record = RunningPunchRecord.objects.get(punch_id=punch_id)
        record.reload += 1
        record.voucher_ref = refPath
        record.document = document
        record.voucher_store = filePath
        record.record_time = timezone.now()

        record.save()

        goal = RunningGoal.objects.get(user_id=user.user_id)

        # 自由模式剩余距离
        left_distance = goal.left_distance

        if goal.goal_type == 0:

            # 重写之前还剩下的距离
            killo = record.distance + left_distance
            # 重写累计距离
            goal.add_distance = float(goal.add_distance) - float(record.distance) + float(distance)
            goal.left_distance = float(killo) - float(distance)
            goal.save()
            record.distance = distance
            record.save()
        else:
            print("success")

        # record.save()

        return JsonResponse({'status': 201})
    else:
        return HttpResponseNotFound


# 跑步免签API
def running_no_sign_in_handler(request):
    if request.POST:
        goal = request.POST['goal']
        use_ticket = UserTicket.objects.use_ticket(goal_id=goal, ticket_type='NS')
        if use_ticket:
            return ({'status': 200})
        else:
            return JsonResponse({'status': 201})
    else:
        return HttpResponseNotFound


# 跑步举报API
def running_report_handler(request):
    if request.POST:
        punch = request.POST['punch']
        user = request.session['user']
        openid = user.wechat_id
        content = "被举报用户发布了虚假信息"
        nickname = UserInfo.objects.get(user_id=user.user_id).nickname
        RunningPunchRecord.objects.report_punch(user_id=user.user_id, punch_id=punch)
        url = 'http://wechat.onmytarget.cn/'
        data = report_tem(openid, url, content, nickname)
        do_push(data)
        return JsonResponse({'status': 200})
    else:
        return HttpResponseNotFound


# 跑步点赞API
def running_praise_handler(request):
    if request.POST:
        punch = request.POST['punch']
        user = request.session['user']
        RunningPunchRecord.objects.praise_punch(user_id=user.user_id, punch_id=punch)
        return JsonResponse({'status': 200})
    else:
        return HttpResponseNotFound


# 作息免签API

def sleeping_no_sign_in_handler(request):
    if request.POST:
        user_wechat_id = request.session['user'].wechat_id
        goal = request.POST['goal']
        # 免签卡记录的时间是8个小时以后的时间, 这一点作息与跑步不同
        use_ticket = UserTicket.objects.use_ticket(goal_id=goal, ticket_type='NS',
                                                   use_time=timezone.now() + timezone.timedelta(hours=8))
        if use_ticket:
            return JsonResponse({'status': 200})
        else:
            return JsonResponse({'status': 201})
    else:
        return HttpResponseNotFound


# 作息延时API
def sleeping_delay_handler(request):
    if request.POST:
        goal = request.POST['goal']
        # 延时记录的应该是第二天早上的起床时间延迟，为了检索方便，直接定位到第二天。因为一定是9点以后打卡睡眠，所以打卡在4小时后即可
        use_ticket = UserTicket.objects.use_ticket(goal_id=goal, ticket_type='D',
                                                   use_time=timezone.now() + timezone.timedelta(hours=8))
        if use_ticket:
            return JsonResponse({'status': 200})
        else:
            return JsonResponse({'status': 201})
    else:
        return HttpResponseNotFound


# 作息睡觉打卡
def sleeping_sleep_handler(request):
    if request.POST:
        user = request.session['user']
        # 查询当前打卡用户的openid
        openid = user.wechat_id
        # 查询用户的nickname
        nickname = user.nickname
        goal_id = request.POST['goal']
        goal = SleepingGoal.objects.get(goal_id=goal_id)
        # 当前用户的打卡时间
        punch_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 如果record无误，则打卡成功；否则打卡失败
        record = SleepingPunchRecord.objects.create_sleep_record(goal=goal)
        remark_msg = "记得明天早晨也要打卡哦"
        if record:

            return JsonResponse({'status': 200,
                                 'time': record.before_sleep_time.time().strftime("%H:%M")})
        else:
            return JsonResponse({'status': 201})
    else:
        return HttpResponseNotFound


# 作息起床打卡
def sleeping_getup_handler(request):
    if request.POST:
        user = request.session['user']
        # 查询当前打卡用户的openid
        openid = user.wechat_id
        # 查询用户的nickname
        nickname = user.nickname
        goal_id = request.POST['goal']
        goal = SleepingGoal.objects.get(goal_id=goal_id)
        punch_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 如果record无误，则返回早起时间；否则打卡失败
        record = goal.punch.update_getup_record()
        remark_msg = ""
        if record:
            return JsonResponse({'status': 200,
                                 'getuptime': record.get_up_time.time().strftime("%H:%M"),
                                 'checktime': record.check_time.time().strftime("%H:%M")})
        else:

            return JsonResponse({'status': 201})


# 作息确认打卡
def sleeping_confirm_handler(request):
    if request.POST:
        user = request.session['user']
        # 查询当前打卡用户的openid
        openid = user.wechat_id
        # 查询用户的nickname
        nickname = user.nickname
        goal_id = request.POST['goal']
        goal = SleepingGoal.objects.get(goal_id=goal_id)
        punch_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 如果record无误，则返回确认时间；否则打卡失败
        record = goal.punch.update_confirm_time()
        if record:
            """增加用户的完成天数"""
            UserRecord.objects.update_finish_day(user=request.session['user'])
            return JsonResponse({'status': 200,
                                 'time': record.confirm_time.time().strftime("%H:%M")})
        else:
            return JsonResponse({'status': 201})


# 开启书籍阅读
def reading_start_handler(request):
    if request.POST:
        goal_id = request.POST['goal']
        goal = ReadingGoal.objects.get(goal_id=goal_id)
        # 开始阅读后，更改阅读时间
        if settings.DEBUG:
            # 只是暂定一个时间，最迟1个月后开始
            goal.start_time = timezone.now() - timedelta(days=30)
        else:
            goal.start_time = timezone.now()
        goal.is_start = True
        goal.save()
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 201})


# 书籍阅读打卡
def reading_record_handler(request):
    if request.POST:
        user_wechat_id = request.session['user'].wechat_id
        # 本次阅读了page页，耗时time秒
        goal_id = request.POST['goal']
        timedelta = request.POST['time']
        page = request.POST['page']
        # 新建一个阅读记录，并返回返回值
        return ReadingPunchRecord.objects.create_record(goal_id=goal_id,
                                                        today_page=page,
                                                        today_time=timedelta)
    else:
        return HttpResponseNotFound


# 查询擂主押金
def search_deposit(request):
    if request.GET:

        winner = RunningGoal.objects.get(user_id='100101').activate_deposit
        if winner:
            return JsonResponse({'status': 200, "winner": winner})
        else:
            return JsonResponse({'status': 403})
    else:
        return HttpResponseNotFound
