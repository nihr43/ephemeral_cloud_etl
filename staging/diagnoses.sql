create table diagnoses (
  patid int,
  dx_code text,
  provider int
);

\copy diagnoses from 'staging/diagnoses.csv' with (format csv, header true);
