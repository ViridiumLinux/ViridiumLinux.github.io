# Viridium Linux

Viridium Linux is a minimal, Arch-based Linux distribution built around a custom installation and package-management system.

Viridium uses the Arch Linux package ecosystem, including the official repositories and the AUR. The underlying system remains familiar to Arch users, while Viridium adds its own tools and conventions on top.

The main components are:

* `vinstall` — the Viridium installation system
* `vbuild` — the primary package manager
* `viridium` — system management and maintenance utility
* NetworkManager — network configuration
* `systemd-boot` — bootloader used by the installer

The main design goal is to keep the normal Arch package ecosystem while simplifying package management. In particular, `vbuild` combines the official repositories and the AUR into a single package-management interface instead of requiring separate tools for each.

`vbuild` also uses a faster workflow than the traditional `pacman` + AUR helper setup.

---

# Installation

## Requirements

A Viridium installation requires:

* A UEFI-capable system
* A network connection
* A disk with 5gb of space for the minimal installation (Though i recommend more than 20gb.)

Viridium currently installs through the live environment and downloads packages during installation.

## Starting the installer

Boot the Viridium live environment and run:

```bash id="y8z8p6"
vinstall
```

The installer handles the initial system setup, filesystem configuration, package installation, user creation, and bootloader configuration.

## Installation options

`vinstall` provides two main disk configuration modes.

### Wipe the entire disk

This mode partitions the selected disk automatically and installs Viridium onto it.

It is intended for systems where Viridium will be the only operating system on the disk.

Because this mode is destructive, the installer requires an explicit typed confirmation before continuing.

### Use existing partitions

Existing partitions can be selected instead of partitioning an entire disk.

At minimum, the installation requires:

* A root filesystem partition
* An EFI System Partition

This mode is intended for existing installations and dual-boot configurations.

An existing EFI System Partition can be reused. Viridium does not need to create a new EFI partition when one is already available.

Existing boot entries are left in place. For example, a Windows Boot Manager entry can remain alongside the Viridium boot entry.

Destructive operations require confirmation before they are performed.

## Kernel selection

The installer allows the kernel to be selected during installation.

The selected kernel is installed into the new system and used for normal booting.

## Hostname

The hostname is configured during installation.

This becomes the system hostname after the first boot.

## Timezone

A timezone is selected during installation and applied to the installed system, which you choose!

## User creation

A user account is created during installation.

The account is configured for `sudo`, allowing administrative commands to be run without logging into the root account directly.

## Bootloader

Viridium installs and configures `systemd-boot` on UEFI systems.

The bootloader is installed to the EFI System Partition selected during installation.

## Network requirements

An internet connection is required during installation because packages are downloaded from the configured repositories.

---

# Package management

## vbuild

`vbuild` is the primary package manager in Viridium.

It is designed around two main problems with the traditional Arch package-management workflow:

1. Official repository packages and AUR packages normally require different tools.
2. Using a separate AUR helper alongside `pacman` adds extra overhead to package management.

`vbuild` combines both sources into one interface.

A package does not need to be handled differently just because it comes from the AUR rather than an official repository.

The command syntax is intentionally similar to `pacman`, making the transition easier for existing Arch users.

## Package sources

`vbuild` can work with:

* Official Arch Linux repositories
* The Arch User Repository (AUR)

The official repositories remain the primary source for packages where available. The AUR provides additional packages that are not available in the official repositories.

`vbuild` handles the distinction internally.

## Installing packages

```bash id="4m5q0k"
vbuild -S package
```

For example:

```bash id="f6h0qn"
vbuild -S firefox
```

The package can come from the official repositories or the AUR.

## Searching

```bash id="7b8u5u"
vbuild -Ss search-term
```

For example:

```bash id="fprx6x"
vbuild -Ss firefox
```

This searches the available package sources.

## Updating the system

```bash id="svz5m2"
vbuild -Syu
```

This updates the installed system using the configured repositories and AUR sources.

## Removing packages

```bash id="7a2w4e"
vbuild -Rns package
```

This removes the selected package and cleans up dependencies that are no longer required.

## Cleaning orphaned packages

```bash id="k3w7w5"
vbuild -Yc
```

This removes packages that are no longer required by another installed package.

## Why vbuild exists

The primary reason for `vbuild` is the combination of the official repositories and AUR.

A normal Arch setup often looks like:

```text
pacman → official repositories
yay    → AUR
```

Viridium instead uses:

```text
vbuild → official repositories + AUR
```

This means package installation, searching, and updates can all be handled through one tool.

`vbuild` is also designed to reduce the overhead involved in the traditional two-tool workflow, making common package operations faster.

---

# pacman and yay

## Default behaviour

Direct use of `pacman` and `yay` is disabled by default.

This is intentional, as vbuild is our faster alternative.

Allowing every package operation to be performed through several different tools would undermine the purpose of `vbuild`. Viridium expects normal package management to go through `vbuild`.

This also keeps the official-repository and AUR workflows together instead of having separate package-management paths.

## Command detection

If `pacman` or `yay` is run directly, Viridium detects the command.

