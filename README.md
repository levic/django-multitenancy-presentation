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

### Create sample test data
```bash
./manage.py createtestdata
```

- For options see `--help`
  - Notably you can use the `--account` param to generate more/less data
  - Takes ~5m30s to generate 2,000 accounts (~30k projects, ~150k tasks, ~750k subtasks)
