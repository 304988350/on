from django.http import Http404
from django.shortcuts import render, redirect
import json
import functools
from wechatpy.oauth import WeChatOAuth
from django.http import HttpResponse, JsonResponse
from on.user import UserInfo, UserRelation, UserTrade, UserAddress, UserOrder, UserInvite, FoolsDay, Invitenum
from on.models import Activity, Goal, RunningPunchRecord, ReadingGoal, SleepingGoal, RunningGoal
from on.serializers import UserSerializer, ActivitySerializer
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.http import HttpResponseRedirect
from on.wechatconfig import oauthClient, client
from django.conf import settings
from on.wechatconfig import get_wechat_config
import decimal
from .QR_invite import user_qrcode
from django.views.decorators.csrf import csrf_exempt
from on.errorviews import page_not_found

mappings = {
    "0": "sleeping.html",
    "1": "running.html",
    "2": "reading.html",
    "3": "origami.html"
}


# o0jd6wgPxXAFK9aifqR858FOWDV0(王顺)
# o0jd6wh-yDVy-2YzvR-hz2gr_pUA歐成東
# o0jd6wnbJqpDofcVMx_MAbrw6dqQ (没有参加)
def oauth(method):
    @functools.wraps(method)
    def warpper(request, *args, **kwargs):
        if settings.DEBUG:
            user_info = {"openid": "o0jd6wqeLKWNJ-zruWoW-pD2YLdg",
                         "nickname": "",
                         "sex": "1",
                         "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46",
                         }
            wechat_id = user_info["openid"]
            user = UserInfo.objects.check_user(wechat_id)
            if not user:
                user = UserInfo.objects.create_user(user_info["openid"],
                                                    user_info["nickname"],
                                                    user_info["headimgurl"],
                                                    int(user_info["sex"]))
            request.session['user'] = user
            return method(request, *args, **kwargs)
        else:
            if request.session.get('user', False):
                return method(request, *args, **kwargs)
            if request.method == 'GET':
                code = request.GET['code'] if 'code' in request.GET else None
                print(code, "当前登陆的用户")
                oauthClient.redirect_uri = settings.HOST + request.get_full_path()
                # 如果有授权code, 说明是重定向后的页面
                if code:
                    # 利用code来换取网页授权的access_token
                    oauthClient.fetch_access_token(code=code)
                    # 如果access_token有效，则进行下一步
                    if not oauthClient.check_access_token():
                        redirect_url = oauthClient.authorize_url
                        return redirect(redirect_url)
                    else:
                        pass
                    # 利用access_token获取用户信息
                    try:
                        user_info = client.user.get(user_id=oauthClient.open_id)
                        wechat_id = user_info["openid"]
                        # 如果微信号不存在，则新建一个用户
                        user = UserInfo.objects.check_user(wechat_id)
                        if not user:
                            user = UserInfo.objects.create_user(user_info["openid"],
                                                                user_info["nickname"],
                                                                user_info["headimgurl"],
                                                                int(user_info["sex"]))
                    except Exception as e:
                        print(e)
                    else:
                        request.session['user'] = user
                        return method(request, *args, **kwargs)
                # 否则直接到重定向后的页面去
                else:
                    redirect_url = oauthClient.authorize_url
                    return redirect(redirect_url)
            else:
                return method(request, *args, **kwargs)

    return warpper


# 显示主页
@oauth
def show_activities(request):
    user = request.session["user"]
    activities = Activity.objects.all()
    # TODO: fake
    activities = fake_data(activities)

    # 检测用户是否激活愚人节活动
    if FoolsDay.objects.check_user(user.user_id):
        fools = 1
    else:
        fools = 0
    # 判断用户是否参与了愚人节活动
    if FoolsDay.objects.join_in_fools(user_id=user.user_id):
        join = 1
    else:
        join = 0

    return render(request, 'activity/index.html', {
        'activities': activities, "fools": fools, 'join': join})

# 展示用户的用户的协议
def agreement(request):
    return render(request, 'user/userAgreement.html')


# 展示用户的排行榜
# def rank_list(request):
#     user = request.session['user']
#     # 获取所有用户，目前按照user_id排序
#     user_id = UserInfo.objects.all().order_by("-user_id")[:20]
#     # 需要传递的数据待定
#     context = {
#         "test1": user_id
#     }
#     return render(request, 'user/test.html', context)

