# tiers can be found at https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases
module "dev" {
  name    = "dev"
  source  = "./modules/do-postgres"
  tier    = "db-s-2vcpu-4gb"
  size_mb = "61440"
}
