[alembic]

# Put here all modules which contain migrations
# used in this project and which are not defined
# the ./migrations/versions/ folder. Each of the
# listed modules must have submodule/directory
# named 'migrations' containing alembic
# version files.
# plugin_migrations =
#     connector.template
#     connector.instance
#     longitude.credential

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
