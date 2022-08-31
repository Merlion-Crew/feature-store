terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_resource_group" "resource_group" {
  name     = local.resource_group_name
  location = var.location

  tags = var.resource_tags
}

