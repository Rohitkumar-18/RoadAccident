from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),
    path("accidents/", views.accidents_list),
    path("accidents/upload/", views.upload_accidents),
    path("hotspots/", views.hotspots_list),
    path("analysis/run/", views.run_analysis),
    path("dashboard/", views.dashboard),
]
