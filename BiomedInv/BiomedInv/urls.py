"""
URL configuration for BiomedInv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital.views import *
urlpatterns = [
    path('machines_history/', machines_history, name="machines_history"),
    path('report_problem/', report_problem, name="report_problem"),
    path('update_room/', update_room, name='update_room'),
    path('generate_report/', generate_report, name='generate_report'),
    path('manufacturer/', manufacturer, name="manufacturer"),
    path('logout_page', logout_page, name='logout_page'),
    path('employee_register/', employee_register, name='employee_register'),
    path('engineer_dashboard/', engineer_dashboard, name='engineer_dashboard'),
    path('engineer_login/', engineer_login, name='engineer_login'),
    path('equipments/', equipments, name='equipments'),
    path('nurse_dashboard', nurse_dashboard, name='nurse_dashboard'),
    path('nurse_login/', nurse_login, name='nurse_login'),
    path('home/', home, name="home"),
    path('admin/', admin.site.urls),
]
