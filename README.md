# Multi-tenancy strategies with Django+PostgreSQL

A presentation given at PyCon AU 2023 on Friday August 18

https://www.youtube.com/watch?v=j-bbaf6hCMo

## Presentation

To view the presentation slides:

```bash
cd presentation
python3 -m http.server
```

You can now view the presentation at http://localhost:8000/


## Code Samples

Code samples are in [`examples`](examples)

There are two strategies demonstrated:
- single app server + multiple databases
- single app server + single database schema, mandatory tenancy filtering in querysets/managers, tenancy denormalisation, postgres row-level security

If you want sample code for implementing a single app server + multiple schemas then check out [django-tenants](https://django-tenants.readthedocs.io/)  

Create the file `examples/env` with the following entries (fill in values as appropriate, and uncomment one of the MultipleDb or SingleSchema sections)
```ini

#export DJANGO_CONFIGURATION=MultipleDb
#export PGDATABASE=...
#export MULTIDB_COUNT=5

#export DJANGO_CONFIGURATION=SingleSchema
#export PGDATABASE=...
# this user must not be a postgres superuser or RLS checks will be bypassed
#export PGUSER=...


# Optional settings:
#export PGHOST=localhost
#export PGPORT=5432
#export PGUSER=...
#export PGPASSWORD=...
export TZ=Australia/Melbourne

export SECRET_KEY=...

```

Now `source env` to load these environment variables into your local shell 

Python virtualenv setup:
```bash
cd examples

# the code uses some of the typing additions in python 3.11 (eg typing.Self)
# if you want it to work with earlier python versions then you can just delete
# those references in the code when python throws up an error
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

```

### Multiple Database setup

- Database names are in the form `$PGDATABASE_tenant-$i`
- The `MULTIDB_COUNT` env var is used to define the number of tenant databases to create   
- Create databases:
```bash
# you still need a default database for some operations (even if it's empty)
echo "CREATE DATABASE \"$PGDATABASE\";" | psql postgres
for i in {0..$(( $MULTIDB_COUNT - 1 ))} ; do
  (
    db="${PGDATABASE}_tenant-$i"
    # uncomment the DROP if you want clean databases
    #echo "DROP DATABASE \"$db\";" | psql
    echo "CREATE DATABASE \"$db\";" | psql
    ./manage.py migrate --database "tenant-$i"
  )
done
```

- Note that while django insists that the `default` database exists, we don't
  actually use it so don't need to run the migrations for it.


### Single Database/Schema Setup

```bash
# uncomment the DROP if you want clean databases
#echo "DROP DATABASE \"$PGDATABASE\";" | psql postgres
echo "CREATE DATABASE \"$PGDATABASE\";" | psql postgres
./manage.py migrate
````

### Create sample test data

- Code is common for both strategies

```bash
./manage.py createtestdata --accounts 5
```

- For options see `--help`
  - Notably you can use the `--accounts` param to generate more/less data
  - Takes ~9m to generate 2,000 accounts (~30k projects, ~150k tasks, ~750k subtasks)
  - If using the Multiple Database config you can't create more accounts than `$MULTIDB_COUNT` (the databases won't exist)
- Each run will generate the same data (so if you run it multiple times in a row you'll get uniqueness errors). If you want to regenerate the data with more accounts then drop the database and start again.  

### DNS entries
- Both strategies provide  middleware that uses the subdomain to work out which tenancy is being used
- you need to add DNS entries to your hosts file for `tenant-0.localhost`, `tenant-1.localhost`, `tenant-2.localhost` etc
- After running `./manage.py runserver 8080` you can access:
  - `http://tenant-0.localhost:8080/`
  - `http://tenant-1.localhost:8080/`
  - `http://tenant-2.localhost:8080/`
  - etc
  - `http://localhost:8080/` (SingleSchema only -- this won't work for MultipleDb)
  - There's only 1 view in the system (listing subtasks), and the homepage will redirect to this view

