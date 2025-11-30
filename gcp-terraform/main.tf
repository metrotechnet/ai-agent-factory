########################
# Enable required APIs - APIs are already enabled manually
########################
# resource "google_project_service" "enable_apis" {
#   for_each = toset([
#     "run.googleapis.com",
#     "cloudbuild.googleapis.com",
#     "artifactregistry.googleapis.com",
#     "cloudscheduler.googleapis.com",
#     "storage.googleapis.com",
#     "firestore.googleapis.com",
#     "iam.googleapis.com",
#     "pubsub.googleapis.com"
#   ])
#   service = each.key
#   disable_on_destroy = false
# }

########################
# Service Account
########################
resource "google_service_account" "sa" {
  account_id   = "${var.service_name}-${var.env}-sa"
  display_name = "Service account for ${var.service_name}"
}

########################
# IAM: Give SA basic roles for Cloud Run / storage / pubsub / cloudbuild
########################
resource "google_project_iam_member" "sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "sa_pubsub_admin" {
  project = var.project_id
  role    = "roles/pubsub.editor"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_project_iam_member" "sa_cloudbuild_service" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

########################
# GCS bucket for videos/transcripts
########################
resource "google_storage_bucket" "videos_bucket" {
  name          = "${var.project_id}-${var.env}-videos"
  location      = var.region
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}

########################
# Artifact Registry (Docker repo)
########################
resource "google_artifact_registry_repository" "docker_repo" {
  provider = google-beta
  repository_id = "${var.project_id}-docker-repo"
  location      = var.region
  format        = "DOCKER"
  description   = "Artifact Registry for containers"
}

########################
# Firestore (Native mode) - one-time creation
########################
resource "google_firestore_database" "default" {
  name     = "(default)"
  location_id = var.location_firestore
  type     = "FIRESTORE_NATIVE"
}

########################
# Cloud Run service (deployed from image)
########################
resource "google_cloud_run_service" "service" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.container_image
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.videos_bucket.name
        }
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }
      }

      service_account_name = google_service_account.sa.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# Allow unauthenticated invocation (optional — remove for private)
resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_service.service.location
  project  = var.project_id
  service  = google_cloud_run_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

########################
# Cloud Scheduler job -> triggers Cloud Run via HTTP OIDC token
########################
resource "google_cloud_scheduler_job" "scheduler_job" {
  name             = "${var.service_name}-ingest-job"
  description      = "Trigger pipeline job on Cloud Run"
  schedule         = "0 */6 * * *" # every 6 hours (modify as needed)
  time_zone        = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_service.service.status[0].url}/update" 
    oidc_token {
      service_account_email = google_service_account.sa.email
      audience              = "https://${google_cloud_run_service.service.status[0].url}"
    }
  }
}

########################
# Outputs
########################
output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_service.service.status[0].url
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.docker_repo.name
}

output "gcs_bucket" {
  value = google_storage_bucket.videos_bucket.name
}
