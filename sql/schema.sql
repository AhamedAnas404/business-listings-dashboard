-- LocalLens MySQL 8 schema, generated for the internship assignment.
CREATE DATABASE IF NOT EXISTS business_dashboard
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE business_dashboard;

CREATE TABLE IF NOT EXISTS listing_master (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  business_name VARCHAR(255) NOT NULL,
  category VARCHAR(100) NOT NULL,
  city VARCHAR(100) NOT NULL,
  address TEXT NOT NULL,
  phone VARCHAR(100) DEFAULT NULL,
  source VARCHAR(100) NOT NULL,
  source_ref VARCHAR(128) NOT NULL,
  data_origin VARCHAR(10) NOT NULL DEFAULT 'real',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_listing_source_ref (source_ref),
  INDEX ix_listing_master_category (category),
  INDEX ix_listing_master_city (city),
  INDEX ix_listing_master_source (source),
  INDEX ix_listing_master_data_origin (data_origin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
