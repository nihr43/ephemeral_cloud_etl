create table providers (
  npi int,
  lname text,
  fname text
);

\copy providers from 'staging/providers.csv' with (format csv, header true);
