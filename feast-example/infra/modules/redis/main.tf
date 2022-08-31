terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_redis_cache" "redis" {
  name                = local.redis_name
  location            = var.location
  resource_group_name = var.resource_group_name
  capacity            = var.capacity
  family              = var.family
  sku_name            = var.sku
  enable_non_ssl_port = true
  minimum_tls_version = "1.2"
  redis_version       = 6

  tags = var.resource_tags
}

data "azurerm_subscription" "subscription" {
}

data "azurerm_role_definition" "contributor" {
  name  = "Contributor"
  scope = data.azurerm_subscription.subscription.id
}

resource "azurerm_role_assignment" "contributor_to_managed_identity" {
  scope              = azurerm_redis_cache.redis.id
  role_definition_id = data.azurerm_role_definition.contributor.id
  principal_id       = var.managed_identity_principal_id
}
