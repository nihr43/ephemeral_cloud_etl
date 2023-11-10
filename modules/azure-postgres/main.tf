variable "name" {}
variable "tier" {}
variable "login" {}
variable "password" {}
variable "storage_mb" {}

resource "azurerm_resource_group" "etl" {
  name     = "api-rg-${var.name}"
  location = "East US"
}

resource "azurerm_postgresql_server" "etl" {
  name                = "pgsql-${var.name}"
  location = "East US"
  location            = azurerm_resource_group.etl.location
  resource_group_name = azurerm_resource_group.etl.name
  sku_name = var.tier
  storage_mb                   = var.storage_mb
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = var.login
  administrator_login_password = var.password
  version                      = "11"
  ssl_enforcement_enabled      = true
}

resource "azurerm_postgresql_database" "etl" {
  name                = "dbt"
  resource_group_name = azurerm_resource_group.etl.name
  server_name         = azurerm_postgresql_server.etl.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}
