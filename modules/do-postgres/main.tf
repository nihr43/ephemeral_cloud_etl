variable "name" {}
variable "tier" {}

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
