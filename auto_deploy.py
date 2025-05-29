#!/usr/bin/env python3
import os
import glob
import subprocess
import time
import paramiko

# === KONFIGURATION ===
# Sök efter .vmx-fil i "Documents/Virtual Machines"
def find_vmx():
    hemkatalog = os.environ.get("USERPROFILE", os.environ.get("HOME"))
    sökväg = os.path.join(hemkatalog, "Documents", "Virtual Machines")
    filer = glob.glob(os.path.join(sökväg, "**", "*.vmx"), recursive=True)
    if not filer:
        raise RuntimeError(f"Ingen .vmx-fil hittad under {sökväg}")
    return filer[0]

VMX_PATH = find_vmx()
SSH_HOST = "192.168.109.135"  # Uppdatera vid behov
SSH_PORT = 22
SSH_USER = "jacob"
SSH_PASSWORD = "."

# === STARTA VM I HEADLESS-LÄGE ===
def start_vm():
    """Starta VM utan grafiskt gränssnitt via vmrun"""
    print("Startar VM i headless-läge...")
    vmrun = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
    subprocess.run([vmrun, "start", VMX_PATH, "nogui"], check=True)
    print("VM startad")

# === VÄNTA PÅ SSH-ANSLUTNING ===
def wait_for_ssh(timeout=120):
    """Väntar på SSH-anslutning, kontrollerar porten tills den går att ansluta"""
    print("Väntar på SSH-anslutning...", end="", flush=True)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for _ in range(timeout):
        try:
            client.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD, timeout=5)
            client.close()
            print(" klar!")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(1)
    print("\nSSH-anslutning timeout")
    return False

# === KÖR KOMMANDO PÅ VM VIA SSH ===
def run_remote(cmd, sudo=False):
    """Kör kommando på VM via SSH, med sudo om så anges"""
    if sudo:
        cmd = f"echo '{SSH_PASSWORD}' | sudo -S sh -c \"{cmd}\""
    print(f"Kör på VM: {cmd}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD)
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    client.close()
    if out:
        print("OUTPUT:\n" + out)
    if err:
        print("FEL:\n" + err)

# === HUVUDPROGRAM ===
def main():
    # 1: Starta VM
    start_vm()

    # 2: Vänta kort så VM bootar klart
    time.sleep(5)

    # 3: Vänta på SSH-anslutning
    if not wait_for_ssh():
        return

    # 4: Uppdatera och uppgradera
    run_remote("DEBIAN_FRONTEND=noninteractive apt-get update -y && apt-get upgrade -y", sudo=True)

    # 5: Installera säkerhetspaket
    install_cmd = (
        "DEBIAN_FRONTEND=noninteractive apt-get install -y "
        "ufw fail2ban unattended-upgrades"
    )
    run_remote(install_cmd, sudo=True)

    # 6: Konfigurera brandvägg
    rules = [
        "ufw default deny incoming",
        "ufw default allow outgoing",
        "ufw allow OpenSSH",
        "ufw allow 80",
        "ufw --force enable"
    ]
    for rule in rules:
        run_remote(rule, sudo=True)

    # 7: Aktivera säkerhetstjänster
    for service in ["fail2ban", "unattended-upgrades"]:
        run_remote(f"systemctl enable {service}", sudo=True)

    # 8: Skapa autostartsskript för säkerhetsinitiering
    run_remote("mkdir -p /home/jacob/.config/autostart", sudo=True)
    run_remote(
        "cat << 'EOF' > /usr/local/bin/security_init.sh\n"
        "#!/bin/bash\n"
        "sudo ufw reload\n"
        "sudo apt-get update -y && sudo apt-get upgrade -y\n"
        "EOF",
        sudo=True
    )
    run_remote("chmod +x /usr/local/bin/security_init.sh", sudo=True)
    run_remote(
        "cat << 'EOF' > /home/jacob/.config/autostart/security_init.desktop\n"
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Exec=/usr/local/bin/security_init.sh\n"
        "Hidden=false\n"
        "NoDisplay=false\n"
        "X-GNOME-Autostart-enabled=true\n"
        "Name=Säkerhetsinitiering\n"
        "Comment=Kör brandvägg och uppdateringar vid inloggning\n"
        "EOF",
        sudo=True
    )
    run_remote("chown jacob:jacob /home/jacob/.config/autostart/security_init.desktop", sudo=True)

    # 9: Starta om VM
    run_remote("reboot", sudo=True)
    print("Alla steg klara, VM:n startas om")

if __name__ == "__main__":
    main()
