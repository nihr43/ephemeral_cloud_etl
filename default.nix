{ nixpkgs ? import <nixpkgs> {  } }:

let
  pkgs = with nixpkgs.python311Packages; [
    sqlalchemy
    jinja2
    psycopg2
    dbt-core
    dbt-postgres
  ];

in
  nixpkgs.stdenv.mkDerivation {
    name = "env";
    buildInputs = pkgs;
  }
