"""Boot the actual ISO with BIOS/UEFI and no NIC; retain serial evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

iso = str(Path(sys.argv[1]).resolve())
results = {}
for mode in ['bios','uefi']:
    path=Path('dist')/('boot-'+mode+'.log')
    cmd=['qemu-system-x86_64','-accel','tcg','-cpu','max','-m','4096','-smp','2',
         '-cdrom',iso,'-boot','d','-display','none','-serial','file:'+str(path),
         '-monitor','none','-nic','none','-no-reboot']
    if mode == 'uefi':
        shutil.copy('/usr/share/OVMF/OVMF_VARS_4M.fd','dist/OVMF_VARS.fd')
        cmd += ['-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
                '-drive','if=pflash,format=raw,file=dist/OVMF_VARS.fd']
    begin=time.monotonic();proc=subprocess.Popen(cmd)
    try:
        success=False
        while time.monotonic()-begin < 360 and proc.poll() is None:
            text=path.read_text(errors='replace') if path.exists() else ''
            if 'AGRIROBOT_BOOT_READY' in text: success=True;break
            if 'AGRIROBOT_BOOT_FAILED' in text: break
            time.sleep(2)
        results[mode]={'status':'passed' if success else 'failed',
                       'seconds_to_api_marker':round(time.monotonic()-begin,2),
                       'network':'no_NIC','ram_mib':4096,'cpus':2,'acceleration':'TCG'}
    finally:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
Path('dist/boot-validation.json').write_text(json.dumps(results,indent=2)+'\n')
Path('dist/OVMF_VARS.fd').unlink(missing_ok=True)
print(json.dumps(results,indent=2))
if not all(r['status']=='passed' for r in results.values()):sys.exit(1)
