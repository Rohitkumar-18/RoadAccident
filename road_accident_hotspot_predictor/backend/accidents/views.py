import csv
import io
from datetime import datetime
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.db.models import Count
from .models import Accident, Hotspot, AnalysisRun
from .serializers import AccidentSerializer, HotspotSerializer
from .services import run_hotspot_analysis

REQUIRED = {"accident_id", "date", "time", "latitude", "longitude"}

@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "message": "Road Safety API is running"})

@api_view(["GET"])
def accidents_list(request):
    qs = Accident.objects.all()
    severity = request.query_params.get("severity")
    if severity:
        qs = qs.filter(severity__iexact=severity)
    return Response(AccidentSerializer(qs[:500], many=True).data)

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_accidents(request):
    uploaded = request.FILES.get("file")
    if not uploaded:
        return Response({"error": "Please select a CSV file using the 'file' field."}, status=400)
    if not uploaded.name.lower().endswith(".csv"):
        return Response({"error": "Only CSV files are supported."}, status=400)
    try:
        decoded = uploaded.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            return Response({"error": "CSV file is empty."}, status=400)
        missing = REQUIRED - set(reader.fieldnames)
        if missing:
            return Response({"error": f"Missing required columns: {', '.join(sorted(missing))}"}, status=400)

        created, skipped, errors = 0, 0, []
        for line_no, row in enumerate(reader, start=2):
            try:
                accident_id = (row.get("accident_id") or "").strip()
                if not accident_id:
                    raise ValueError("accident_id is empty")
                lat, lon = float(row["latitude"]), float(row["longitude"])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError("coordinates out of range")
                date_value = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()
                time_text = row["time"].strip()
                try:
                    time_value = datetime.strptime(time_text, "%H:%M:%S").time()
                except ValueError:
                    time_value = datetime.strptime(time_text, "%H:%M").time()
                _, was_created = Accident.objects.get_or_create(
                    accident_id=accident_id,
                    defaults={
                        "date": date_value, "time": time_value,
                        "latitude": lat, "longitude": lon,
                        "accident_type": (row.get("accident_type") or "").strip(),
                        "severity": (row.get("severity") or "Unknown").strip() or "Unknown",
                        "weather": (row.get("weather") or "").strip(),
                        "road_type": (row.get("road_type") or "").strip(),
                        "vehicle_type": (row.get("vehicle_type") or "").strip(),
                    },
                )
                created += int(was_created)
                skipped += int(not was_created)
            except Exception as exc:
                if len(errors) < 10:
                    errors.append(f"Line {line_no}: {exc}")
        return Response({
            "message": "CSV processing completed.",
            "created": created, "skipped_duplicates": skipped, "errors": errors,
        }, status=201)
    except UnicodeDecodeError:
        return Response({"error": "CSV must be UTF-8 encoded."}, status=400)

@api_view(["GET"])
def hotspots_list(request):
    latest = AnalysisRun.objects.order_by("-created_at").first()
    if not latest:
        return Response([])
    qs = Hotspot.objects.filter(analysis_run=latest)
    return Response(HotspotSerializer(qs, many=True).data)

@api_view(["POST"])
def run_analysis(request):
    try:
        run = run_hotspot_analysis(request.data.get("dataset_name", "Uploaded CSV"))
        return Response({
            "message": "Hotspot analysis completed.",
            "analysis_id": run.id,
            "records_processed": run.records_processed,
            "hotspots_found": run.hotspots_found,
        })
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)

@api_view(["GET"])
def dashboard(request):
    total = Accident.objects.count()
    severe = Accident.objects.filter(severity__iregex=r"^(serious|severe|fatal)$").count()
    latest = AnalysisRun.objects.order_by("-created_at").first()
    hotspot_count = latest.hotspots_found if latest else 0
    by_severity = list(Accident.objects.values("severity").annotate(count=Count("id")).order_by("-count"))
    by_month = []
    # Keep the API lightweight; React can display the available severity summary.
    return Response({
        "total_accidents": total,
        "serious_or_fatal": severe,
        "hotspot_count": hotspot_count,
        "last_analysis": latest.created_at if latest else None,
        "by_severity": by_severity,
        "by_month": by_month,
    })
