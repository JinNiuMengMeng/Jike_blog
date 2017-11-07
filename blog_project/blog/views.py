# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
import logging
# Create your views here.

logger = logging.getLogger('blog.views')#命名记录器，getLogger()的参数也可以使用__name__


def global_setting(request):
    return {'SITE_NAME':settings.SITE_NAME, 'SITE_DESC':settings.SITE_DESC}


def index(request):
    try:
        file = open('xxx.txt', 'r')
    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())