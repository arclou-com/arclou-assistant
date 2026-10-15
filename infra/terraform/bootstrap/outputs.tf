output "project_ids" {
  description = "IDs dos projetos por ambiente"
  value       = { for k, p in google_project.this : k => p.project_id }
}

output "project_numbers" {
  value = { for k, p in google_project.this : k => p.number }
}

output "tfstate_bucket" {
  description = "Bucket do state remoto (use em backend \"gcs\")"
  value       = google_storage_bucket.tfstate.name
}
