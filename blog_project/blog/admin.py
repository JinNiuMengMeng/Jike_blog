# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'click_count') #将文章按照设置分列显示
    list_display_links = ('title', 'desc',) #将title与desc设置为链接，点击后可以编辑文章
    list_editable = ('click_count', ) #在列表页可编辑点击次数(click_count)

    fieldsets = (
        ['Main', {'fields':('title', 'desc', 'content')}],
        ['高级设置', {
            'classes':('collapse',),
            'fields':('click_count', 'is_recommend', 'user', ),
        }]
    )

    class Media:
        js = (
            '/static/js/kindeditor-4.1.10/kindeditor-min.js',
            '/static/js/kindeditor-4.1.10/lang/zh_CN.js',
            '/static/js/kindeditor-4.1.10/config.js',
        )
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Catagory)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
admin.site.register(Ad)
admin.site.register(Links)