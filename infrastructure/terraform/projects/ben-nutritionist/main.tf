# Ben Nutritionist Project Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  
  backend "gcs" {
    bucket = "terraform-state-bennutritioniste"
    prefix = "agents/ben-nutritionist"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Use the reusable agent module
module "ben_nutritionist" {
  source = "../../modules/agent-service"
  
  agent_name      = "ben-nutritionist"
  project_id      = var.project_id
  region          = var.region
  container_image = var.container_image
  
  environment_vars = {
    OPENAI_API_KEY     = var.openai_api_key
    AGENT_SPECIALIZATION = "nutrition"
    DB_TYPE           = "chromadb"
    LANGUAGE_SUPPORT  = "fr,en"
  }
  
  min_instances = 0
  max_instances = 5
  memory       = "1Gi"
  cpu          = "1"
}

# Agent-specific resources
resource "google_firestore_database" "nutrition_db" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Custom domain mapping (optional)
resource "google_cloud_run_domain_mapping" "nutrition_domain" {
  count    = var.custom_domain != "" ? 1 : 0
  location = var.region
  name     = var.custom_domain

  spec {
    route_name = module.ben_nutritionist.service_name
  }
}