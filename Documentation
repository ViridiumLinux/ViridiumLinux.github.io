Viridium Linux is a minimal Arch-based Linux system, with its own custom package manager, and more.
Base:
Arch Linux

Installer:
vinstall 1.0

Custom Packages:
vbuild (package manager)
viridium (Control Center)

Init System:
systemd-boot


Installation process:

vinstall

You choose:
Kernel — linux, linux-zen, linux-lts, or linux-hardened
Hostname (default: viridium)
Timezone
Username (gets sudo)
Mode — wipe whole disk, use existing partitions, or cancel

Whole disk: erases the drive, creates EFI + root.
Existing partitions: formats the root you pick; leaves EFI alone.
Type the confirmations exactly: ERASE, FORMAT, or yes. Reboot when done.
Needs UEFI, network, and a root partition of at least ~1 GiB.

First login
A short welcome shows once. Your user is in the wheel group (sudo works).

Commands:

viridium:

viridium update          Update the system
viridium clean           Remove orphaned packages
viridium doctor          Health checks
viridium doctor --fix    Checks + simple fixes (needs sudo)
viridium history [N]     Last N package changes (default 20)
viridium unlock [MIN]    Allow pacman/yay for MIN minutes
viridium lock            Lock them again
viridium info            Kernel, hostname, uptime, package count
viridium help            Show this list

vbuild:

vbuild -Syu
vbuild -S name
vbuild -Rns name
vbuild -Ss query


Temporary unlock if you need to:
sudo viridium unlock - Default is 10 minutes
sudo viridium unlock 30 - Unlocks pacman and yay for 30 minutes
sudo viridium lock - Locks pacman and yay

Networking:

NetworkManager is enabled at boot.

nmtui
nmcli device wifi list
nmcli device wifi connect "SSID" password "…"
nmcli device status

What’s included

- Chosen kernel + firmware
- NetworkManager
- sudo, bash, vim, kitty, fastfetch
- systemd-boot


NOTES:
No desktop or window manager. Add one later if you want:

pacman/yay blocked
Use vbuild - its faster and more versitile.

No network / DNS
nmtui, then viridium doctor

Disk full
viridium clean, df -h /

Need full Arch tools
sudo viridium unlock 60
Boot uses systemd-boot and root label viridium_root. For serious recovery, boot a live USB, mount the system, or unlock and use normal Arch docs.
