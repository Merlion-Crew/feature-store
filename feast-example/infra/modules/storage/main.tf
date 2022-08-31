terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_storage_account" "storage_account" {
  name                     = local.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = var.tier
  account_replication_type = var.replication_type

  tags = var.resource_tags
}

resource "azurerm_storage_container" "feast_registry" {
  name                 = local.feast_registry_name
  storage_account_name = azurerm_storage_account.storage_account.name
}

data "azurerm_subscription" "subscription" {
}

data "azurerm_role_definition" "storage_blob_data_contributor" {
  name  = "Storage Blob Data Contributor"
  scope = data.azurerm_subscription.subscription.id
}

resource "azurerm_role_assignment" "storage_blob_data_contributor_to_managed_identity" {
  scope              = azurerm_storage_account.storage_account.id
  role_definition_id = data.azurerm_role_definition.storage_blob_data_contributor.id
  principal_id       = var.managed_identity_principal_id
}
