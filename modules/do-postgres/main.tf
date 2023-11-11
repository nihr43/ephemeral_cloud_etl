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

resource "digitalocean_kubernetes_cluster" "data-apps" {
  name   = "foo"
  region = "nyc1"
  version = "1.28.2-do.0"
  node_pool {
    name       = "worker-pool"
    size       = "s-1vcpu-2gb"
    node_count = 1
  }
}

provider "kubernetes" {
  host  = digitalocean_kubernetes_cluster.data-apps.endpoint
  token = digitalocean_kubernetes_cluster.data-apps.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.data-apps.kube_config[0].cluster_ca_certificate
  )
}

resource "kubernetes_deployment" "pgweb" {
  depends_on = [digitalocean_kubernetes_cluster.data-apps, digitalocean_database_cluster.etl]
  metadata {
    name = "pgweb"
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "pgweb"
      }
    }
    template {
      metadata {
        labels = {
          app = "pgweb"
        }
      }
      spec {
        container {
          image = "sosedoff/pgweb"
          name  = "pgweb"
          env {
            name  = "PGWEB_DATABASE_URL"
            value = "postgres://${digitalocean_database_cluster.etl.user}:${digitalocean_database_cluster.etl.password}@${digitalocean_database_cluster.etl.private_host}:${digitalocean_database_cluster.etl.port}/${digitalocean_database_cluster.etl.database}"
          }
        }
      }
    }
  }
}
