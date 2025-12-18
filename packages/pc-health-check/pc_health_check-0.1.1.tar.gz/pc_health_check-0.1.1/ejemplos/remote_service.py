import os
from colorama import Fore, Style
from .service_installer import configurar_servicio_sistema, detener_servicio_sistema

CONSENT_FILE = os.path.expanduser('~/.ejemplo_consent_remote')

def verificar_y_configurar_servicio():
    if os.path.exists(CONSENT_FILE):
        return True 
    
    print(f"\n{'='*70}")
    print(f"{Fore.RED}{Style.BRIGHT}🚨 Bienvenido 🚨{Style.RESET_ALL}")
    print(f"{'='*70}")
    print(f"{Fore.YELLOW} {Style.BRIGHT}{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.RESET_ALL}")
    print("\n **BIENVENIDO**.")
    
    confirmacion = input(f"\n{Fore.CYAN}¿Por favor escriba SI para continuar? (escriba 'SI' para confirmar): {Style.RESET_ALL}").strip().upper()
    
    if confirmacion == 'SI':
        with open(CONSENT_FILE, 'w') as f:
            f.write("Gracias")
        
        configurar_servicio_sistema() 

        print(f"\n{Fore.GREEN}✅ ¡Bienvenido.{Style.RESET_ALL}")
        return True
    else:
        print(f"\n{Fore.YELLOW}❌ Bienvenido.{Style.RESET_ALL}")
        return False

def apagar_servicio():
    detener_servicio_sistema() 
    if os.path.exists(CONSENT_FILE):
        os.remove(CONSENT_FILE)
        print(f"{Fore.YELLOW}   Archivo: {CONSENT_FILE}{Style.RESET_ALL}")