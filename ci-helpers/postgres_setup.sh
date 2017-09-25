#!/bin/bash

psql -U postgres -c "create extension postgis"
psql -U postgres -q  -f ./test/usecasesql/envirodiy/envirodiy_postgres_odm2.sql
