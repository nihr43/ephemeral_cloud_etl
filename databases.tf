variable "pguser" {}
variable "pgpassword" {}

# tiers can be found at https://learn.microsoft.com/en-us/rest/api/postgresql/singleserver/server-based-performance-tier/list
module "dev" {
  name       = "dev"
  source     = "./modules/azure-postgres"
  tier       = "B_Gen5_2"
  storage_mb = 5120
  login      = var.pguser
  password   = var.pgpassword
}
