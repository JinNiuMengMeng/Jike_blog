# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from myblog1.models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db.models import Count
from myblog1.forms import *
import json
from django.core.urlresolvers import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
#引入分页器的类，后三者是异常类型

logger = logging.getLogger('myblog1.views')


#分页代码
def getPage(request, article_list):
    paginator = Paginator(article_list, 3)
    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list


# Create your vi ews here.
def get_setting(request):#获取setting文件中的信息， 此函数需要在setting文件TEMPLATES中配置，不然不会被调用
    #文章归档
    archive_list = Article.objects.distinct_date()  # 按照自定义的manager去重复查询日期
    #标签分类
    tag_list = Tag.objects.all()
    #友情链接
    friend_link = Links.objects.all()
    #排序结果
    sort_results = Article.objects.order_by("-click_count")

    return {
        'archive_list':archive_list,
        'tag_list':tag_list,
        'friend_link':friend_link,
        'sort_results':sort_results,

        'SITE_URL':settings.SITE_URL,
        'SITE_NAME':settings.SITE_NAME,
        'SITE_DESC':settings.SITE_DESC,
        'WEIBO_SINA':settings.WEIBO_SINA,
        'WEIBO_TENCENT':settings.WEIBO_TENCENT,
        'PRO_RSS': settings.PRO_RSS,
        'PRO_EMAIL': settings.PRO_EMAIL,
        'AUTHOR':settings.AUTHOR
    }


def index(request):
    #文章列表, 分类列表, 标签列表可以放在全局的一个配置中, 不用每次都获取
    article_list = Article.objects.all()
    category_list = Category.objects.all()

    paginator = Paginator(article_list, 3) #创建分页器对象
    page = request.GET.get('page', 1)  # 获取当前页的页码数
    try:
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)

    #archive_list = Article.objects.distinct_date()#按照自定义的manager去重复查询日期

    #return render(request, 'index.html', {'article':article_list, 'category':category_list, 'tag':tag})
    return render(request, 'index.html', locals())
    #locals()函数会自动将本函数中的变量传递到index.html中,与上一句的效果相同


def base(request):
    article_list = Article.objects.all()
    tag_list = Tag.objects.all()
    return render(request, 'base.html', {'article':article_list, 'tag':tag_list})


def article_content(request, nid):
    id = nid
    try:
       article = Article.objects.get(id=nid)
    except Article.DoesNotExist:
        return render(request, 'failure.html', {'reason':'没有找到对应的文章'})
    article.click_count += 1
    article.save()

    # 评论表单, is_authenticated判断用户是否已经注册
    comment_form = CommentForm({'author': request.user.username,
                                'email': request.user.email,
                                 'url': request.user.url,
                                'article': id} if request.user.is_authenticated() else{'article': id})
    # 获取评论信息
    comments = Comment.objects.filter(article=article).order_by('id')
    comment_list = []
    for comment in comments:
        for item in comment_list:
            if not hasattr(item, 'children_comment'):
                setattr(item, 'children_comment', [])
            if comment.pid == item:
                item.children_comment.append(comment)
                break
        if comment.pid is None:
            comment_list.append(comment)

    return render(request, 'article_content.html', locals())


def archive(request):

    #获取客户端提交的信息（年份， 月份， 天份）
    year = request.GET.get("year", None)
    month = request.GET.get("month", None)
    day = unicode(str(request.GET.get("day", None)).strip())#去除多余的字符, 并转换成unicode编码, 同year, month相一致

    article_list = Article.objects.filter(date_publish__icontains=year+'-'+month+'-'+day)

    article_list = getPage(request, article_list)

    return render(request, 'archive.html', locals())


def tag_article(request, tag_id):

    tag_t = Tag.objects.get(id=tag_id)#先找到标签id对应的标签名(tag.name)
    article_list = Article.objects.filter(tag__name__icontains=tag_t)
    #article与tag是多对多的关系,根据tag_name模糊查询,找到所有包含tag_t的文章对象

    article_list = getPage(request, article_list)
    return render(request, 'tag_article.html', locals())


# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                             email=comment_form.cleaned_data["email"],
                                             url=comment_form.cleaned_data["url"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())

# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())


def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())