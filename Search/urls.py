from django.contrib import admin
from django.urls import path
from mysite.views import index,select_condition

urlpatterns = [
    path("output/",select_condition),
    #path("add/",select_condition),
    path('', index),
]
