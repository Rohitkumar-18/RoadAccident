from django.db import models

class Accident(models.Model):
    accident_id = models.CharField(max_length=80, unique=True)
    date = models.DateField()
    time = models.TimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    accident_type = models.CharField(max_length=100, blank=True, default="")
    severity = models.CharField(max_length=30, blank=True, default="Unknown")
    weather = models.CharField(max_length=60, blank=True, default="")
    road_type = models.CharField(max_length=60, blank=True, default="")
    vehicle_type = models.CharField(max_length=60, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]

    def __str__(self):
        return self.accident_id


class AnalysisRun(models.Model):
    algorithm = models.CharField(max_length=50, default="DBSCAN")
    dataset_name = models.CharField(max_length=255, blank=True)
    records_processed = models.PositiveIntegerField(default=0)
    hotspots_found = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)


class Hotspot(models.Model):
    cluster_id = models.IntegerField()
    center_latitude = models.FloatField()
    center_longitude = models.FloatField()
    accident_count = models.PositiveIntegerField()
    serious_count = models.PositiveIntegerField(default=0)
    recent_count = models.PositiveIntegerField(default=0)
    risk_score = models.FloatField(default=0)
    risk_level = models.CharField(max_length=20, default="Low")
    analysis_run = models.ForeignKey(AnalysisRun, on_delete=models.CASCADE, related_name="hotspots")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-risk_score"]
