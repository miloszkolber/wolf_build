"""Retain Cargo dependency license declarations and available license texts."""
import json
from pathlib import Path
import re
import shutil
import subprocess

metadata=json.loads(subprocess.check_output(["cargo","metadata","--locked","--format-version=1"]))
root=Path("/opt/wolf-runtime/share/licenses/rust")
root.mkdir(parents=True,exist_ok=True)
inventory=[]
for package in metadata["packages"]:
    directory=Path(package["manifest_path"]).parent
    target=root/(package["name"]+"-"+package["version"])
    target.mkdir(exist_ok=True)
    files=[p for p in directory.iterdir() if p.is_file() and re.match(r"(?i)(license|licence|copying|copyright|notice)",p.name)]
    if package.get("license_file"): files.append(directory/package["license_file"])
    for path in files:
        if path.is_file(): shutil.copyfile(path,target/path.name)
    inventory.append({k:package.get(k) for k in ("name","version","license","source")})
(root/"inventory.json").write_text(json.dumps(inventory,indent=2)+"\n")
