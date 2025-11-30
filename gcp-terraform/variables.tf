variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region (ex: us-central1)"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "env" {
  description = "Environment tag"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "Full container image URL (Artifact Registry or gcr). Example: us-central1-docker.pkg.dev/<proj>/repo/image:tag"
  type        = string
  default     = ""
}

variable "service_name" {
  type    = string
  default = "instagram-agent"
}

variable "location_firestore" {
  description = "Firestore location (same as region best practice)"
  type        = string
  default     = "us-central"
}

variable "openai_api_key" {
  description = "OpenAI API key for the nutrition assistant"
  type        = string
  sensitive   = true
}
