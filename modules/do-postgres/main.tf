variable "tier" {}
variable "size_mb" {}

terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "2.32.0"
    }
  }
}

resource "random_id" "context" {
  byte_length = 4
}

resource "digitalocean_database_cluster" "etl" {
  name       = "dbt-pgsql-${random_id.context.hex}"
  engine     = "pg"
  version    = 15
  size       = var.tier
  region     = "nyc1"
  node_count = 1
  storage_size_mib = var.size_mb
}
