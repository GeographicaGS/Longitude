#!/usr/bin/env python3

import os
import re
import sys

from alembic.config import CommandLine as OriginalCommandLine, Config as OriginalConfig

import importlib.util

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

_longitude_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))

if _longitude_path not in sys.path:
    sys.path.insert(0, _longitude_path)


from longitude import config as app_config


MIGRATION_SUBMODULE_NAME = 'migrations'


def patch_config(conf):

    # By default, migration submodule inside each module is "migrations
    conf.set_main_option('script_location', MIGRATION_SUBMODULE_NAME)

    # Write pattern
    if conf.get_main_option('file_template', None) is None:
        conf.set_main_option(
            'file_template',
            '%%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s'
        )

    if conf.get_main_option('timezone', None) is None:
        conf.set_main_option('timezone', app_config.TIMEZONE)

    # Build db URL configuration from longitude settings
    conf.set_main_option('sqlalchemy.url', 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=app_config.DB_USER,
        password=app_config.DB_PASSWORD,
        host=app_config.DB_HOST,
        port=app_config.DB_PORT,
        db_name=app_config.DB_NAME
    ))

    # Load migration from third party modules defined in 'plugin_migrations'
    external_migration_mods = filter(
        None,
        re.split(r'\s+', conf.get_main_option('plugin_migrations', ''))
    )

    version_locations = [
        os.path.join(os.getcwd(), MIGRATION_SUBMODULE_NAME, 'versions')
    ]

    for mod in external_migration_mods:
        mod_spec = importlib.util.find_spec(mod)

        for module_path in getattr(mod_spec, 'submodule_search_locations', []):
            migration_path = os.path.join(module_path, MIGRATION_SUBMODULE_NAME)

            if os.path.exists(migration_path):
                version_locations.append(migration_path)
                break

    if version_locations:
        if conf.get_main_option('version_locations'):
            version_locations.append(conf.get_main_option('version_locations'))

        conf.set_main_option('version_locations', ' '.join(version_locations))

    return conf

def patch_argv(argv):

    argv = list(argv)

    positional_arguments = tuple(filter(
        lambda x: x.startswith('-'),
        argv
    ))

    # If init provides no template folder, use MIGRATION_SUBMODULE_NAME
    if argv and argv[0]=='init' and len(positional_arguments)==0:
        argv.append(MIGRATION_SUBMODULE_NAME)

    return argv

class Config(OriginalConfig):
    def get_template_directory(self):
        return os.path.join(os.path.dirname(__file__), 'templates')


class CommandLine(OriginalCommandLine):

    def main(self, argv=None):
        options = self.parser.parse_args(argv)
        if not hasattr(options, "cmd"):
            # see http://bugs.python.org/issue9253, argparse
            # behavior changed incompatibly in py3.3
            self.parser.error("too few arguments")
        else:
            cfg = Config(file_=options.config,
                         ini_section=options.name,
                         cmd_opts=options)

            cfg = patch_config(cfg)

            self.run_cmd(cfg, options)



def main(argv=None, prog=None, **kwargs):
    """The console runner function for Alembic."""

    argv = patch_argv(argv or sys.argv[1:])

    CommandLine(prog=prog).main(argv=argv)


if __name__ == '__main__':
    main()
