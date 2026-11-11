CREATE DATABASE IF NOT EXISTS road_safety_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE road_safety_db;

-- Django migrations create the tables below. This schema is provided
-- for database-design documentation and manual inspection.
CREATE TABLE IF NOT EXISTS accidents_accident (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  accident_id VARCHAR(80) NOT NULL UNIQUE,
  date DATE NOT NULL,
  time TIME NOT NULL,
  latitude DOUBLE NOT NULL,
  longitude DOUBLE NOT NULL,
  accident_type VARCHAR(100) NOT NULL DEFAULT '',
  severity VARCHAR(30) NOT NULL DEFAULT 'Unknown',
  weather VARCHAR(60) NOT NULL DEFAULT '',
  road_type VARCHAR(60) NOT NULL DEFAULT '',
  vehicle_type VARCHAR(60) NOT NULL DEFAULT '',
  created_at DATETIME(6) NOT NULL
);

CREATE TABLE IF NOT EXISTS accidents_analysisrun (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  algorithm VARCHAR(50) NOT NULL DEFAULT 'DBSCAN',
  dataset_name VARCHAR(255) NOT NULL DEFAULT '',
  records_processed INT UNSIGNED NOT NULL DEFAULT 0,
  hotspots_found INT UNSIGNED NOT NULL DEFAULT 0,
  status VARCHAR(30) NOT NULL DEFAULT 'completed',
  created_at DATETIME(6) NOT NULL
);

CREATE TABLE IF NOT EXISTS accidents_hotspot (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cluster_id INT NOT NULL,
  center_latitude DOUBLE NOT NULL,
  center_longitude DOUBLE NOT NULL,
  accident_count INT UNSIGNED NOT NULL,
  serious_count INT UNSIGNED NOT NULL DEFAULT 0,
  recent_count INT UNSIGNED NOT NULL DEFAULT 0,
  risk_score DOUBLE NOT NULL DEFAULT 0,
  risk_level VARCHAR(20) NOT NULL DEFAULT 'Low',
  analysis_run_id BIGINT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_hotspot_analysis
    FOREIGN KEY (analysis_run_id) REFERENCES accidents_analysisrun(id)
    ON DELETE CASCADE
);
