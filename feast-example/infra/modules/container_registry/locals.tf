locals {
  container_registry_name = replace("${lower("${var.project_name}cr")}", "/[^a-z0-9]/", "")
}
