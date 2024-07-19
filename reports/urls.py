from django.urls import path
from .views import generate_daily_report, generate_monthly_report, generate_yearly_report, list_reports, generate_custom_report

urlpatterns = [
    path('daily/', generate_daily_report, name='generate_daily_report'),
    path('monthly/', generate_monthly_report, name='generate_monthly_report'),
    path('yearly/', generate_yearly_report, name='generate_yearly_report'),
    path('custom/', generate_custom_report, name='generate_custom_report'),
    path('', list_reports, name='list_reports'),
]
