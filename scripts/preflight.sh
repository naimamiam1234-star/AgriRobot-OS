#!/usr/bin/env bash
set -eu
failed=0
for tool in debootstrap xorriso mksquashfs grub-mkrescue mformat chroot mount umount gpg; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "MISSING tool: $tool"; failed=1
    fi
done
python3 - <<'PY' || failed=1
from pathlib import Path
fields=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
cap=int(fields['CapEff'].strip(),16)
missing=[name for bit,name in [(18,'CAP_SYS_CHROOT'),(21,'CAP_SYS_ADMIN')] if not cap & (1<<bit)]
for name in missing: print('MISSING capability:',name)
raise SystemExit(bool(missing))
PY
if [ ! -f /usr/share/keyrings/ubuntu-archive-keyring.gpg ]; then
    echo 'MISSING Ubuntu archive keyring'; failed=1
fi
if [ "$(id -u)" != 0 ]; then echo 'MISSING root privileges'; failed=1; fi
exit "$failed"
