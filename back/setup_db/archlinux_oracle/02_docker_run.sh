#!/bin/bash -x
docker run -d \
  --name oracle21xe \
  -p 1521:1521 \
  -p 5500:5500 \
  -e ORACLE_PASSWORD="123" \
  -e ORACLE_CHARACTERSET="AL32UTF8" \
  gvenzl/oracle-xe:21.3.0-slim

# ORACLE_PASSWORD="" sets the SYS / SYSTEM / PDBADMIN admin password.
