from environ_odoo_config._odoo_command import OdooCommand

from odoo.addons.odoo_custom_server.command_server import OdooPatchedServer


class WebServer(OdooCommand):
    """
    Run Odoo in web mode, apply patch and then run the server
    """

    name = "web_server"

    def get_runner(self) -> OdooPatchedServer:
        return OdooPatchedServer(apply_patcher=True)

    def run(self, args):
        self.get_runner().execute_command(args)
