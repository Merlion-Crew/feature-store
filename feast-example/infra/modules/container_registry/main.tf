terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_container_registry" "container_registry" {
  name                = local.container_registry_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
}

data "azurerm_subscription" "subscription" {
}

data "azurerm_role_definition" "contributor" {
  name  = "Contributor"
  scope = data.azurerm_subscription.subscription.id
}

resource "azurerm_role_assignment" "contributor_to_managed_identity" {
  scope              = azurerm_container_registry.container_registry.id
  role_definition_id = data.azurerm_role_definition.contributor.id
  principal_id       = var.managed_identity_principal_id
}
