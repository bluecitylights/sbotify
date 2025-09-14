terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west4"
}

variable "image_tag" {
  description = "The image tag to use for deployments"
  type        = string
  default     = "latest"
}

# Use existing service accounts (no creation needed)
data "google_service_account" "chat" {
  account_id = "sbotify-chat-user"
  project    = var.project_id
}

data "google_service_account" "dashboard" {
  account_id = "sbotify-dashboard-user"
  project    = var.project_id
}

data "google_service_account" "mcp_server" {
  account_id = "sbotify-mcp-server-user"
  project    = var.project_id
}

# VPC Connector
data "google_vpc_access_connector" "sbotify_connector" {
  name    = "sbotify-connector"
  region  = var.region
  project = var.project_id
}

# Cloud Run Services
resource "google_cloud_run_service" "chat" {
  name     = "sbotify-chat"
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "1"
        "run.googleapis.com/vpc-access-connector" = data.google_vpc_access_connector.sbotify_connector.id
        "run.googleapis.com/vpc-access-egress"    = "all-traffic"
      }
    }

    spec {
      service_account_name = data.google_service_account.chat.email
      containers {
        image = "europe-west4-docker.pkg.dev/${var.project_id}/sbotify/chat:${var.image_tag}"
        ports {
          container_port = 8080
        }
        env {
          name  = "MCP_SERVER_URL"
          value = google_cloud_run_service.mcp_server.status[0].url
        }
        # Keep existing GEMINI_API_KEY from Secret Manager (handled by your current setup)
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal"
    }
  }
}

resource "google_cloud_run_service" "dashboard" {
  name     = "sbotify-dashboard"
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "1"
        "run.googleapis.com/vpc-access-connector" = data.google_vpc_access_connector.sbotify_connector.id
        "run.googleapis.com/vpc-access-egress"    = "all-traffic"
      }
    }

    spec {
      service_account_name = data.google_service_account.dashboard.email
      containers {
        image = "europe-west4-docker.pkg.dev/${var.project_id}/sbotify/dashboard:${var.image_tag}"
        ports {
          container_port = 8080
        }
        env {
          name  = "CHAT_API_URL"
          value = google_cloud_run_service.chat.status[0].url
        }
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal"
    }
  }
}

resource "google_cloud_run_service" "mcp_server" {
  name     = "sbotify-mcp-server"
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "1"
        "run.googleapis.com/vpc-access-connector" = data.google_vpc_access_connector.sbotify_connector.id
        "run.googleapis.com/vpc-access-egress"    = "all-traffic"
      }
    }

    spec {
      service_account_name = data.google_service_account.mcp_server.email
      containers {
        image = "europe-west4-docker.pkg.dev/${var.project_id}/sbotify/mcp-server:${var.image_tag}"
        ports {
          container_port = 8080
        }
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal"
    }
  }
}

# Outputs (match the service names used in substitutions)
output "chat_url" {
  value = google_cloud_run_service.chat.status[0].url
}

output "dashboard_url" {
  value = google_cloud_run_service.dashboard.status[0].url
}

output "mcp_server_url" {
  value = google_cloud_run_service.mcp_server.status[0].url
}

# Alternative output names to match _SERVICE variable
output "chat" {
  value = google_cloud_run_service.chat.status[0].url
}

output "dashboard" {
  value = google_cloud_run_service.dashboard.status[0].url
}

output "mcp-server" {
  value = google_cloud_run_service.mcp_server.status[0].url
}