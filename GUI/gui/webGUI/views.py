from django.shortcuts import render

from django.shortcuts import HttpResponse  # 导入HttpResponse模块
from .models import UserInfo

def helloworld(request):  # request是必须带的实例。类似class下方法必须带self一样
    return HttpResponse("Hello World!!")  # 通过HttpResponse模块直接返回字符串到前端页面

def index_view(request):
    return render(request, 'index.html')
def post_view(request):
    return render(request, 'post.html')
def author_view(request):
    return render(request, 'author.html')

def toLogin_view(request):
    return render(request, 'login.html') #返回渲染好的login界面

def Login_view(request):

    u = request.POST.get('user','')
    p = request.POST.get('password','')

    if u and p :
        c = UserInfo.objects.filter(user_name=u, user_password=p).count()
        if c:
            return HttpResponse('登录成功!')
        else:
            return HttpResponse('登录失败！')

def toRegister_view(request):
    return render(request, 'register.html') #返回渲染好的界面

def register_view(request):
    u = request.POST.get('user', '')
    p = request.POST.get('password', '')
    if u and p:
        stu = UserInfo(user_name=u, user_password=p)
        stu.save()
        return HttpResponse('注册成功!')
    else:
        return HttpResponse('请重新输入！')