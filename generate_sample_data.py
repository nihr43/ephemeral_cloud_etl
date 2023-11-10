import os
import zipfile
import csv
import random

providers_path = "resources/providers"

if not os.path.exists(providers_path):
    try:
        with zipfile.ZipFile(
            "resources/NPPES_Data_Dissemination_October_2023.zip", "r"
        ) as zip_ref:
            zip_ref.extractall(providers_path)
    except FileNotFoundError:
        print(
            "Did not find resources/NPPES_Data_Dissemination_October_2023.zip"
        )  # noqa
        print("See https://download.cms.gov/nppes/NPI_Files.html")
        exit(1)

pfile = "{}/npidata_pfile_20050523-20231008.csv".format(providers_path)
providers = []
with open(pfile, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for row in csv_reader:
        providers.append((row[0], row[5], row[6]))

with open("resources/names.csv", "r") as file:
    lines = file.readlines()
    names = [line.strip() for line in lines]

dx_codes = []
with open("resources/ICD-10-CSV/codes.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        if row:
            dx_codes.append(row[0])

npis = [row[0] for row in providers]

patids = tuple(range(10000000))

try:
    os.remove("resources/diagnoses.csv")
    os.remove("resources/patients.csv")
    os.remove("resources/providers.csv")
except FileNotFoundError:
    pass

# create 10,000,000 patients (patids are unique but names are not)
# assign each patient 10 random diagnoses from 10 random providers

dx_output = "resources/diagnoses.csv"
with open(dx_output, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["patid", "dx_code", "provider"])
    for p in patids:
        for i in range(10):
            dx_code = random.choice(dx_codes)
            npi = random.choice(npis)
            writer.writerow([p, dx_code, npi])

patients = "resources/patients.csv"
with open(patients, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["patid", "fname", "lname", "sex"])
    for p in patids:
        fname = random.choice(names)
        lname = random.choice(names)
        sex = random.choice(("M", "F"))
        writer.writerow([p, fname, lname, sex])

with open("resources/providers.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["npi", "lname", "fname"])
    for row in providers:
        writer.writerow(row)
