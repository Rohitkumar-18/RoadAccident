from django.contrib import admin
from .models import Accident, Hotspot, AnalysisRun

admin.site.register(Accident)
admin.site.register(Hotspot)
admin.site.register(AnalysisRun)
