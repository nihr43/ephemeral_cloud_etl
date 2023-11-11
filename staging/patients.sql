create table patients (
  patid int,
  fname text,
  lname text,
  sex text
);

\copy patients from 'staging/patients.csv' with (format csv, header true);
