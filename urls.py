from django.urls import path

from . import views

urlpatterns =[
    path('',views.demo,name='index'),
    #path("demo/",views.home,name="home")
]