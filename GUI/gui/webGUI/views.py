from django.shortcuts import render

from django.shortcuts import HttpResponse  # 导入HttpResponse模块


def helloworld(request):  # request是必须带的实例。类似class下方法必须带self一样
    return HttpResponse("Hello World!!")  # 通过HttpResponse模块直接返回字符串到前端页面

def index_view(request):
    return render(request, 'index.html')
def post_view(request):
    return render(request, 'post.html')
def author_view(request):
    return render(request, 'author.html')
