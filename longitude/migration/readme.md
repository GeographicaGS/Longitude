# ``longitude.migrations``

This package interfaces alembic's main script via its alias 
``lmigrate``, which automatically configures alembic using some
conventions and configuration from ``longitude.config``:

* Enforces alembic ``script_location`` main option to be ``migrations``.
This means that the projects using this module should define its
global versions and env file inside a folder named ``migrations``
placed in the same folder that the ``alembic.ini`` file.
* Changes default version file template option (``file_template``)
to follow a pattern including the version's date.
* Enforces the usage of timezones through latitude's config paramater
``latitude.config.TIMEZONE``, unless alembics .ini file option 
``timezone`` is overriden.
* Automatically sets alembic driver's url according to database
connection parameters in ``latitude.config.DB_*``.
* Adds new setting parameter ``plugin_migrations``, which specifies
from which modules should the system try to find new versions and 
migrations. For each of the packages specified in ``plugin_migrations``,
the system will try to find versions in a their respective ``migrations``
submodule.

  This is achieved through a mechanism involving the extension of 
alembic's built in option ``version_locations``.

## Enabling migrations in ``longitude`` based projects.

First, you'll have to install alembic.

```bash
> pip install alembic==2
# Using pipenv
> pipenv install alembic==2
```

The create alembic's configuration structure, simply run:
```bash
> lmigrate init
```

The command will generate a folder named ``migrations`` and an alembic
configuration file named ``alembic.ini``. From the ``alembic.ini`` 
folder you can run usual alembic commands with ``lmigrate``.
  