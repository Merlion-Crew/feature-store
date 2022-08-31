terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.12.0"
    }
  }

  required_version = ">= 1.1.0"
}

resource "azurerm_virtual_network" "internal_vnet" {
  name                = local.vnet_name
  address_space       = var.internal_subnet_vnet_address_space
  location            = var.location
  resource_group_name = var.resource_group_name
}

resource "azurerm_subnet" "internal_subnet" {
  name                 = local.subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.internal_vnet.name
  address_prefixes     = var.internal_subnet_address_prefixes
}

resource "azurerm_network_interface" "nic" {
  name                = local.network_interface_name
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.internal_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}
