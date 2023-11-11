import argparse
import subprocess
import os
import json
from time import sleep
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine, MetaData, exc


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

        print("\nSee pg_activity with:")
        print(
            "PGPASSWORD={} pg_activity -h {} -p {} -U {} -d {}".format(
                self.password, self.host, self.port, self.user, self.database
            )
        )

        print("\nOr run dbt with:\ndbt build --project-dir etl --profiles-dir etl")

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
        "--hints", action="store_true", help="print copy-paste login and dbt commands"
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

    if args.hints:
        for i in databases:
            i.get_login_hint()
        return

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("profiles.yml.j2")
    with open("etl/profiles.yml", "w") as profile:
        profile.truncate()
        profile.write(
            template.render(database=databases[0])
        )  # todo: handle more than one?

    databases[0].stage()
    databases[0].dbt()