# fake数据
def fake_data(activities):
    for activity in activities:
        # 作息数据
        if activity.activity_type == "0":
            activity.coefficient += decimal.Decimal(155)
            activity.active_participants += 15
            activity.bonus_all += decimal.Decimal(2310)
        # 跑步数据
        elif activity.activity_type == "1":
            activity.coefficient += decimal.Decimal(0)
            activity.active_participants += 0
            activity.bonus_all += decimal.Decimal(0)
        # 阅读数据
        else:
            activity.active_participants += 0
            activity.bonus_all += decimal.Decimal(0)
    return activities


# 获取某个模型的所有子模型
def get_son_models(model):
    all_sub_models = {}
    for sub_model in model.__subclasses__():
        all_sub_models[sub_model.__name__] = sub_model
    return all_sub_models


# 显示活动的页面
@oauth
def show_specific_activity(request, pk):
    user = request.session['user']
    print("当前登录的用户是{},用户id是:{}".format(user.nickname, user.user_id))
    activity = Activity.objects.get(activity_id=pk)
    # 余额
    balance = UserInfo.objects.get(user_id=user.user_id).balance
    # TODO:FakeDATA
    activity = fake_data([activity])[0]
    # TODO
    if not settings.DEBUG:
        user = request.session['user']
        sub_models = get_son_models(Goal)
        for sub_model_key in sub_models:
            sub_model = sub_models[sub_model_key]
            goal = sub_model.objects.filter(user_id=user.user_id).filter(activity_type=activity.activity_type)
            if goal:
                goal = goal.first()
                if goal.status != "PENDING":
                    redirect_url = '/goal/{0}?activity_type={1}'.format(goal.goal_id, activity.activity_type)
                    return HttpResponseRedirect(redirect_url)
                else:
                    pass
    else:
        user = request.session['user']
        sub_models = get_son_models(Goal)
        for sub_model_key in sub_models:
            sub_model = sub_models[sub_model_key]
            goal = sub_model.objects.filter(user_id=user.user_id).filter(activity_type=activity.activity_type)
            if goal:
                goal = goal.first()

                if goal.status != "PENDING":
                    redirect_url = '/goal/{0}?activity_type={1}'.format(goal.goal_id, activity.activity_type)

                    return HttpResponseRedirect(redirect_url)

                else:
                    pass

    # 专门为读书设立的字段
    readinginfo = {
        'title': '你的生命有什么可能',
        'intro': '本书探讨了以下问题：高竞争的工作、高不可攀的房价和房租、 拥挤的交通、糟糕的空气、不安全的食品……在竭尽全力才能生存的时代，年轻人如何追求自己的梦想？在这样的时代，我们的生命又有什么可能？如何才能越过现实和理想的鸿沟，找到和进入自己希望的人生？如何修炼自己在现实中活得更好的能力？如何在现实之中发展自己的兴趣？如何连接现实和理想？如何面对生命里的苦难、贫穷、不完美或者不公正？如何获得心灵的自由？',
        'imageurl': '/static/images/reading_book_demo.png',
        'price': 35,
        'return': 20,
        'guaranty': 30,
        'page': 315
    }
    if activity.activity_type == ReadingGoal.get_activity():
        person_goals = ReadingGoal.objects.filter(status="ACTIVE")[:5]
    elif activity.activity_type == SleepingGoal.get_activity():
        person_goals = SleepingGoal.objects.filter(status="ACTIVE")[:5]
    else:
        person_goals = RunningGoal.objects.filter(status="ACTIVE")[:5]
    # 生成一个persons集合
    persons = set()
    for person_goal in person_goals:
        persons.add(UserInfo.objects.get(user_id=person_goal.user_id))

    return render(request, 'activity/{0}'.format(mappings[activity.activity_type]), {
        "app": activity,
        "readinginfo": readinginfo,
        "WechatJSConfig": get_wechat_config(request),
        "persons": persons,
        "DEBUG": settings.DEBUG,
        "balance": balance
    })


# 显示个人页面
@oauth
def show_user(request):
    user = request.session['user']
    userinfo = UserInfo.objects.get(user_id=user.user_id)
    record = userinfo.record.first()
    success_rate = 0 if record.join_times == 0 else int(float(record.finish_times) * 100 / record.join_times)
    fools_obj = FoolsDay.objects.check_user(user.user_id)
    # 检测用户是否参与愚人节活动
    if fools_obj:
        fools = 1
        status = fools_obj.status
    else:
        fools = 0
        status =3
    # 保证金跟底金
    return render(request, 'user/index.html', {
        'user': userinfo,
        'record': record,
        'successrate': success_rate,
        "fools": fools,
        "status":status
    })


