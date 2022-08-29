terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

data "azurerm_client_config" "current" {
}

resource "azurerm_key_vault" "key_vault" {
  name                = local.key_vault_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = var.sku
  tenant_id           = data.azurerm_client_config.current.tenant_id

  tags = var.resource_tags

  // Do not add access_policy blocks here, as they will conflict with additional
  // azurerm_key_vault_access_policy resources created afterwards (in the same or
  // different modules).
}

resource "azurerm_key_vault_access_policy" "key_vault_access_policy" {
  key_vault_id = azurerm_key_vault.key_vault.id
  tenant_id    = var.managed_identity_tenant_id
  object_id    = var.managed_identity_principal_id

  key_permissions    = ["Get", "List"]
  secret_permissions = ["Get", "List"]
}
