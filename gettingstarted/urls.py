from django.urls import include, re_path, path
from django.views.generic.base import RedirectView
from django.contrib import admin
from users import views as users_views
from answers import views as answers_views
admin.autodiscover()

import hello.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

app_name = 'main'  # here for namespacing of urls.
favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)
urlpatterns = [
    path('hello/', include('hello.urls')),
    path("", hello.views.index, name="index"),
    path("db/", hello.views.db, name="db"),
    re_path(r'^favicon\.ico$', favicon_view),
    path("about", hello.views.about, name="about"),
    path("faq", hello.views.faq, name="faq"),
    path("privacy-policy", hello.views.privacy, name="privacy-policy"),
    path('admin/', admin.site.urls),
    path('', users_views.IndexView.as_view(), name='index'),
    path('login/', users_views.login, name='login'),
    path('logout/', users_views.logout, name='logout'),
    path('register/', users_views.register, name='register'),
    path('explore/', answers_views.IndexView.as_view(), name='explore'),
    path('search/', answers_views.SearchView.as_view(), name='search'),
    path('topics/', include('topics.urls')),
    path('users/', include('users.urls')),
    path('asks/', include('asks.urls')),
    path('answers/', include('answers.urls')),
    path('comments/', include('comments.urls')),
]
