# Reusable Agent Service Module
variable "agent_name" {
  description = "Name of the AI agent (e.g., ben-nutritionist)"
  type        = string
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-east4"
}

variable "container_image" {
  description = "Docker image URL"
  type        = string
}

variable "environment_vars" {
  description = "Environment variables for the service"
  type        = map(string)
  default     = {}
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "1Gi"
}

variable "cpu" {
  description = "CPU allocation"
  type        = string
  default     = "1"
}

# Service Account for the agent
resource "google_service_account" "agent_sa" {
  account_id   = "${var.agent_name}-sa"
  display_name = "${title(var.agent_name)} Service Account"
  project      = var.project_id
}

# Storage bucket for agent-specific data
resource "google_storage_bucket" "agent_data" {
  name     = "${var.project_id}-${var.agent_name}-data"
  location = var.region
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Cloud Run Service
resource "google_cloud_run_service" "agent_service" {
  name     = var.agent_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.container_image
        
        # Base environment variables
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "AGENT_NAME"
          value = var.agent_name
        }
        
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.agent_data.name
        }
        
        # Custom environment variables
        dynamic "env" {
          for_each = var.environment_vars
          content {
            name  = env.key
            value = env.value
          }
        }
        
        resources {
          limits = {
            memory = var.memory
            cpu    = var.cpu
          }
        }
      }
      
      container_concurrency = 80
      timeout_seconds      = 300
      service_account_name = google_service_account.agent_sa.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.min_instances
        "autoscaling.knative.dev/maxScale" = var.max_instances
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_service.agent_service.location
  project  = google_cloud_run_service.agent_service.project
  service  = google_cloud_run_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM permissions
resource "google_project_iam_member" "agent_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

resource "google_project_iam_member" "agent_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Outputs
output "service_url" {
  value = google_cloud_run_service.agent_service.status[0].url
}

output "service_account_email" {
  value = google_service_account.agent_sa.email
}

output "bucket_name" {
  value = google_storage_bucket.agent_data.name
}