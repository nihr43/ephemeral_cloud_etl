# ece

This is a platform for developing, running, and publishing a [dbt](https://docs.getdbt.com/docs/introduction) etl project on ephemeral cloud infrastructure.

This provides a fully reproducible, self-service, cost-effective, cost-accountable means of working with such a codebase.

In short, `ece` deploys a postgres database (defined in `databases.tf`), stages some static data, templates out a dbt connection profile, and runs dbt.  A kubernetes cluster is deployed as well for our data-centric apps, with an example [pgweb](https://sosedoff.github.io/pgweb/) deployment that is automatically tapped into the database.  All this allows developers to provision infrastructure and do iterative etl development in isolation (on whatever hardware is deemed cost-effective) - but when a user is satisfied with the state of their current working environment, they can move it all to 'production' with `--publish`.

There are many positive side-affects in making these abstractions:

- we can run etl on fast, expensive instances, and immediately publish to something cheaper.
- full reproducibility.
- triviality of experimentation.
- secure by default.  all credentials are randomly generated every time the infrastructure is provisioned.
- no resource sharing between developers.

This work is presented on DigitalOcean infrastructure, but could be transferred to any cloud provider.

## usage

```
python3 ece -h
usage: ece [-h] [--destroy] [--hints] [--publish]

options:
  -h, --help            show this help message and exit
  --destroy, --cleanup  delete all resources
  --hints               print copy-paste login and dbt commands
  --publish             transfer current working state to production
```

The default action is to enforce infrastructure state and run `dbt build`:

```
(venv) ~/git/ephemeral_cloud_etl$ python3 ece

OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

OpenTofu will perform the following actions:

  -- diff tuncated --
  # module.db.digitalocean_database_cluster.etl will be created
  # module.db.digitalocean_kubernetes_cluster.data-apps will be created
  # module.db.kubernetes_deployment.pgweb will be created
  # module.db.random_id.context will be created

Plan: 4 to add, 0 to change, 0 to destroy.
module.db.random_id.context: Creating...
module.db.random_id.context: Creation complete after 0s [id=uiznCQ]
module.db.digitalocean_kubernetes_cluster.data-apps: Creating...
module.db.digitalocean_database_cluster.etl: Creating...
module.db.digitalocean_kubernetes_cluster.data-apps: Creation complete after 4m12s [id=a85a8a04-eadf-49ee-b867-0d41a906711d]
module.db.digitalocean_database_cluster.etl: Creation complete after 4m33s [id=4273ad9b-a966-48e9-9eb6-20571fada70e]
module.db.kubernetes_deployment.pgweb: Creating...
module.db.kubernetes_deployment.pgweb: Still creating... [10s elapsed]
module.db.kubernetes_deployment.pgweb: Creation complete after 16s [id=default/pgweb]

Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
found database dbt-pgsql-ba2ce709
dbt-pgsql-ba2ce709-do-user-1228802-0.c.db.ondigitalocean.com ready
patients does not exist.  creating...
CREATE TABLE
COPY 10000000
icd10 does not exist.  creating...
CREATE TABLE
COPY 71704
providers does not exist.  creating...
CREATE TABLE
COPY 8026546
diagnoses does not exist.  creating...
CREATE TABLE
COPY 100000000
04:18:38  Running with dbt=1.7.1
04:18:38  Registered adapter: postgres=1.7.1
04:18:38  Unable to do partial parsing because profile has changed
04:18:39  [WARNING]: Configuration paths exist in your dbt_project.yml file which do not apply to any resources.
There are 1 unused configuration paths:
- models.etl.example
04:18:39  Found 5 models, 10 tests, 4 sources, 0 exposures, 0 metrics, 401 macros, 0 groups, 0 semantic models
04:18:39  
04:18:40  Concurrency: 10 threads (target='dev')
04:18:40  
04:18:40  1 of 15 START sql table model public.distinct_patients ......................... [RUN]
04:18:40  2 of 15 START sql table model public.distinct_providers ........................ [RUN]
04:18:40  3 of 15 START sql table model public.female_patients ........................... [RUN]
04:18:40  4 of 15 START sql table model public.male_patients ............................. [RUN]
04:18:40  5 of 15 START sql table model public.observed_diagnoses ........................ [RUN]
04:20:25  3 of 15 OK created sql table model public.female_patients ...................... [SELECT 5001021 in 104.32s]
04:20:25  6 of 15 START test not_null_female_patients_patid .............................. [RUN]
04:20:25  7 of 15 START test unique_female_patients_patid ................................ [RUN]
04:20:27  4 of 15 OK created sql table model public.male_patients ........................ [SELECT 4998979 in 106.47s]
04:20:27  8 of 15 START test not_null_male_patients_patid ................................ [RUN]
04:20:27  9 of 15 START test unique_male_patients_patid .................................. [RUN]
04:20:31  6 of 15 PASS not_null_female_patients_patid .................................... [PASS in 6.49s]
04:20:40  8 of 15 PASS not_null_male_patients_patid ...................................... [PASS in 13.09s]
04:21:28  7 of 15 PASS unique_female_patients_patid ...................................... [PASS in 63.01s]
04:21:43  1 of 15 OK created sql table model public.distinct_patients .................... [SELECT 10000000 in 182.56s]
04:21:43  10 of 15 START test not_null_distinct_patients_patid ........................... [RUN]
04:21:43  11 of 15 START test unique_distinct_patients_patid ............................. [RUN]
04:21:59  10 of 15 PASS not_null_distinct_patients_patid ................................. [PASS in 16.04s]
04:22:30  9 of 15 PASS unique_male_patients_patid ........................................ [PASS in 123.61s]
04:23:14  11 of 15 PASS unique_distinct_patients_patid ................................... [PASS in 91.18s]
04:28:37  5 of 15 OK created sql table model public.observed_diagnoses ................... [SELECT 71704 in 596.31s]
04:28:37  12 of 15 START test not_null_observed_diagnoses_dx_code ........................ [RUN]
04:28:37  13 of 15 START test unique_observed_diagnoses_dx_code .......................... [RUN]
04:28:37  12 of 15 PASS not_null_observed_diagnoses_dx_code .............................. [PASS in 0.40s]
04:28:37  13 of 15 PASS unique_observed_diagnoses_dx_code ................................ [PASS in 0.48s]
04:28:49  2 of 15 OK created sql table model public.distinct_providers ................... [SELECT 6104471 in 608.50s]
04:28:49  14 of 15 START test not_null_distinct_providers_npi ............................ [RUN]
04:28:49  15 of 15 START test unique_distinct_providers_npi .............................. [RUN]
04:28:52  14 of 15 PASS not_null_distinct_providers_npi .................................. [PASS in 2.82s]
04:29:05  15 of 15 PASS unique_distinct_providers_npi .................................... [PASS in 15.74s]
04:29:05  
04:29:05  Finished running 5 table models, 10 tests in 0 hours 10 minutes and 26.08 seconds (626.08s).
04:29:05  
04:29:05  Completed successfully
04:29:05  
04:29:05  Done. PASS=15 WARN=0 ERROR=0 SKIP=0 TOTAL=15
```

At any stage in the process, the user is free to use the underlying tools independently of the abstraction `ece` provides.  For example, once the infrastructure is provisioned, one can freely cd into the dbt project at `etl/` and run dbt commands as usual.

Pre-populated copy-paste command hints can be produced at any time:

```
(venv) ~/git/ephemeral_cloud_etl$ python3 ece --hints
module.db.random_id.context: Refreshing state... [id=uiznCQ]
module.db.digitalocean_database_cluster.etl: Refreshing state... [id=4273ad9b-a966-48e9-9eb6-20571fada70e]
module.db.digitalocean_kubernetes_cluster.data-apps: Refreshing state... [id=a85a8a04-eadf-49ee-b867-0d41a906711d]
module.db.kubernetes_deployment.pgweb: Refreshing state... [id=default/pgweb]

No changes. Your infrastructure matches the configuration.

OpenTofu has compared your real infrastructure against your configuration and found no differences, so no changes are needed.

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
found database dbt-pgsql-ba2ce709

Log into dbt-pgsql-ba2ce709 with:
PGPASSWORD=AVNS_hEICA80ZuxfdNoT2XV5 psql -h dbt-pgsql-ba2ce709-do-user-1228802-0.c.db.ondigitalocean.com -p 25060 -U doadmin -d defaultdb

See pg_activity with:
PGPASSWORD=AVNS_hEICA80ZuxfdNoT2XV5 pg_activity -h dbt-pgsql-ba2ce709-do-user-1228802-0.c.db.ondigitalocean.com -p 25060 -U doadmin -d defaultdb

Run dbt with:
dbt build --project-dir etl --profiles-dir etl

Connect to kubernetes with:
kubectl --kubeconfig kubeconfig.yml get pods

Forward frontend with:
kubectl --kubeconfig kubeconfig.yml port-forward deployment/pgweb 8081:8081
```

ece has landed `./kubeconfig.yml`, so we can copy-paste these commands to view our pods and reach the web ui:

```
(venv) ~/git/ephemeral_cloud_etl$ kubectl --kubeconfig kubeconfig.yml get pods
NAME                     READY   STATUS    RESTARTS   AGE
pgweb-59c5b595f5-jkb76   1/1     Running   0          24m

(venv) ~/git/ephemeral_cloud_etl$ kubectl --kubeconfig kubeconfig.yml port-forward deployment/pgweb 8081:8081
```

When we're happy with the environment, we can publish it to 'production'.  This doesn't move any data, but moves the tf state itsef from our dev context to the production state under `prod/`.  The idea here is that when working on a team, `prod/` would be configured to use an external locking state provider.

In this example, we have a smaller instance tier defined for the production database, so it is simultaneously downsized in-place:

```
(venv) ~/git/ephemeral_cloud_etl$ python3 ece --publish
module.db.random_id.context: Refreshing state... [id=uiznCQ]
module.db.digitalocean_database_cluster.etl: Refreshing state... [id=4273ad9b-a966-48e9-9eb6-20571fada70e]
module.db.digitalocean_kubernetes_cluster.data-apps: Refreshing state... [id=a85a8a04-eadf-49ee-b867-0d41a906711d]
module.db.kubernetes_deployment.pgweb: Refreshing state... [id=default/pgweb]

No changes. Your infrastructure matches the configuration.

OpenTofu has compared your real infrastructure against your configuration and found no differences, so no changes are needed.

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
found database dbt-pgsql-ba2ce709

No changes. No objects need to be destroyed.

Either you have not created any objects yet or the existing objects were already deleted outside of OpenTofu.

Destroy complete! Resources: 0 destroyed.
module.db.random_id.context: Refreshing state... [id=uiznCQ]
module.db.digitalocean_database_cluster.etl: Refreshing state... [id=4273ad9b-a966-48e9-9eb6-20571fada70e]
module.db.digitalocean_kubernetes_cluster.data-apps: Refreshing state... [id=a85a8a04-eadf-49ee-b867-0d41a906711d]
module.db.kubernetes_deployment.pgweb: Refreshing state... [id=default/pgweb]

OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  ~ update in-place

OpenTofu will perform the following actions:

  # module.db.digitalocean_database_cluster.etl will be updated in-place
  ~ resource "digitalocean_database_cluster" "etl" {
        id                   = "4273ad9b-a966-48e9-9eb6-20571fada70e"
        name                 = "dbt-pgsql-ba2ce709"
      ~ size                 = "db-s-2vcpu-4gb" -> "db-s-1vcpu-2gb"
        tags                 = []
        # (16 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.

Do you want to perform these actions?
  OpenTofu will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

module.db.digitalocean_database_cluster.etl: Modifying... [id=4273ad9b-a966-48e9-9eb6-20571fada70e]
module.db.digitalocean_database_cluster.etl: Modifications complete after 14m32s [id=4273ad9b-a966-48e9-9eb6-20571fada70e]

Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
Removed module.db.random_id.context
Successfully removed 1 resource instance(s).
Removed module.db.digitalocean_database_cluster.etl
Successfully removed 1 resource instance(s).
Removed module.db.digitalocean_kubernetes_cluster.data-apps
Successfully removed 1 resource instance(s).
Removed module.db.kubernetes_deployment.pgweb
Successfully removed 1 resource instance(s).
```

Once published, our dev state is empty, and we're free to run the full stack again without affecting production:

```
(venv) ~/git/ephemeral_cloud_etl$ tofu state list
(venv) ~/git/ephemeral_cloud_etl$
(venv) ~/git/ephemeral_cloud_etl$ tofu -chdir=prod state list
module.db.digitalocean_database_cluster.etl
module.db.digitalocean_kubernetes_cluster.data-apps
module.db.kubernetes_deployment.pgweb
module.db.random_id.context
(venv) ~/git/ephemeral_cloud_etl$ python3 ece
...
```

All resources are destroyed with `--cleanup`.  (This does not include production.  Once published, ece doesn't touch production again until the next publication):

```
$ python3 ece --cleanup
module.dev.digitalocean_database_cluster.etl: Refreshing state... [id=530c0958-7e7d-4670-9c30-d94d631a68de]
module.dev.digitalocean_database_db.etl: Refreshing state... [id=530c0958-7e7d-4670-9c30-d94d631a68de/database/dbt]

OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

OpenTofu will perform the following actions:

  # module.dev.digitalocean_database_cluster.etl will be destroyed

-- diff truncated --

Plan: 0 to add, 0 to change, 2 to destroy.
module.dev.digitalocean_database_db.etl: Destroying... [id=530c0958-7e7d-4670-9c30-d94d631a68de/database/dbt]
module.dev.digitalocean_database_db.etl: Destruction complete after 12s
module.dev.digitalocean_database_cluster.etl: Destroying... [id=530c0958-7e7d-4670-9c30-d94d631a68de]
module.dev.digitalocean_database_cluster.etl: Destruction complete after 2s

Destroy complete! Resources: 2 destroyed.
```

## caveats

In this example project, I'm simply staging some sample data from local csvs.  If dealing with TBs of data, we would of course want to stage this from somthing local to our infrastructure, like object storage.

The `--publish` workflow doesn't do much other than export our tf state.  IRL, we would probably also want to trigger the movement of a floating ip, dns, etc. as appropriate.
