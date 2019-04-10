# How to add your own Data Source

**IMPORTANT**: this is useful information if you are **developing the Longitude library**. If you are just using it, this information is irrelevant for you.

If you want to add data source classes to Longitude you must create a new class that inherits from DataSource.

* That class must implement ```execute_query()``` and ```parse_response()```
* It can also override:
  * ```__init___```: if it needs instance attributes to be defined
  * ```setup()```: if it needs some process to be done **before** executing queries

### Template

Feel free to copy/paste this code and customize it:

```python

from core.data_sources.base import DataSource


class MyDatabaseTechnologyDataSource(DataSource):

    def __init__(self, options={}):
        # TODO: Here you can define instance values like cursors, connections, etc...
        super().__init__(options)

    def setup(self):
        # TODO: Write how your database connection is stablised, how to log...
        super().setup()

    def execute_query(self, query_template, params, query_config, **opts):
        # TODO: Write how the database query is executed and return the response or None
        pass

    def parse_response(self, response):
        # TODO: Write how the database query response is converted into a LongitudeQueryResponse object
        pass

```

### Do I need to override the methods always?

No. If your data source is, for example, some REST API (or any service without session or permament connection), you do not need any preparation. You can just execute queries and parse responses.

Sometimes the setup thing is needed for performance (i.e. instead of connecting/disconnecting a database in each query.)

### Must I implement the execute and parse methods always?

Yes. Those are the interface methods and are mandatory.