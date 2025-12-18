import psutil
from colorama import Fore, Style

def format_bytes(bytes_value):
    if bytes_value >= (1024 ** 3):
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    return f"{bytes_value / (1024 ** 2):.2f} MB"

def mostrar_recursos(consentimiento_activo):
    print(f"\n{Fore.CYAN}=== 💻 RECURSOS DEL SISTEMA ({Style.BRIGHT}ejemplo{Style.NORMAL}) ==={Style.RESET_ALL}")
    
    mem = psutil.virtual_memory()
    print(f"\n{Fore.BLUE}--- 💾 Memoria RAM ---{Style.RESET_ALL}")
    print(f"  Total:    {Fore.MAGENTA}{format_bytes(mem.total)}{Style.RESET_ALL}")
    print(f"  En Uso:   {Fore.YELLOW}{format_bytes(mem.used)} ({mem.percent}%)")

    try:
        disco = psutil.disk_usage('/')
        print(f"\n{Fore.BLUE}--- 💽 Almacenamiento Principal ---{Style.RESET_ALL}")
        print(f"  Capacidad: {Fore.MAGENTA}{format_bytes(disco.total)}{Style.RESET_ALL}")
        print(f"  Libre:     {Fore.GREEN}{format_bytes(disco.free)}{Style.RESET_ALL}")
    except Exception:
        print(f"{Fore.RED}  No se pudo acceder a la información del disco raíz.{Style.RESET_ALL}")

    if consentimiento_activo:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🟢 ESTADO DE GESTIÓN :{Style.RESET_ALL} {Fore.GREEN}ACTIVA{Style.RESET_ALL}")
        print(f"   leer, ejecute: {Fore.YELLOW}ejemplo --disable-remote{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}🟡 ESTADO DE GESTIÓN : {Fore.YELLOW}INACTIVA (Requiere Consentimiento){Style.RESET_ALL}")