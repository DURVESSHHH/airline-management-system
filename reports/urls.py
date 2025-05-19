from django.urls import path
from .views import download_csv_report, report_detail

app_name = 'reports'

urlpatterns = [
    path('detail/', report_detail, name='report_detail'),
    path('download-csv/', download_csv_report, name='download_csv_report'),
]
