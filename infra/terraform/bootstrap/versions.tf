terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.10"
    }
  }
}

provider "google" {
  region = var.region
}

# Budgets API exige um projeto de cota: usamos o de produção criado aqui mesmo.
provider "google" {
  alias                 = "billing"
  region                = var.region
  user_project_override = true
  billing_project       = local.projects.prd.id
}
