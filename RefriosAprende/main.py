"""Punto de entrada de Refrios Aprende."""
import customtkinter as ctk

from controller.usuario_controller import UsuarioController
from view.screens.dashboard_view import DashboardView
from view.screens.login_view import LoginView
from view.screens.primer_administrador_view import PrimerAdministradorView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AplicacionRefriosAprende:
    """Orquesta la navegación entre ventanas de la aplicación."""

    def iniciar(self) -> None:
        if UsuarioController().existe_administrador_activo():
            self._mostrar_login()
        else:
            self._mostrar_primer_administrador()

    def _mostrar_primer_administrador(self) -> None:
        ventana = PrimerAdministradorView(al_crear_administrador=self._mostrar_login)
        ventana.mainloop()

    def _mostrar_login(self) -> None:
        ventana = LoginView(al_iniciar_sesion=self._mostrar_dashboard)
        ventana.mainloop()

    def _mostrar_dashboard(self, usuario_autenticado) -> None:
        ventana = DashboardView(usuario=usuario_autenticado, al_cerrar_sesion=self._mostrar_login)
        ventana.mainloop()


if __name__ == "__main__":
    AplicacionRefriosAprende().iniciar()
