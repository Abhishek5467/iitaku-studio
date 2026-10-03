"""Portable local-only GLB folder watcher. Stops with Ctrl+C."""
import argparse
import shutil
import time
from pathlib import Path
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--target",required=True);a=p.parse_args();source=Path(a.source).resolve();target=Path(a.target).resolve()
    if source==target or source in target.parents:p.error("Use separate folders; target must not be inside source")
    if not source.is_dir():p.error("Source folder does not exist")
    target.mkdir(parents=True,exist_ok=True);seen={};pending={};print("Watching GLB exports. Ctrl+C stops. Git push remains manual.",flush=True)
    try:
        while True:
            for f in source.glob("*.glb"):
                try:
                    stat=f.stat();stamp=(stat.st_mtime_ns,stat.st_size)
                    if stat.st_size and seen.get(f.name)!=stamp:
                        if pending.get(f.name)==stamp:
                            temp=target/(f.name+".copying");shutil.copy2(f,temp);temp.replace(target/f.name);seen[f.name]=stamp;print(f"Updated {f.name}",flush=True)
                        else:pending[f.name]=stamp
                except (FileNotFoundError,PermissionError):continue
            time.sleep(2)
    except KeyboardInterrupt:print("Watcher stopped.")
