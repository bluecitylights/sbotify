# Dit zijn de waardes die u moet kopiëren en in uw GitHub Secrets plakken.

# SECRET: SERVICE_ACCOUNT_EMAIL
output "github_actions_sa_email" {
  description = "De e-mail van de Service Account (voor SERVICE_ACCOUNT_EMAIL secret)."
  value       = google_service_account.github_sa.email
}

# SECRET: WORKLOAD_IDENTITY_PROVIDER
output "github_actions_wif_provider_url" {
  description = "De volledige Workload Identity Provider URL (voor WORKLOAD_IDENTITY_PROVIDER secret)."
  value       = "https://iam.googleapis.com/${google_iam_workload_identity_pool_provider.github_provider.name}"
}

# Voor uw Cloud Run deployment
output "gcp_project_number" {
  description = "Het numerieke projectnummer, nodig voor sommige API-calls."
  value       = data.google_project.project.number
}

data "google_project" "project" {}
