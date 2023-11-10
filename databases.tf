# tiers can be found at https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases
module "dev" {
  name     = "dev"
  source   = "./modules/do-postgres"
  tier     = "db-s-1vcpu-1gb"
}
