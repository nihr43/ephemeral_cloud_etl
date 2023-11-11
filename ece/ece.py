import argparse
import subprocess
import os
import json
from time import sleep
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine, MetaData


def run_cmd(cmd):
    err = subprocess.call(cmd, shell=True)
    if err != 0:
        raise RuntimeError("command `{}` failed".format(cmd))


class Database:
    """
    creating a Database object does not create a database,
    rather database objects are created from tofu state dict.
    see tofu show --json | jq .values.root_module.child_modules[].resources[]
    rnd_context is the module.db.random_id.context b64_url for ues when importing
    the instance into production without having the id re-ggenerated
    """

    def __init__(self, meta_dict, rnd_context):
        self.provider = "digitalocean"
        self.id = meta_dict["id"]
        self.name = meta_dict["name"]
        self.host = meta_dict["host"]
        self.port = meta_dict["port"]
        self.user = meta_dict["user"]
        self.password = meta_dict["password"]
        self.database = meta_dict["database"]
        self.context = rnd_context

        print("found database {}".format(self.name))

    def get_login_hint(self):
        print("\nLog into {} with:".format(self.name))
        print(
            "PGPASSWORD={} psql -h {} -p {} -U {} -d {}".format(
                self.password, self.host, self.port, self.user, self.database
            )
        )

        print("\nSee pg_activity with:")
        print(
            "PGPASSWORD={} pg_activity -h {} -p {} -U {} -d {}".format(
                self.password, self.host, self.port, self.user, self.database
            )
        )

        print("\nRun dbt with:\ndbt build --project-dir etl --profiles-dir etl")

    def wait_ready(self):
        """
        immediately after a database is created, it can take a minute to be reachable over the internet
        """
        psql = "postgresql://{}:{}@{}:{}/{}".format(
            self.user, self.password, self.host, self.port, self.database
        )
        engine = create_engine(psql)
        i = 0
        while i < 60:
            try:
                metadata = MetaData()
                metadata.reflect(bind=engine)
            except:
                print("waiting for {} to become ready".format(self.host))
                sleep(10)
                i += 1
            else:
                print("{} ready".format(self.host))
                break
            finally:
                engine.dispose()

    def stage(self):
        """
        for each csv found under staging/, check if a corresponding table exists.
        if no table exists, execute the associated .sql.  (patients.csv is loaded by patients.sql)
        """
        files = os.listdir("staging")
        csvs = [f for f in files if f.endswith(".csv")]
        self.wait_ready()
        try:
            psql = "postgresql://{}:{}@{}:{}/{}".format(
                self.user, self.password, self.host, self.port, self.database
            )
            engine = create_engine(psql)
            metadata = MetaData()
            metadata.reflect(bind=engine)
            for c in csvs:
                table = c.removesuffix(".csv")
                if table not in metadata.tables:
                    print("{} does not exist.  creating...".format(table))
                    run_cmd(
                        "PGPASSWORD={} psql -h {} -p {} -U {} -d {} -f staging/{}.sql".format(
                            self.password,
                            self.host,
                            self.port,
                            self.user,
                            self.database,
                            table,
                        )
                    )
        finally:
            if engine:
                engine.dispose()

    @staticmethod
    def dbt():
        run_cmd("dbt build --project-dir etl --profiles-dir etl")

    def publish(self):
        # import resources into production state:
        run_cmd("tofu -chdir=prod destroy")
        run_cmd(
            "tofu -chdir=prod import module.db.random_id.context {}".format(
                self.context
            )
        )
        run_cmd(
            "tofu -chdir=prod import module.db.digitalocean_database_cluster.etl {}".format(
                self.id
            )
        )
        run_cmd("tofu -chdir=prod apply")

        # remove resources from dev state
        run_cmd("tofu state rm module.db.random_id.context")
        run_cmd("tofu state rm module.db.digitalocean_database_cluster.etl")


def parse_databases():
    # inspects tfstate, returns a Database
    tofushow = subprocess.run(
        ["tofu", "show", "-json"], check=True, capture_output=True
    )
    state = json.loads(tofushow.stdout)
    try:
        for j in state["values"]["root_module"]["child_modules"]:
            for i in j["resources"]:
                if i["address"] == "module.db.digitalocean_database_cluster.etl":
                    db_meta = i["values"]
                if i["address"] == "module.db.random_id.context":
                    rnd_context = i["values"]["b64_url"]

        db = Database(db_meta, rnd_context)

    except KeyError:
        print("no resources found")
    return db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destroy", "--cleanup", action="store_true", help="delete all resources"
    )
    parser.add_argument(
        "--hints", action="store_true", help="print copy-paste login and dbt commands"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="transfer current working state to production",
    )
    args = parser.parse_args()

    if "TF_VAR_do_token" not in os.environ:
        raise ValueError("Environment variable TF_VAR_do_token required")

    if args.destroy:
        run_cmd("tofu destroy --auto-approve")
        return
    else:
        run_cmd("tofu apply --auto-approve")

    database = parse_databases()

    if args.publish:
        database.publish()
        return

    if args.hints:
        database.get_login_hint()
        return

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("profiles.yml.j2")
    with open("etl/profiles.yml", "w") as profile:
        profile.truncate()
        profile.write(template.render(database=database))

    database.stage()
    database.dbt()
