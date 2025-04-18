import subprocess
import os
from pathlib import Path

WRAPPER_DIR = Path.home() / ".local/bin"

class WrapperCreator:
    def __init__(self, wrapper_dir=WRAPPER_DIR, tailscale_cmd="tailscale"):
        self.wrapper_dir = wrapper_dir
        self.tailscale_cmd = tailscale_cmd

    def create_wrapper(self, prog_name, config):
        self.wrapper_dir.mkdir(parents=True, exist_ok=True)
        wrapper_path = self.wrapper_dir / prog_name
        real_path = subprocess.run(["which", prog_name], capture_output=True, text=True).stdout.strip()

        mode = config.get("mode", "always")
        trigger_cmds = config.get("trigger_commands", [])
        exit_node_ip = config.get("exit_node", "100.100.100.100")

        with open(wrapper_path, "w") as f:
            f.write(f"""#!/bin/bash

# Ghostscale Wrapper for {prog_name}

function cleanup() {{
    {self.tailscale_cmd} set --exit-node=
}}
trap cleanup EXIT INT TERM

MODE={mode}
CMD="$1"

if [[ "$MODE" == "always" || "$MODE" == "smart" && " {' '.join(trigger_cmds)} " =~ "$CMD" ]]; then
    {self.tailscale_cmd} set --exit-node={exit_node_ip}
fi

{real_path} "$@"
""")
        os.chmod(wrapper_path, 0o755)
        print(f"Wrapper erstellt: {wrapper_path}")