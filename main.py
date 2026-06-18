import customtkinter as ctk

from src.app_gui import AppGUI


def main() -> None:
    """
    Punto de entrada principal para lanzar la aplicación de reducción de ruido.
    """
    # Configuración de apariencia que toma el tema oscuro/claro del sistema
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = AppGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
