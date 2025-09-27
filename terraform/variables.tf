# Google Cloud Project ID
variable "gcp_project_id" {
  description = "De ID van het Google Cloud Project (bijv. sbotify-470716)."
  type        = string
}

# De naam van de GitHub organisatie en repository.
# Dit moet exact overeenkomen met het pad van uw repository (bijv. bluecitylights/sbotify).
variable "github_org_repo" {
  description = "De organisatie/repository naam (bijv. bluecitylights/sbotify)."
  type        = string
}

# De regio voor de Cloud Run service.
variable "gcp_region" {
  description = "De Google Cloud regio voor de deployment (bijv. europe-west4)."
  type        = string
  default     = "europe-west4"
}