# 更新个人信息
@oauth
@csrf_exempt
def update_address(request):
    user = request.session['user']
    if request.method == 'POST':
        address_dict = json.loads(request.POST.get("data"))
        UserAddress.objects.update_address(user=user, field_dict=address_dict)
        return JsonResponse({'status': 200})
    else:
        return JsonResponse({'status': 403})


# 获取用户的打卡记录信息
def show_history(request):
    user = request.session['user']
    punch_inform = user.record.first()
    # 找到 User 所有的Goal,按照时间排列
    all_goals = []
    all_punchs = []
    for sub_model in Goal.__subclasses__():
        all_goals.append(sub_model)
    # 遍历所有的Goal, 找到其对应的 Punch 的类型
    for goal in all_goals:
        try:
            punchs = goal.objects.get(user=user)
            all_punchs += [format_record(record) for record in punchs.punch.all()]
        except:
            pass
    all_punchs.sort(key=lambda x: x['time'])
    all_punchs.reverse()
    # TODO: 添加更多活动的 punchs 显示
    record = user.record.first()
    success_rate = 0 if record.join_times == 0 else int(float(record.finish_times) * 100 / record.join_times)
    return render(request, 'user/history.html', {
        'punchs': all_punchs,
        'punchinform': punch_inform,
        'successrate': success_rate
    })


# 格式化所有的打卡记录
def format_record(punch):
    # 添加更多punch record
    if isinstance(punch, RunningPunchRecord):
        target_days = int(punch.goal.goal_day)
        target_distance = int(punch.goal.goal_distance)
        target = '{0:d}天,{1:d}km'.format(target_days, target_distance)
        if punch.goal.running_type == 0:
            punch_type = "跑步 自由模式"
        elif punch.goal.running_type == 1:
            punch_type = "跑步 自律模式"
        else:
            punch_type = "默认"
    else:
        target = '暂无'
    bonus = '{0:f}元'.format(punch.bonus)
    time = punch.record_time.strftime('%Y{0} %m{1} %d{2}').format('年', '月', '日')
    return {"type": punch_type, "target": target, "bonus": bonus, "time": time}


# 展示支付页面
@oauth
def show_cash(request):
    user = request.session['user']
    user_info = UserInfo.objects.get(user_id=user.user_id)
    return render(request, 'user/cash.html', {'balance': user_info.balance})


# 展示我的圈子
@oauth
def show_circle(request):
    user = request.session['user']
    user_id = user.user_id
    nickname = UserInfo.objects.get(user_id=user_id)
    sex = UserInfo.objects.get(user_id=user_id).sex
    context = {
        'user_id': user_id,
        "nickname": nickname,
        'sex': sex
    }
    return render(request, 'user/circle.html', context)


# 展示好友页面
@oauth
def show_friends(request):
    return render(request, 'user/friend.html')


# 展示我的订单
@oauth
def show_order(request):
    user = request.session['user']
    address = UserAddress.objects.get_address(user.user_id)
    orders = UserOrder.objects.filter(user_id=user.user_id)
    return render(request, 'user/order.html', {
        "address": address,
        "orders": orders
    })


# 分享
@oauth
@csrf_exempt
def share(request):
    user_id = request.GET.get("user_id")
    wechat_config = get_wechat_config(request)
    user = UserInfo.objects.get(user_id=user_id)
    nickname = user.nickname
    imgUrl = user.headimgurl
    ticket = user_qrcode(user.user_id)
    url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)
    context = {
        "user_id": user_id,
        "wechat_config": wechat_config,
        "nickname": nickname,
        "imgUrl": imgUrl,
        "url": url
    }
    return render(request, 'user/share.html', context)


@oauth
@csrf_exempt
def invite_num(request):
    if request.method == 'POST':
        user_id = request.session["user"].user_id
        num = UserInvite.objects.filter(user_id=user_id).count()
        return JsonResponse({"num": num})


def share_qrcode(request):
    user_id = request.GET.get("user_id")
    wechat_config = get_wechat_config(request)
    user = UserInfo.objects.get(user_id=user_id)
    nickname = user.nickname
    imgUrl = user.headimgurl
    ticket = user_qrcode(user.user_id)
    url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)
    context = {
        "user_id": user_id,
        "wechat_config": wechat_config,
        "nickname": nickname,
        "imgUrl": imgUrl,
        "url": url
    }
    return render(request, 'user/share.html', context)


@oauth
@csrf_exempt
def change_name(request):
    user = request.session["user"]
    if request.GET:
        new_name = request.GET.get("name")
        print("用户的新名字{}".format(new_name))
        user.nickname = new_name
        try:
            user.save()
        except Exception as e:
            print("保存失败，报错信息：{}".format(e))
            return JsonResponse({"status": 403})
        else:
            return JsonResponse({"status": 200})
    else:
        return JsonResponse({"status": 403})


