import math
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from sklearn.cluster import DBSCAN
from .models import Accident, Hotspot, AnalysisRun

EARTH_RADIUS_KM = 6371.0088

def run_hotspot_analysis(dataset_name=""):
    records = list(Accident.objects.all())
    if len(records) < 3:
        raise ValueError("At least 3 valid accident records are required for DBSCAN analysis.")

    coords = [[math.radians(a.latitude), math.radians(a.longitude)] for a in records]
    # eps is in radians because DBSCAN uses the haversine metric.
    model = DBSCAN(eps=0.5 / EARTH_RADIUS_KM, min_samples=3, metric="haversine")
    labels = model.fit_predict(coords)

    run = AnalysisRun.objects.create(
        algorithm="DBSCAN (0.5 km, min_samples=3)",
        dataset_name=dataset_name,
        records_processed=len(records),
        status="completed",
    )
    Hotspot.objects.filter(analysis_run__isnull=False).delete()

    grouped = {}
    for record, label in zip(records, labels):
        if label == -1:
            continue
        grouped.setdefault(int(label), []).append(record)

    if not grouped:
        run.hotspots_found = 0
        run.save(update_fields=["hotspots_found"])
        return run

    now_date = timezone.localdate()
    raw = []
    for cluster_id, items in grouped.items():
        center_lat = sum(x.latitude for x in items) / len(items)
        center_lon = sum(x.longitude for x in items) / len(items)
        serious = sum(1 for x in items if x.severity.lower() in {"serious", "severe", "fatal"})
        recent = sum(1 for x in items if (now_date - x.date).days <= 365)
        raw.append({
            "cluster_id": cluster_id,
            "lat": center_lat,
            "lon": center_lon,
            "count": len(items),
            "serious": serious,
            "recent": recent,
        })

    max_count = max(x["count"] for x in raw) or 1
    max_serious = max(x["serious"] for x in raw) or 1
    max_recent = max(x["recent"] for x in raw) or 1

    for item in raw:
        frequency = item["count"] / max_count
        severity = item["serious"] / max_serious
        recency = item["recent"] / max_recent
        score = round((0.4 * frequency + 0.4 * severity + 0.2 * recency) * 100, 2)
        level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
        Hotspot.objects.create(
            cluster_id=item["cluster_id"],
            center_latitude=item["lat"],
            center_longitude=item["lon"],
            accident_count=item["count"],
            serious_count=item["serious"],
            recent_count=item["recent"],
            risk_score=score,
            risk_level=level,
            analysis_run=run,
        )

    run.hotspots_found = len(raw)
    run.save(update_fields=["hotspots_found"])
    return run
