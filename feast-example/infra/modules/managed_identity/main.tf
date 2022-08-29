terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_user_assigned_identity" "managed_identity" {
  name                = local.managed_identity_name
  resource_group_name = var.resource_group_name
  location            = var.location

  tags = var.resource_tags
}
