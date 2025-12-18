from __future__ import annotations

from addons_installer import cli as installer_cli
from environ_odoo_config._odoo_command import OdooCommand

from odoo_custom_server.command_server import OdooPatchedServer


class GenericServer(OdooCommand):
    """
    1. apply patch
    2. install the addons
    3. start server odoo with the config
    """

    name = "generic_server"

    def get_runner(self) -> OdooPatchedServer:
        return OdooPatchedServer(True)

    def run(self, args: list[str]):
        installer_cli.install_from_env(installer_cli.ArgsCli(all=True, verbose=True))
        self.get_runner().execute_command(args=args)
