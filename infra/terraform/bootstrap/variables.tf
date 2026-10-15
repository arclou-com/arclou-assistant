variable "org_id" {
  description = "ID da organização (arclouai-org)"
  type        = string
}

variable "billing_account" {
  description = "Conta de billing ligada aos projetos"
  type        = string
}

variable "region" {
  description = "Região padrão de tudo"
  type        = string
  default     = "southamerica-east1"
}

variable "project_id_suffix" {
  description = "Sufixo dos IDs de projeto, se arclou-stg/arclou-prd estiverem ocupados (ex.: \"-7k2q\")"
  type        = string
  default     = ""
}

variable "budget_amount" {
  description = "Orçamento mensal da conta de billing, na moeda dela (BRL)"
  type        = number
  default     = 350
}

variable "budget_currency" {
  description = "Moeda da conta de billing"
  type        = string
  default     = "BRL"
}
