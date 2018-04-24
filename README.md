# Longitude

A bunch of middleware functions to build applications on top of CARTO.

How to use:
```
pip install geographica-longitude
```

Or install from GitHub:
```
pip install -e git+https://github.com/GeographicaGS/Longitude#egg=longitude
```

## Upload a new version

You need to be part of Geographica's developer team to be able to accomplish this task.

Start docker
```
docker-compose run --rm python bash
```
Install twine
```
pip install twine
```

Set vertion at setup.py

Upload:
```
python setup.py sdist
twine upload dist/geographica-longitude-<yourversion>.tar.gz
```
