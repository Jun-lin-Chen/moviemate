from django.http import HttpResponseRedirect
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

#登录界面
def toLogin_view(request):
    return render(request, 'login.html') #返回渲染好的login界面

#将用户输入的用户名与密码与数据库中数据进行比对
def Login_view(request):

    u = request.POST.get('user','')
    p = request.POST.get('password','')

    if u and p :
        c = UserInfo.objects.filter(user_name=u, user_password=p).count()
        if c:
            return HttpResponseRedirect('http://127.0.0.1:8000/dev/index/')
        else:
            return HttpResponse('Login failed！')
    else:
        return HttpResponse('Your user name or password should not be empty！')

#注册界面
def toRegister_view(request):
    return render(request, 'register.html') #返回渲染好的界面

#将用户注册信息存入数据库
def register_view(request):
    u = request.POST.get('user', '')
    p = request.POST.get('password', '')
    if u and p:
        if UserInfo.objects.filter(user_name=u).exists():
            return HttpResponse('This username is already taken. Please try another one.')
        else:
            stu = UserInfo(user_name=u, user_password=p)
            stu.save()
            # Pass a message to the template
            message = 'Register successfully! Redirecting to login page in 2s...'
            return render(request, 'register_success.html', {'message': message})
    else:
        return HttpResponse('Please try again！')