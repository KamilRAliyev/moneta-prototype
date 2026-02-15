#!/bin/bash
# Copy custom pg_hba.conf so connections from Docker network are allowed.
# Runs only on first DB init; overlay mount handles existing volumes.
cp /docker-entrypoint-initdb.d/pg_hba.conf "$PGDATA/pg_hba.conf"
