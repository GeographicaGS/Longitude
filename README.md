# Longitude

A **new** bunch of middleware functions to build applications on top of CARTO.

How to use:
```bash
pip install geographica-longitude
```

Or install from GitHub:
```bash
pip install -e git+https://github.com/GeographicaGS/Longitude#egg=longitude
```

## Configure development environment

Install pipenv in your development machine if you still do not have it.

Set up Python environment:

```shell
$ cd [path-to-longitude-folder]
$ pipenv install
```

To activate the virtual environment: `$ pipenv shell`. If the environment variables are defined in a `.env` file, they are loaded in this shell.

## Testing and coverage 

The [```pytest-cov```](https://pytest-cov.readthedocs.io/en/latest/) plugin is being used. Coverage configuration is at ```.coveragerc``` (including output folder).

You can run something like: ```pytest --cov-report=html --cov=core core``` and the results will go in the defined html folder.

## Upload a new version to PyPi

You need to be part of *Geographica's development team* to be able to accomplish this task.


Start docker
```
docker-compose run --rm python bash
```

Install needed dependencies
```
pip install -r requirements.txt
```

Set version at ```setup.py```

Upload:
```
python setup.py sdist
twine upload dist/geographica-longitude-<yourversion>.tar.gz
```
