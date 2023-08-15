# Multi-tenancy strategies with Django+PostgreSQL

A presentation given at PyCon AU 2023 on Friday August 18

## Presentation

To view the presentation:

```bash
cd presentation
python3 -m http.server
```

You can now view the presentation at http://localhost:8000/


## Code Samples

Code samples are in `examples`

Create the file `examples/env` with the following entries (fill in values as appropriate)
```ini
SECRET_KEY=....
```

Setup:
```bash
cd examples

python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

```

### Multiple Database setup

- Database names are in the form `$PGDATABASE_tenant-$i`
- The `MULTIDB_COUNT` env var is used to define the max number of tenancies  
- Create databases:
```bash
# you still need a default database for some operations (even if it's empty)
echo "CREATE DATABASE \"$PGDATABASE\";" | psql postgres
for i in {0..$(( $MULTIDB_COUNT - 1 ))} ; do
  (
    db="${PGDATABASE}_tenant-$i"
    # uncomment the DROP if you want clean databases
    echo "DROP DATABASE \"$db\";" | psql
    echo "CREATE DATABASE \"$db\";" | psql
    ./manage.py migrate --database "tenant-$i"
  )
done
```

### Create sample test data
```bash
./manage.py createtestdata
```

- For options see `--help`
  - Notably you can use the `--account` param to generate more/less data
  - Takes ~9m to generate 2,000 accounts (~30k projects, ~150k tasks, ~750k subtasks)
  - If using the Multiple Database config you can't create more accounts than `$MULTIDB_COUNT` (the databases won't exist)

