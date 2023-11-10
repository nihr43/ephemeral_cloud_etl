variable "name" {}
variable "tier" {}

terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "2.32.0"
    }
  }
}

resource "digitalocean_database_db" "etl" {
  cluster_id = digitalocean_database_cluster.etl.id
  name       = "dbt"
}

resource "digitalocean_database_cluster" "etl" {
  name       = "etl-pgsql-${var.name}"
  engine     = "pg"
  version    = 15
  size       = var.tier
  region     = "nyc1"
  node_count = 1
}