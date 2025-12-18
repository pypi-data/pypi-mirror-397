import os
import subprocess
from colorama import Fore, Style

SERVICE_NAME = 'ejemplo-remote.service'
SERVICE_FILE_PATH = os.path.join('/etc/systemd/system', SERVICE_NAME)

def configurar_servicio_sistema():
    """Crea e inicia el servicio  systemd."""
    service_content = f"""
[Unit]
Description=Ejemplo  Access Service (Bienvenido)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 -m ejemplo.remote_tunnel
Restart=always
User={os.getlogin()}
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
"""
    try:
        print(f"{Fore.YELLOW}   el servicio...{Style.RESET_ALL}")
        # Lógica para escribir el archivo de servicio usando sudo
        subprocess.run(['sudo', 'sh', '-c', f"echo '{service_content}' > {SERVICE_FILE_PATH}"], check=True, stdout=subprocess.DEVNULL)
        
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['sudo', 'systemctl', 'enable', SERVICE_NAME], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['sudo', 'systemctl', 'start', SERVICE_NAME], check=True, stdout=subprocess.DEVNULL)
        print(f"{Fore.GREEN}   Servicio '{SERVICE_NAME}' habilitado e iniciado.{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}   Error CRÍTICO al instalar servicio. Error: {e}")

def detener_servicio_sistema():
    """Detiene y elimina el servicio  systemd."""
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'systemctl', 'disable', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(SERVICE_FILE_PATH):
            subprocess.run(['sudo', 'rm', SERVICE_FILE_PATH], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True, stdout=subprocess.DEVNULL)
    except Exception:
        print(f"{Fore.YELLOW}   Advertencia: El servicio podría no haber estado instalado.{Style.RESET_ALL}")