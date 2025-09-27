locals {
  app_name = "sbotify"
  # Lijst van alle services die een dedicated Service Account nodig hebben voor Cloud Run
  cloud_run_services = ["chat", "dashboard", "mcp-server"]
}

# 1. Definieer de dedicated Service Accounts voor de Cloud Run services.
# Deze worden in de CI/CD gebruikt met de --service-account vlag.
resource "google_service_account" "cloud_run_users" {
  for_each     = toset(local.cloud_run_services)
  project      = var.gcp_project_id
  account_id   = "${local.app_name}-${each.value}-user"
  display_name = "Cloud Run SA for ${title(each.value)} Service"
}

# 2. Geef de CI/CD Service Account de rol 'Service Account User' op elk van 
#    de bovenstaande Cloud Run Service Accounts.
#
#    Dit is de FIX voor de 'iam.serviceaccounts.actAs' PERMISSION_DENIED fout, 
#    waardoor de CI/CD zich mag voordoen als de Cloud Run Service Account.
resource "google_service_account_iam_member" "cicd_sa_impersonation" {
  for_each           = google_service_account.cloud_run_users
  service_account_id = each.value.id
  role               = "roles/iam.serviceAccountUser"
  
  # Leden: De e-mail van de CI/CD Runner Service Account
  # LET OP: Vervang 'google_service_account.github_sa' indien uw CI/CD SA anders heet.
  member             = "serviceAccount:${google_service_account.github_sa.email}"
}
