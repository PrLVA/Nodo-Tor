import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
import time

def run_command(command):
    """Ejecuta un comando en la terminal y retorna su salida o error."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def install_tor():
    """Instala Tor si no está presente."""
    output_text.insert(tk.END, "Actualizando paquetes e instalando Tor...\n")
    output_text.update()
    run_command("sudo apt update")
    result = run_command("sudo apt install tor -y")
    output_text.insert(tk.END, result + "\n")
    if "error" not in result.lower():
        output_text.insert(tk.END, "Tor instalado correctamente.\n")
    else:
        output_text.insert(tk.END, "Fallo al instalar Tor. Verifica tu conexión o permisos.\n")

def configure_torrc(nickname, contact_email, or_port, bandwidth_rate):
    """Configura el archivo torrc para un nodo intermedio."""
    torrc_path = "/etc/tor/torrc"
    config = f"""
Nickname {nickname}
ContactInfo {contact_email}
ORPort {or_port}
ExitRelay 0
SocksPort 0
RelayBandwidthRate {bandwidth_rate}
RelayBandwidthBurst {int(bandwidth_rate.split()[0]) * 2} KB
"""
    try:
        with open("torrc_temp", "w") as f:
            f.write(config)
        run_command(f"sudo mv torrc_temp {torrc_path}")
        run_command(f"sudo chown root:root {torrc_path}")
        run_command(f"sudo chmod 644 {torrc_path}")
        output_text.insert(tk.END, f"Archivo {torrc_path} configurado como nodo intermedio.\n")
    except Exception as e:
        output_text.insert(tk.END, f"Error al configurar torrc: {e}\n")

def restart_tor():
    """Reinicia el servicio de Tor."""
    output_text.insert(tk.END, "Reiniciando Tor...\n")
    output_text.update()
    result = run_command("sudo systemctl restart tor")
    time.sleep(2)
    status = run_command("sudo systemctl status tor")
    output_text.insert(tk.END, result + "\n")
    if "active (running)" in status:
        output_text.insert(tk.END, "Tor reiniciado y corriendo correctamente.\n")
    else:
        output_text.insert(tk.END, "Tor no está corriendo. Revisa los logs.\n")

def check_tor_logs():
    """Muestra las últimas líneas de los logs de Tor."""
    output_text.insert(tk.END, "\nMostrando últimas líneas de los logs de Tor...\n")
    logs = run_command("sudo tail -n 20 /var/log/tor/log")
    output_text.insert(tk.END, logs + "\n")

def start_configuration():
    """Inicia el proceso de configuración del nodo."""
    nickname = entry_nickname.get().strip()[:19]
    contact_email = entry_email.get().strip()
    or_port = entry_port.get().strip() or "9001"
    bandwidth_rate = entry_bandwidth.get().strip() or "100 KB"

    if not nickname or " " in nickname:
        messagebox.showerror("Error", "El nombre del nodo no debe estar vacío ni contener espacios.")
        return
    if not contact_email:
        messagebox.showerror("Error", "Ingresa un correo de contacto.")
        return

    output_text.delete(1.0, tk.END)  # Limpia el área de texto
    install_tor()
    configure_torrc(nickname, contact_email, or_port, bandwidth_rate)
    restart_tor()
    output_text.insert(tk.END, f"\nRecuerda abrir el puerto {or_port} en tu router/firewall.\n")
    output_text.insert(tk.END, "Verifica tu nodo en https://metrics.torproject.org/rs.html después de unas horas.\n")

def show_logs():
    """Muestra los logs de Tor en el área de texto."""
    output_text.delete(1.0, tk.END)
    check_tor_logs()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Configurador de Nodo Tor")
root.geometry("600x500")

# Etiquetas y campos de entrada
tk.Label(root, text="Nombre del nodo (máx. 19 caracteres, sin espacios):").pack(pady=5)
entry_nickname = tk.Entry(root)
entry_nickname.pack()

tk.Label(root, text="Correo de contacto (será público):").pack(pady=5)
entry_email = tk.Entry(root)
entry_email.pack()

tk.Label(root, text="Puerto ORPort (Enter para 9001):").pack(pady=5)
entry_port = tk.Entry(root)
entry_port.pack()

tk.Label(root, text="Límite de ancho de banda (ej. '100 KB', Enter para predeterminado):").pack(pady=5)
entry_bandwidth = tk.Entry(root)
entry_bandwidth.pack()

# Botones
tk.Button(root, text="Configurar Nodo", command=start_configuration).pack(pady=10)
tk.Button(root, text="Ver Logs", command=show_logs).pack(pady=5)

# Área de texto para salida
output_text = scrolledtext.ScrolledText(root, width=70, height=20)
output_text.pack(pady=10)

# Nota inicial
output_text.insert(tk.END, "Nota: Este script debe ejecutarse con 'sudo python3 script.py'.\n")

# Iniciar la ventana
root.mainloop()