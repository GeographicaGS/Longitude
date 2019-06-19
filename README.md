# Longitude

A **new** bunch of middleware functions to build applications on top of CARTO.

## Roadmap

- [ ] Database model
  - [x] CARTO data source
    - [x] Basic parametrized queries (i.e. templated queries)
    - [x] Protected parametrized queries (i.e. avoiding injection)
    - [ ] Bind/dynamic parameters in queries (server-side render)
  - [x] Postgres data source
    - [x] psycopg2
    - [x] SQLAlchemy
  - [x] Cache
    - [x] Base cache
      - [x] Put
      - [x] Get
      - [x] Key generation
      - [x] Flush
      - [x] Tests
    - [x] Ram Cache
      - [x] Tests
    - [x] Redis Cache
      - [x] Tests 
  - [x] Documentation
    - [x] Sample scripts
  - [x] Unit tests
  - [x] Sample scripts
 
- [x] Config
 
- [x] CI PyPi versioning

- [ ] COPY operations
  - [x] Carto
    - [x] COPY FROM
    - [ ] COPY TO
  - [x] Postgres
    - [x] COPY FROM
    - [ ] COPY TO
  - [x] SQLAlchemy
    - [x] COPY FROM
    - [ ] COPY TO
 
- [ ] Validations
  - [ ] Marshmallow
    - [ ] Wrapper (?)
    - [ ] Documentation
 
- [x] Swagger
  - [ ] Decorators
  - [x] Flassger (?)
  - [ ] OAuth integration
  - [x] Postman integration
  - [ ] Documentation
  
- [ ] SQL Alchemy
  - [ ] Model definition
  - [ ] Jenkins integration
  - [ ] Documentation

- [ ] OAuth
  - [x] OAuth2 with Carto (onprem)
  - [ ] Role mapping
  - [ ] Token storage
  - [ ] Documentation
  
## As final user...

How to use:
```bash
pip install longitude
```

Or:
```bash
pipenv install longitude
```

Or:
```bash
poetry add longitude
```

Or install from GitHub:
```bash
pip install -e git+https://github.com/GeographicaGS/Longitude#egg=longitude
```

## As developer...

### First time

1. Install ```poetry``` using the [recommended process](https://github.com/sdispater/poetry#installation)
    1. poetry is installed globally as a tool
    1. It works along with virtualenvironments
1. Create a virtual environment for Python 3.x (check the current development version in ```pyproject.toml```)
    1. You can create it wherever you want but do not put it inside the project
    1. A nice place is ```$HOME/virtualenvs/longitude```
1. Clone the ```longitude``` repo
1. `cd` to the repo and:
    1. Activate the virtual environment: `. ~/virtualenvs/longitude/bin/activate`
    1. Run `poetry install`
1. Configure your IDE to use the virtual environment

### Daily

1. Remember to activate the virtual environment 

### Why Poetry?

Because it handles development dependencies and packaging with a single file (```pyproject.toml```), which is [already standard](https://flit.readthedocs.io/en/latest/pyproject_toml.html).

## Sample scripts

These are intended to be used with real databases (i.e. those in your profile) to check features of the library. They must be run from the virtual environment.

## Testing and coverage 

The [```pytest-cov```](https://pytest-cov.readthedocs.io/en/latest/) plugin is being used. Coverage configuration is at ```.coveragerc``` (including output folder).

You can run something like: ```pytest --cov-report=html --cov=core core``` and the results will go in the defined html folder.

There is a bash script called ```generate_core_coverage.sh``` that runs the coverage analysis and shows the report in your browser.
