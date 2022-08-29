locals {
  storage_account_name = replace("${lower("${var.project_name}sa")}", "/[^a-z0-9]/", "")
  feast_registry_name  = "${local.storage_account_name}-feast-registry"
}
