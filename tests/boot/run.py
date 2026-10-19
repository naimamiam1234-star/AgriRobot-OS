"""Boot the actual ISO with BIOS/UEFI and no NIC; retain serial evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

def boot(mode, iso, output, timeout=360, poll_interval=2):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    path=output/('boot-'+mode+'.log')
    # Remove previous evidence before the child can start; never trust stale markers.
    path.unlink(missing_ok=True)
    cmd=['qemu-system-x86_64','-accel','tcg','-cpu','max','-m','4096','-smp','2',
         '-cdrom',str(iso),'-boot','d','-display','none','-serial','file:'+str(path),
         '-monitor','none','-nic','none','-no-reboot']
    variables=output/'OVMF_VARS.fd'
    if mode == 'uefi':
        shutil.copy('/usr/share/OVMF/OVMF_VARS_4M.fd',variables)
        cmd += ['-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd',
                '-drive','if=pflash,format=raw,file='+str(variables)]
    begin=time.monotonic();proc=subprocess.Popen(cmd)
    try:
        success=False
        while time.monotonic()-begin < timeout and proc.poll() is None:
            text=path.read_text(errors='replace') if path.exists() else ''
            if 'AGRIROBOT_BOOT_READY' in text: success=True;break
            if 'AGRIROBOT_BOOT_FAILED' in text: break
            time.sleep(poll_interval)
        return {'status':'passed' if success else 'failed',
                'seconds_to_api_marker':round(time.monotonic()-begin,2),
                'network':'no_NIC','ram_mib':4096,'cpus':2,'acceleration':'TCG',
                'scope':'guest_API_readiness_only_inference_tested_separately_in_rootfs'}
    finally:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        variables.unlink(missing_ok=True)


def main():
    iso = str(Path(sys.argv[1]).resolve())
    results={mode:boot(mode,iso,'dist') for mode in ['bios','uefi']}
    Path('dist/boot-validation.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
    if not all(r['status']=='passed' for r in results.values()):sys.exit(1)


if __name__=='__main__':main()
