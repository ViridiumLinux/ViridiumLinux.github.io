# Viridium Linux

Viridium is a minimal, Arch-based Linux distro. Under the hood it's just Arch — same packages, same repos, same everything — but it comes with its own installer and its own way of managing packages, built around one idea: **you shouldn't need two different tools (pacman and an AUR helper) to manage your system.**

That one tool is `vbuild`. There's also `viridium`, a small command for everyday maintenance. Both are covered below.

## Installing it

Boot the live environment and run:

```bash
vinstall
```

It'll walk you through picking a kernel, hostname, timezone, and username, then ask how you want to partition:

- **Wipe the whole disk** — simplest option if this is the only OS going on the machine.
- **Use existing partitions** — pick a root partition to install onto and an EFI partition to boot from. If you're dual-booting, point it at your existing EFI partition rather than making a new one — Viridium won't touch anything else already there (like a Windows or existing Arch entry), it just adds itself alongside.

Each destructive step asks for a typed confirmation before it does anything, so there's a chance to back out if you picked the wrong disk.

You'll need UEFI firmware and a network connection for the install to complete — it downloads packages as it goes, the same way a normal Arch install does.

Once it's done and you reboot, you'll land on a login prompt. The first time you log in, you'll get a short one-time message explaining the pacman/vbuild thing below — after that it won't show again. Your user is already set up with `sudo`, so you're ready to go right away.

## Day to day: installing and updating things

This is the main thing that's different about Viridium. `vbuild` is your package manager — it searches and installs from both the official Arch repos and the AUR, so you never have to think about which one something comes from:

```bash
vbuild -S firefox     # install something
vbuild -Ss firefox     # not sure of the exact name? search first
vbuild -Syu            # update everything
vbuild -Rns firefox    # remove something, and anything it needed that's now unused
vbuild -Yc             # clean up leftover orphaned packages
```

If you've used `pacman` or `yay` before, these flags will feel familiar — that's on purpose.

For quicker day-to-day use, `viridium` wraps the common ones:

```bash
viridium update    # same as vbuild -Syu
viridium clean      # same as vbuild -Yc
viridium info        # kernel, hostname, uptime, package count
viridium doctor      # checks DNS, disk space, orphaned packages, etc.
```

Run `viridium help` any time for the full list.

### Why can't I just use pacman?

You'll notice `pacman` and `yay` themselves refuse to run directly — that's intentional, not a bug. It's there so you always go through `vbuild`, which keeps the repo and AUR sides of things in sync. If you type one of them by mistake, Viridium will actually notice and offer to run the equivalent `vbuild` command for you on the spot, so it's rarely more than pressing enter.

If you genuinely need the real, unmodified tools — say, a script that expects stock pacman behaviour — you can open them back up temporarily:

```bash
sudo viridium unlock       # allows real pacman/yay for 10 minutes
sudo viridium unlock 30    # or specify how long
sudo viridium lock         # re-lock early, if you're done sooner
```

They lock themselves back up automatically once the timer's up, so there's nothing to remember to undo.

## Getting online

NetworkManager is running out of the box. If you're not on ethernet:

```bash
nmtui
```

is the easiest way to connect to Wi-Fi — a simple text menu, no flags to remember. `nmcli` is there too if you'd rather script it.

## When something's not working

**`viridium doctor`** is the first thing to reach for — it checks the usual suspects (DNS, disk space, orphaned packages, failed services) and tells you plainly what it finds. Add `--fix` and it'll sort out what it safely can on its own.

**Running low on disk space?**
```bash
viridium clean
```
clears out orphaned packages, which is usually most of it.

**Need the real pacman/yay for something specific?** See the unlock command above.

**Can't boot at all?** Everything under the hood is standard Arch, so normal Arch recovery steps apply — boot a live USB, mount your root partition, and go from there. The one Viridium-specific detail worth knowing: the root filesystem is labelled `viridium_root`, which can help you identify it quickly with `lsblk -f`.
