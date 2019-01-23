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
