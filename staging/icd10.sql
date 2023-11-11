create table icd10 (
  dx_code text,
  description text
);

\copy icd10 from 'staging/icd10.csv' with (format csv, header true);