@oauth
@csrf_exempt
def fools_day(request):
    user = request.session["user"]

    context = {
        "user": user.nickname,
        "user_id":user.user_id
    }
    return render(request, "festival/aprilFoolsDay/aprilFoolsDayJoin.html", context)


@oauth
@csrf_exempt
def join_fools(request):
    user = request.session["user"]
    if request.POST:
        rem = request.POST["rem"]
        if int(rem) == 1:
            FoolsDay.objects.join_act(user_id=user.user_id)
            return JsonResponse({"statu": 200, "user_id": user.user_id})
        else:
            pass
    else:
        return page_not_found(request)


# @oauth
# @csrf_exempt
# def foolsday_rank(request):
#     user = request.session["user"]
#     context = {
#         "user": user.nickname
#     }
#     return render(request, "festival/aprilFoolsDay/rank.html", context)


@csrf_exempt
def create_active(request):
    user = request.session["user"]
    if request.POST:
        # 传过来的状态码，1代表余额，0代表提现
        status = int(request.POST["req"])
        # 每有一个人激活，就给激活的那个人赠送0.41
        user = UserInfo.objects.get(user_id=user.user_id)
        user.balance += decimal.Decimal(0.41)
        user.save()
        #先判断用户是否已经创建了愚人节活动
        if FoolsDay.objects.join_in_fools(user_id=user.user_id):
            print("用户已经创建了愚人节活动")
            return JsonResponse({"status":403})
        else:
            print("给用户创建愚人节活动表")
            # 给用户创建愚人节活动表
            if status == 1:
                FoolsDay.objects.create(user_id=user.user_id, add_point=5, reduce_point=0, point_all=5, status=status,
                                        is_no_join=0)
            else:
                FoolsDay.objects.create(user_id=user.user_id, add_point=0, reduce_point=3, point_all=3, status=status,
                                        is_no_join=0)
        # 查询当前点击用户的上级邀请用户的userID
        inviter = UserInvite.objects.filter(invite=user.wechat_id, fools_day=1)
        if inviter:
            # 上级用户的邀请id是
            uper = inviter[0].user_id
            print("上级用户的userid是{}".format(uper))
            # 若用户点击的是余额，则是增加积分
            if len(FoolsDay.objects.filter(user_id=uper)) > 0:
                if status == 0:
                    print("用户点击的是提现开始给用户增加积分")
                    FoolsDay.objects.add_points(user_id=uper)
                # 若用户点击的是提现，则减少积分
                else:
                    print("用户点击的是余额，开始给用户减少积分")
                    FoolsDay.objects.reduce_points(user_id=uper)
                FoolsDay.objects.update_point(user_id=uper)
                return JsonResponse({"status": 200})
            else:
                return JsonResponse({"status": 403})
        else:
            return JsonResponse({"status": 200})
    else:
        return page_not_found(request)


# 生成用户排行榜
@oauth
@csrf_exempt
def foolsday_rank(request):
    user = request.session["user"]
    user_message = []
    myself = []
    user_list = FoolsDay.objects.filter(is_no_join=1).order_by("-point_all")
    for users in user_list[:99]:
        # user_id = users.user_id
        user_data = UserInfo.objects.get(user_id=users.user_id)
        nickname = user_data.nickname
        userimg = user_data.headimgurl
        point = users.point_all
        # print("当前该用户的积分是{}".format(point))
        # user_rank = list(user_list).index(user)
        # 邀请了多少人
        if len(UserInvite.objects.filter(user_id=users.user_id, fools_day=1)) > 0:
            invite_num = len(UserInvite.objects.filter(user_id=users.user_id, fools_day=1))
        else:
            # 没查询到表示没有查询到
            invite_num = 0
        user_message.append({
            "user_id": users.user_id,
            "nickname": nickname,
            "userimg": userimg,
            "invite_num": invite_num,
            "point":point,
            # "user_rank":user_rank
        })
        my_invite_num = len(UserInvite.objects.filter(user_id=user.user_id, fools_day=1))
        myself = [{
            "user_id": user.user_id,
            "nickname": user.nickname,
            "userimg": user.headimgurl,
            "invite_num": my_invite_num,
            "point":  FoolsDay.objects.filter(user_id=user.user_id)[0].point_all,
        }]
    return render(request, 'festival/aprilFoolsDay/rank.html', {"user_message": user_message,"myself":myself,"user_id":user.user_id})
