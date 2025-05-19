# OwnVM
# Automatiserad Deployment av Debian-VM

## Syfte
Automatisera uppstart och konfiguration av en Debian-VM för att effektivisera utvecklings- och testmiljöer.

## Funktionalitet
- Startar en lokal Debian-VM via VirtualBox.
- Klonar ett specificerat GitHub-repo direkt in i VM:en.

## Användningsinstruktioner
1. Se till att VirtualBox är installerat och att en VM med namnet "debian-vm" finns.
2. Uppdatera `repo_url` och `vm_ip` i `auto_deploy.py` med dina specifika värden.
3. Kör skriptet via Anaconda:
   ```bash
   python auto_deploy.py
