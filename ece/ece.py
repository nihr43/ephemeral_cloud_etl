import argparse
import subprocess
import os
import json
from jinja2 import Environment, FileSystemLoader


def run_cmd(cmd):
    err = subprocess.call(cmd, shell=True)
    if err != 0:
        raise RuntimeError("command `{}` failed".format(cmd))


class Database:
    """
    creating a Database object does not create a database,
    rather database objects are created from tofu state dict.
    see tofu show --json | jq .values.root_module.child_modules[].resources[]
    """

    def __init__(self, meta_dict):
        self.provider = "digitalocean"
        self.name = meta_dict["name"]
        self.host = meta_dict["host"]
        self.port = meta_dict["port"]
        self.user = meta_dict["user"]
        self.password = meta_dict["password"]
        self.database = meta_dict["database"]

        print("found database {}".format(self.name))

    def get_login_hint(self):
        print("\nLog into {} with:".format(self.name))
        print(
            "PGPASSWORD={} psql -h {} -p {} -U {} -d {}".format(
                self.password, self.host, self.port, self.user, self.database
            )
        )
        print("\nOr run dbt with:\ndbt build --project-dir etl --profiles-dir etl")


def parse_databases():
    # inspects tfstate, returns list of Databases
    databases = []
    tofushow = subprocess.run(
        ["tofu", "show", "-json"], check=True, capture_output=True
    )
    state = json.loads(tofushow.stdout)
    try:
        for j in state["values"]["root_module"]["child_modules"]:
            for i in j["resources"]:
                if "digitalocean_database_cluster" in i["address"]:
                    db = Database(i["values"])
                    databases.append(db)
    except KeyError:
        print("no resources found")
    return databases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destroy", "--cleanup", action="store_true", help="delete all resources"
    )
    parser.add_argument(
        "--login-hint", action="store_true", help="print copy-paste login command"
    )
    args = parser.parse_args()

    if "TF_VAR_do_token" not in os.environ:
        raise ValueError("Environment variable TF_VAR_do_token required")

    if args.destroy:
        run_cmd("tofu destroy --auto-approve")
        return
    else:
        run_cmd("tofu apply --auto-approve")

    databases = parse_databases()

    if args.login_hint:
        for i in databases:
            i.get_login_hint()

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("profiles.yml.j2")
    with open("etl/profiles.yml", "w") as profile:
        profile.truncate()
        profile.write(
            template.render(database=databases[0])
        )  # todo: handle more than one?
