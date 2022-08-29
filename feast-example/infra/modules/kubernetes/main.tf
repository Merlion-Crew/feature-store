terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

data "azurerm_subscription" "subscription" {
}

data "azurerm_role_definition" "contributer" {
  name  = "Contributor"
  scope = data.azurerm_subscription.subscription.id
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = local.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = local.cluster_name

  default_node_pool {
    name       = "default"
    node_count = var.default_node_pool_node_count
    vm_size    = var.default_node_pool_vm_size
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_id]
  }

  tags = var.resource_tags
}

resource "azurerm_role_assignment" "cluster_contributor_to_managed_identity" {
  scope              = azurerm_kubernetes_cluster.cluster.id
  role_definition_id = data.azurerm_role_definition.contributer.id
  principal_id       = var.managed_identity_principal_id
}
