# tiers can be found at https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases
module "db" {
  source  = "../modules/do-postgres"
  tier    = "db-s-1vcpu-2gb"
  size_mb = "61440"
}
