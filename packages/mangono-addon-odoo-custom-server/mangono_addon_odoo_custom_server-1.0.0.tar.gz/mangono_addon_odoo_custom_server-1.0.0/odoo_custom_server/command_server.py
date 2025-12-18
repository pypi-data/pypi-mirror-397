from __future__ import annotations

import contextlib
import csv
import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Callable, Tuple, Union

import psycopg2

with contextlib.suppress(ImportError):
    import odoo

import importlib_metadata
from environ_odoo_config import cli
from environ_odoo_config.environ import Environ
from environ_odoo_config.odoo_config import OdooEnvConfig
from environ_odoo_config.odoo_utils import get_config_db_names

_logger = logging.getLogger(__name__)


def _flat_map(f: Callable[[str], list[str]], xs: list[str]) -> list[str]:
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys


def _auto_load_entry_point() -> dict[str, Callable[[Environ], bool]]:
    """Charge tous les patchs d'odoo
    Ces patchs sont définis par des points d'entrée dans le pyproject.toml dans les sections
    [tool.addon-odoo-wheel.entry-points."odoo_patch_server"]
    La variable d'environnement ODOO_CUSTOM_SERVER_DISABLE_PATCH permet de désactiver le patchage
    """

    result: dict[str, Callable[[Environ], bool]] = {}
    if os.getenv("ODOO_CUSTOM_SERVER_DISABLE_PATCH", str(False)).lower() == "true":
        _logger.info("No patching Odoo, ODOO_CUSTOM_SERVER_DISABLE_PATCH is set to 'True'")
        return result
    _logger.info("---------- PATCHING ODOO ---------- ")
    entry_points = importlib_metadata.entry_points(group="odoo_patch_server")
    for entry_point in entry_points:
        ep = entry_point.load()
        if callable(ep):
            ep()
        _logger.info("Patching %s", entry_point.name)
    return result


class OdooPatchedServer:
    """Odoo Config from env (mapper and all converter entry-points are loaded).
    Only exist after `load_env_config` not in `__init__`"""

    _exit = True  # May be False for testing, to avoid odoo process doing sys.exit()
    env_config: Union[OdooEnvConfig, None]

    def __init__(self, apply_patcher=True):
        super().__init__()
        self._apply_patcher = apply_patcher
        self.env_config = None  # it's load_env_config that creates the configuration

    def _parser(self) -> ArgumentParser:
        """Return a parser handling --config to define the configuration file if needed
        Usefull if need to use an existing one, or alternate location must be used
        """
        parser = ArgumentParser()
        parser.add_argument("-c", "--config", dest="config", help="specify alternate config file")
        return parser

    def execute_command(self, args) -> None:
        self.load_env_config()
        if not self.do_somethings():
            return
        if self._apply_patcher:
            _auto_load_entry_point()
        opt, args = self.convert_args(args)
        config_rc = opt.config

        if not config_rc and not self.env_config.misc.config_file:
            raise ValueError("No configuration file for Odoo")
        cli.cli_save_env_config(self.env_config, auto_save=True)

        rc = self._exec_odoo()
        if self._exit:
            sys.exit(rc)

    def _exec_odoo(self) -> int:
        """Code copied from odoo odoo/cli/server.py:main(), but without the empty database creation and without
        translation command handling"""
        from odoo.cli.server import check_postgres_user, check_root_user, report_configuration, setup_pid_file
        from odoo.service.server import start

        check_root_user()
        check_postgres_user()
        report_configuration()
        config = odoo.tools.config
        self.report_additional_configuration(config)

        # the default limit for CSV fields in the module is 128KiB, which is not
        # quite sufficient to import images to store in attachment. 500MiB is a
        # bit overkill, but better safe than sorry I guess
        csv.field_size_limit(500 * 1024 * 1024)

        preloads = get_config_db_names(config)
        for preload in preloads:
            if odoo.service.db.exp_db_exist(preload):
                self._setup_database(preload)

        # This needs to be done now to ensure the use of the multiprocessing
        # signaling mecanism for registries loaded with -d (until V16)
        if config["workers"] and odoo.release.serie < "17.0":
            odoo.multi_process = True

        stop = config["stop_after_init"]
        setup_pid_file()
        return start(preload=preloads, stop=stop)

    def load_env_config(self):
        self.env_config = OdooEnvConfig()

    def do_somethings(self) -> bool:
        """to be overridden by subclasses"""
        return True

    def convert_args(self, args: list[str]) -> Tuple[Namespace, list[str]]:
        # Removing blank sub_args
        # Is called with "$ENV_VAR" but ENV_VAR isn't set, then `sub_args` contains `['']
        # So we remove empty string from it
        args = _flat_map(lambda it: it.split(), args)
        args = [s.strip() for s in args if s.split()]
        return self._parser().parse_known_args(args)

    def report_additional_configuration(self, config):
        _logger.info("database: max conn %s", config["db_maxconn"])
        _logger.info("Loaded module: %s", config["server_wide_modules"])
        _logger.info("Stop after init: %s", config["stop_after_init"])

    def _setup_database(self, name):
        """
        Allow to setup a database for Odoo, same as service/db#_create_empty_database with the `CREATE DATABASE`
        The data must exist
        """
        import odoo.sql_db
        import odoo.tools

        try:
            db = odoo.sql_db.db_connect(name)  # noqa
            with db.cursor() as cr:
                cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
                if odoo.tools.config["unaccent"]:
                    cr.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
                    # From PostgreSQL's point of view, making 'unaccent' immutable is incorrect
                    # because it depends on external data - see
                    # https://www.postgresql.org/message-id/flat/201012021544.oB2FiTn1041521@wwwmaster.postgresql.org#201012021544.oB2FiTn1041521@wwwmaster.postgresql.org
                    # But in the case of Odoo, we consider that those data don't
                    # change in the lifetime of a database. If they do change, all
                    # indexes created with this function become corrupted!
                    cr.execute("ALTER FUNCTION unaccent(text) IMMUTABLE")
        except psycopg2.Error as e:
            _logger.warning("Unable to create PostgreSQL extensions : %s", e)

        if odoo.release.version >= "18.0":
            import odoo.service.db

            odoo.service.db._check_faketime_mode(name)
        # restore legacy behaviour on pg15+
        try:
            db = odoo.sql_db.db_connect(name)
            with db.cursor() as cr:
                cr.execute("GRANT CREATE ON SCHEMA PUBLIC TO PUBLIC")
        except psycopg2.Error as e:
            _logger.warning("Unable to make public schema public-accessible: %s", e)
