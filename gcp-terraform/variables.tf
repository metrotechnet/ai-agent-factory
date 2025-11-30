variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region (ex: us-east4)"
  type        = string
  default     = "us-east4"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-east4-a"
}

variable "env" {
  description = "Environment tag"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "Full container image URL (Artifact Registry or gcr). Example: us-east4-docker.pkg.dev/<proj>/repo/image:tag"
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
  default     = "us-east4"
}

variable "openai_api_key" {
  description = "OpenAI API key for the nutrition assistant"
  type        = string
  sensitive   = true
}
