"""jike_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from myblog1 import views, upload
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', views.index, name='index'),
    url(r'^base/$', views.base, name='base'),
    url(r'^article_content/(?P<nid>\d+)/$', views.article_content, name='article_content'),
    url(r'^admin/upload/(?P<dir_name>[^/]+)$', upload.upload_image, name='upload_image'),
    url(r'^archive/$', views.archive, name='archive'),
    url(r'^tag_article/(?P<tag_id>[^/d]+)$', views.tag_article, name='tag_article'),

    url(r'^comment/post/$', views.comment_post, name='comment_post'),
    url(r'^logout$', views.do_logout, name='logout'),
    url(r'^reg', views.do_reg, name='reg'),
    url(r'^login', views.do_login, name='login'),
    url(r'^category/$', views.category, name='category'),
]
urlpatterns += staticfiles_urlpatterns()