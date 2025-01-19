FROM postgres:13

# Set wal_level to logical
RUN sed -i \
    -e "s/^wal\_level\s=*/wal\_level\s=\slogical/" /var/lib/postgresql/data/postgresql.conf
