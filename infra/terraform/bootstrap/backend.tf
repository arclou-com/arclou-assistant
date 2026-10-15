# Criado pelo próprio bootstrap. No primeiro apply, comente este bloco, aplique e rode:
#   terraform init -migrate-state
terraform {
  backend "gcs" {
    bucket = "arclou-prd-tfstate"
    prefix = "bootstrap"
  }
}
