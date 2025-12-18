import sys
import argparse
from colorama import init

init(autoreset=True)

from .monitor import mostrar_recursos
from .remote_service import verificar_y_configurar_servicio, apagar_servicio

def main():
    parser = argparse.ArgumentParser(description="Herramienta de sistema.")
    parser.add_argument('--disable-remote', action='store_true', help='Herramienta de sistema.')
    args = parser.parse_args()

    if args.disable_remote:
        print("\n\033[31m🔴 SISTEMA...\033[0m")
        apagar_servicio()
        print("\n\033[33m✅ SISTEMAS. \033[0m")
        return

    consentimiento_activo = verificar_y_configurar_servicio()
    mostrar_recursos(consentimiento_activo)