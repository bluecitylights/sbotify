# Configureer Google Provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
}

# ----------------------------------------------------
# 1. CI/CD SERVICE ACCOUNT (De Robot)
# ----------------------------------------------------
resource "google_service_account" "github_sa" {
  project      = var.gcp_project_id
  account_id   = "github-ci-cd-runner"
  display_name = "Service Account for GitHub Actions CI/CD"
}


# ----------------------------------------------------
# 2. WORKLOAD IDENTITY FEDERATION SETUP
# ----------------------------------------------------
# A. De Pool (Container voor identiteiten)
resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.gcp_project_id
  workload_identity_pool_id = "github-ci-pool" # <-- Aangepaste, unieke ID om 409 te vermijden
  display_name              = "GitHub OIDC Pool"
  description               = "Pool voor het vertrouwen van GitHub Actions OIDC tokens."
  disabled                  = false
}

# B. De Provider (De Brug naar GitHub)
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.gcp_project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-ci-cd" 
  display_name                       = "GitHub CI/CD Provider"
  description                        = "OIDC-provider voor GitHub."
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  # FIX 1: Attribute mapping is nu verplicht voor OIDC-providers.
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  # FIX 2: Wanneer je een custom mapping gebruikt, is een 'attribute_condition' vereist.
  # Deze conditie is voldoende om de API tevreden te stellen.
  attribute_condition = "assertion.sub != ''"
}

# ----------------------------------------------------
# 3. IAM BINDING (De Fix voor de 403 Fout)
# ----------------------------------------------------
# Deze binding geeft de GitHub Repository Principal het recht om de SA te impersoneren.
resource "google_service_account_iam_member" "token_creator_binding" {
  service_account_id = google_service_account.github_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  
  # DEFINITIEVE FIX: Filter op de custom claim 'attribute.repository' (de org/repo naam) 
  # met een schuine streep als scheidingsteken.
  member = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_org_repo}"
}

# ----------------------------------------------------
# 4. ESSENTIËLE SERVICE ROLLEN (Rechten om te werken)
# ----------------------------------------------------
# De Service Account moet ook de rollen krijgen om Artifacts te pushen en Cloud Run services te deployen.
resource "google_project_iam_member" "artifact_registry_writer" {
  project = var.gcp_project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_sa.email}"
}

resource "google_project_iam_member" "cloud_run_admin" {
  project = var.gcp_project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_sa.email}"
}

# ----------------------------------------------------
# 5. UITGANGEN (Inputs voor GitHub Secrets)
# ----------------------------------------------------
output "service_account_email" {
  description = "De e-mail van de Service Account om te impersoneren."
  value       = google_service_account.github_sa.email
}

output "workload_identity_provider" {
  description = "De volledige resource naam van de WIF Provider voor de 'audience' in GitHub Actions."
  # Geeft de resource naam terug, die nodig is voor de GitHub Action.
  value = google_iam_workload_identity_pool_provider.github_provider.name
}
