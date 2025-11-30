# Fitness Coach Agent Configuration
module "fitness_coach" {
  source = "../../modules/agent-service"
  
  agent_name      = "fitness-coach"
  project_id      = var.project_id
  region          = var.region
  container_image = var.container_image
  
  environment_vars = {
    OPENAI_API_KEY       = var.openai_api_key
    AGENT_SPECIALIZATION = "fitness"
    DB_TYPE             = "pinecone"  # Different vector DB
    LANGUAGE_SUPPORT    = "en"
    FITNESS_API_KEY     = var.fitness_api_key
  }
  
  min_instances = 1  # Keep 1 instance warm for fitness tracking
  max_instances = 15 # Higher scale for workout sessions
  memory       = "2Gi" # More memory for workout data
  cpu          = "2"
}

# Fitness-specific resources
resource "google_storage_bucket" "workout_plans" {
  name     = "${var.project_id}-workout-plans"
  location = var.region
}

resource "google_cloud_scheduler_job" "daily_fitness_tips" {
  name        = "daily-fitness-tips"
  description = "Send daily fitness tips"
  schedule    = "0 8 * * *"  # 8 AM daily
  time_zone   = "America/New_York"
  
  http_target {
    uri         = "${module.fitness_coach.service_url}/daily-tip"
    http_method = "POST"
  }
}