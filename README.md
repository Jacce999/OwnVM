# OwnVM – Automatiserat Deployment- och Säkerhetsskript

# https://www.youtube.com/watch?v=SX_FdmiyD0M

## 1. Inledning
I dagens moderna IT-miljöer besitter automatisering en viktig roll för att begränsa manuella fel och säkerställa konsekventa konfigurationer. Denna artikel ger en helautomatiserad lösning för provisionering och säkerhet av Debian 12 VM inom VMware Workstation Pro.

## 2. Syfte
Instructions
För Godkänt (G) på arbetet skall följande krav uppfyllas:
● Skriptet ska korrekt automatisera deployment och
konfiguration av en virtuell miljö enligt uppgiftens
specifikationer.
● En tydlig beskrivning av skriptets syfte, funktionalitet
och användningsinstruktioner ska ingå.
● Rapporten skall ha en diskussion kring eventuella
problem som uppstod, samt hur du har löst dem.
● Skriptet ska vara läsbart och kommenterat.

För Väl Godkänt (VG) på arbetet skall följande krav uppfyllas:
● Skriptet ska inkludera ytterligare funktioner, såsom
t.ex. automatiserad säkerhetskonfiguration,
felhantering eller inloggning av användare.
● En genomtänkt diskussion kring skriptets potentiella
förbättringsområden och dess tillämpbarhet i olika
scenarier.

## 3. Funktionalitet
1. **Start av VM**
Kör `vmrun start <VMX_PATH> nogui` för headless-boot.
2. **Väntar på SSH**
Pollar port 22 (max 120 s) via Paramiko tills SSH-servern svarar.
3. **Systemuppdatering**
`DEBIAN_FRONTEND=noninteractive apt-get update && apt-get upgrade -y`
4. **Installation av säkerhetspaket**
Installerar `ufw`, `fail2ban` och `unattended-upgrades`.
5. **Brandväggskonfiguration**
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80
ufw --force enable
```
6. **Enabling av säkerhetstjänster**
```bash
systemctl enable fail2ban
systemctl enable unattended-upgrades
```
7. **Autostart för kontinuerlig säkerhetsinitiering**
- Installs `/usr/local/bin/security_init.sh`:
```bash
#!/bin/bash
sudo ufw reload

sudo apt-get update -y && sudo apt-get upgrade -y
```
- Installs `.desktop` to `/home/jacob/.config/autostart`.
8. **Reboot**
Ends with `reboot` so all services will start correctly.

## 4. Video Walkthrough
In detaljerad genomgång hittar du här:
https://www.youtube.com/watch?v=SX_FdmiyD0M

## 5. Användningsinstruktioner
1. Klona repot:
```bash
git clone https://github.com/Jacce999/OwnVM.git
cd OwnVM
```
2. Anpassa `SSH_HOST` i `auto_run1.py` till din VM:s IP.
3. Installera beroenden:
```bash
pip install paramiko
```
4. Kör skriptet från Windows PowerShell:
```powershell
cd C:\\\sökväg\\\till\\\OwnVM
python .\auto_run1.py
```
5. On reboot, check in VM:
```bash
sudo ufw status verbose
systemctl is-enabled fail2ban
systemctl is-enabled unattended-upgrades
ls -l /usr/local/bin/security_init.sh
```

## 6. Problem och lösningar
| Problem | Lösning |
|----------------------------------|---------------------------------------------------------------|
| Gränssnitt `ens33` var nedstängt | Aktivera med `ip link set ens33 up && dhclient ens33` eller auto i `/etc/network/interfaces`. |
| Timeout på SSH-polling | Lagt till `time.sleep(5)` efter VM-start och ökad max-tid. |
| Interaktiva apt-dialoger | Använder `DEBIAN_FRONTEND=noninteractive` och Dpkg-options. |

## 7. Ytterligare funktioner (VG)
- Automated säkerhetsconfig (UFW, Fail2Ban, Unattended-Upgrades)
- Non-interactive error-handling för apt-kommandon
- Autostart-skript för kontinuerlig säkerhetsinitiering
- Tydliga och svenskspråkiga kommentarer i koden

## 8. Improvement areas & Applicability
- **SSH-key-auhtentisering** i stället för lösenord för ökad säkerhet.
- **Loggning** av script-körning till fil (exempel: `/var/log/deploy.log`).
- **Modulärt** så att flera VM-typer eller distributioner understöds.
- **CI/CD**-integration (GitHub Actions, Jenkins) för automatiserad test och deploy.
- **Skalning**: parametrisation för bulk-provisioning av ett antal containrar eller VM:er.
