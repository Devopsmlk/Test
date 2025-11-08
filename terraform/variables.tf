variable "resource_group_name" {
  default = "rg-qashqade-test"
}

variable "location" {
  default = "francecentral"
}

variable "acr_name" {
  default = "acrqashqade"
}

variable "aks_name" {
  default = "aks-qashqade"
}

variable "postgres_name" {
  default = "postgres-qashqade"
}

variable "db_admin_username" {
  default = "qashqadeadmin"
}

variable "db_admin_password" {
  default = "YourSecureP@ssw0rd!"
  sensitive = true
}

variable "node_count" {
  default = 2
}