Instead of simply failing, the system can show the equivalent `vbuild` command and offer to run it.

For example, a command intended for `pacman` can be translated into the corresponding `vbuild` operation.

## Unlocking the original tools

Some software may genuinely require the normal `pacman` or `yay` binaries.

The tools can therefore be temporarily unlocked.

```bash id="5vqu6m"
sudo viridium unlock
```

This enables the original tools for the default unlock period.

A custom duration can be specified in minutes:

```bash id="8g5k5v"
sudo viridium unlock 30
```

The tools can also be locked manually:

```bash id="5s5j50"
sudo viridium lock
```

The unlock automatically expires after the configured period, returning the system to the normal Viridium package-management setup.

---

# viridium

`viridium` is the general system-management command.

Unlike `vbuild`, which focuses on packages, `viridium` handles common maintenance tasks and system information.

## Help

```bash id="2z6k4a"
viridium help
```

Displays the available commands.

## Updating

```bash id="5a8q0y"
viridium update
```

Runs the normal system update through `vbuild`.

Equivalent to:

```bash id="6f8j7d"
vbuild -Syu
```

## Cleaning

```bash id="0b2m3x"
viridium clean
```

Cleans up orphaned packages and other removable package data.

Equivalent to:

```bash id="7k7x8n"
vbuild -Yc
```

## System information

```bash id="d5s0t4"
viridium info
```

Displays basic information about the current installation, including:

* Kernel
* Hostname
* Uptime
* Installed package count

## Diagnostics

```bash id="v6y2j1"
viridium doctor
```

`viridium doctor` checks the system for common problems.

Checks include:

* DNS
* Disk space
* Orphaned packages
* Failed services
* Other basic system conditions

The output is intended to explain the problem rather than simply returning an error code.

### Automatic fixes

Some problems can be fixed automatically:

```bash id="1u4n3h"
viridium doctor --fix
```

Only issues that can be safely handled automatically are modified.

---

# Networking

Viridium uses NetworkManager for network management.

NetworkManager is enabled by default after installation.

## nmtui

For an interactive terminal interface:

```bash id="5v3e7s"
nmtui
```

`nmtui` provides a text-based menu for connecting to Wi-Fi and managing network connections.

## nmcli

`nmcli` can also be used for command-line network configuration.

It is useful for scripting or users who prefer direct command-line control.

---

# First login

The first login after installation includes a one-time information message.

The message explains the Viridium package-management setup, including:

* `vbuild`
* `pacman`
* `yay`
* The reason `pacman` and `yay` are normally locked

The message is only shown once.

Afterwards, normal logins go directly to the shell.

---

# System maintenance

Viridium's maintenance tools are intended to cover the most common tasks without requiring the user to remember multiple commands.

A basic maintenance routine can therefore be done with:

```bash id="xw4i6c"
viridium update
viridium doctor
viridium clean
```

`vbuild` remains available when more direct package-management control is required.

## Running low on disk space

The first thing to check is usually:

```bash id="q7u6j2"
viridium clean
```

This removes orphaned packages and other package data that is no longer required.

For a more detailed check of the system:

```bash id="4y5k1q"
viridium doctor
```

---

# Command reference

## vbuild

| Command               | Purpose                                  |
| --------------------- | ---------------------------------------- |
| `vbuild -S package`   | Install a package                        |
| `vbuild -Ss term`     | Search for packages                      |
| `vbuild -Syu`         | Update the system                        |
| `vbuild -Rns package` | Remove a package and unused dependencies |
| `vbuild -Yc`          | Remove orphaned packages                 |

## viridium

| Command                 | Purpose                               |
| ----------------------- | ------------------------------------- |
| `viridium help`         | Show available commands               |
| `viridium update`       | Update the system                     |
| `viridium clean`        | Clean orphaned packages               |
| `viridium info`         | Display system information            |
| `viridium doctor`       | Check for common problems             |
| `viridium doctor --fix` | Automatically fix supported problems  |
| `viridium unlock`       | Temporarily unlock `pacman` and `yay` |
| `viridium unlock 30`    | Unlock for 30 minutes                 |
| `viridium lock`         | Lock `pacman` and `yay` immediately   |

## Networking

| Command | Purpose                                  |
| ------- | ---------------------------------------- |
| `nmtui` | Interactive NetworkManager configuration |
| `nmcli` | Command-line NetworkManager control      |

---

# Design overview

Viridium keeps the underlying Arch ecosystem rather than creating a separate package ecosystem.

The main additions are the tools surrounding it:

```text
                    Viridium Linux
                          │
          ┌───────────────┴───────────────┐
          │                               │
       vinstall                        Runtime
          │                               │
    System setup                ┌─────────┴─────────┐
                                │                   │
                              vbuild            viridium
                                │                   │
                     ┌──────────┴──────────┐        │
                     │                     │        │
                 Arch repos               AUR    Maintenance
```

This keeps Viridium compatible with the Arch package ecosystem while giving the distribution its own installation and management workflow.

The goal is not to replace the Arch ecosystem, but to provide a simpler interface around it — particularly for users who want official repository and AUR packages handled through one tool without giving up the underlying Arch system.
