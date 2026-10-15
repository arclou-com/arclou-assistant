locals {
  projects = {
    stg = { id = "arclou-stg${var.project_id_suffix}", name = "Arclou Staging", env = "stg" }
    prd = { id = "arclou-prd${var.project_id_suffix}", name = "Arclou Production", env = "prd" }
  }

  # APIs habilitadas nos dois projetos (doc 12, S0-03)
  services = [
    "compute.googleapis.com",
    "iap.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "firestore.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "aiplatform.googleapis.com",
    "dns.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "storage.googleapis.com",
    "cloudbilling.googleapis.com",
    "billingbudgets.googleapis.com",
  ]

  project_services = {
    for pair in setproduct(keys(local.projects), local.services) :
    "${pair[0]}/${pair[1]}" => { project = pair[0], service = pair[1] }
  }

  labels = { app = "arclou", managed_by = "terraform" }
}

resource "google_project" "this" {
  for_each = local.projects

  project_id      = each.value.id
  name            = each.value.name
  org_id          = var.org_id
  billing_account = var.billing_account
  labels          = merge(local.labels, { env = each.value.env })

  auto_create_network = false
  deletion_policy     = "PREVENT"
}

resource "google_project_service" "this" {
  for_each = local.project_services

  project            = google_project.this[each.value.project].project_id
  service            = each.value.service
  disable_on_destroy = false
}

# State remoto de todos os ambientes (um prefixo por pasta de envs/)
resource "google_storage_bucket" "tfstate" {
  project  = google_project.this["prd"].project_id
  name     = "${google_project.this["prd"].project_id}-tfstate"
  location = var.region
  labels   = merge(local.labels, { env = "shared" })

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 20
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.this]
}

resource "google_billing_budget" "monthly" {
  provider = google.billing

  billing_account = var.billing_account
  display_name    = "Arclou · orçamento mensal"

  budget_filter {
    projects               = [for p in google_project.this : "projects/${p.number}"]
    credit_types_treatment = "INCLUDE_ALL_CREDITS"
  }

  amount {
    specified_amount {
      currency_code = var.budget_currency
      units         = tostring(var.budget_amount)
    }
  }

  # E-mails vão para os admins da conta de billing
  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.9
  }
  threshold_rules {
    threshold_percent = 1.0
  }
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }

  depends_on = [google_project_service.this]
}
