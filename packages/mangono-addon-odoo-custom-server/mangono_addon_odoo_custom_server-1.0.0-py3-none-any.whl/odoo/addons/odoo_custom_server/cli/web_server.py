from environ_odoo_config._odoo_command import OdooCommand

from odoo_custom_server.command_server import OdooPatchedServer


class WebServer(OdooCommand):
    """
    Only the default behavior
    1. apply patch
    2. start server odoo with the config
    """

    name = "web_server"

    def get_runner(self) -> OdooPatchedServer:
        return OdooPatchedServer(apply_patcher=True)

    def run(self, args):
        self.get_runner().execute_command(args)
