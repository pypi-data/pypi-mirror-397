import os
import subprocess
from pathlib import Path

def run(cmd):
    env = os.environ.copy()
    env["XKID_DEVICE_EXTERNAL"] = "1"
    env["XKID_DEVICE_KID"] = "sha256:deadbeef"

    p = subprocess.run(
        cmd,
        cwd=Path(__file__).parents[1],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return json.loads(p.stdout)
