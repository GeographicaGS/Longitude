### SQLAlchemy dialect and py-dbapi connector for Carto integration with alembic

#### Usage:

You'll need to add to alembic/env.py:


```python
    # ...
    from longitude.tools.sqlalchemy.dbapi import connect as carto_dbapi_connect
    # ...

    def cartodb_connector(*args, **kwargs):
        return carto_dbapi_connect(user=<CARTO_USER>, api_key=<CARTO_API_KEY>)
    # ...


    def run_migrations_offline():
        # ...
        context.configure(
            connection=cartodb_connector(), target_metadata=target_metadata, literal_binds=True
        )
        # ...


    def run_migrations_online():
        # ...
        # Note the 'carto' string with the just-registered sqlalembic dialect.
        # This dialect is auto-registered by the dbapi.py script when it's included
        connectable = create_engine('carto://', creator=cartodb_connector)
        # ...

    # ...
```

Then, you'll be able to use `alembic` as normal. i.e:

```bash
alembic revision --autogenerate -m "Crossing fingers..."
```
