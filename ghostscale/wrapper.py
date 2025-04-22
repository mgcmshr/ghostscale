import subprocess
import os
from pathlib import Path
import yaml

WRAPPER_DIR = Path.home() / ".local/bin"

class WrapperCreator:
    def __init__(self, wrapper_dir=WRAPPER_DIR, tailscale_cmd="tailscale"):
        self.wrapper_dir = wrapper_dir
        self.tailscale_cmd = tailscale_cmd

    def create_wrapper(self, prog_name, config):
        self.wrapper_dir.mkdir(parents=True, exist_ok=True)
        wrapper_path = self.wrapper_dir / prog_name

        # Wenn der Dienst deaktiviert ist, entferne bestehenden Wrapper und beende
        if not config.get("enabled", True):
            if wrapper_path.exists():
                wrapper_path.unlink()
                print(f"[Ghostscale] Deaktiviert: Wrapper für {prog_name} wurde entfernt.")
            else:
                print(f"[Ghostscale] Deaktiviert: Kein aktiver Wrapper für {prog_name} vorhanden.")
            return

        real_path = subprocess.run(["which", prog_name], capture_output=True, text=True).stdout.strip()

        mode = config.get("mode", "always")
        trigger_cmds = config.get("trigger_commands", [])
        exit_node_ip = config.get("exit_node", "100.100.100.100")
        include_remotes = config.get("include_remotes", [])
        exclude_remotes = config.get("exclude_remotes", [])

        proxy_host = config.get("proxy_host")
        proxy_user = config.get("proxy_user")
        proxy_port = config.get("proxy_port", 1080)
        proxy_password = config.get("proxy_password", "")
        proxy_server = config.get("proxy_server", f"socks5://localhost:{proxy_port}")

        with open(wrapper_path, "w") as f:
            if mode == "proxy":
                f.write(f"""#!/bin/bash

# Ghostscale Proxy Wrapper for {prog_name}

PROXY_PORT={proxy_port}
PROXY_USER={proxy_user}
PROXY_HOST={proxy_host}
PROXY_SERVER={proxy_server}
PROXY_PASSWORD={proxy_password}

TUNNEL_RUNNING=$(lsof -i :$PROXY_PORT | grep ssh)

if [ -z "$TUNNEL_RUNNING" ]; then
  echo "[Ghostscale] Starte Proxy-Tunnel auf Port $PROXY_PORT ..."
  sshpass -p "$PROXY_PASSWORD" ssh -f -N -D $PROXY_PORT $PROXY_USER@$PROXY_HOST
  sleep 1
fi

exec {real_path} --proxy-server="$PROXY_SERVER" "$@"
""")
            else:
                f.write(f"""#!/bin/bash

# Ghostscale Wrapper for {prog_name}

function cleanup() {{
    {self.tailscale_cmd} set --exit-node=
}}
trap cleanup EXIT INT TERM

MODE={mode}
CMD=\"$1\"

SHOULD_ACTIVATE=false

if [[ \"$MODE\" == \"always\" ]]; then
    SHOULD_ACTIVATE=true
elif [[ \"$MODE\" == \"smart\" ]]; then
    for trigger in {' '.join(trigger_cmds)}; do
        if [[ \"$CMD\" == \"$trigger\" ]]; then
            SHOULD_ACTIVATE=true
        fi
    done
fi

if $SHOULD_ACTIVATE; then
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [[ -n \"$REMOTE\" ]]; then
        INCLUDE_MATCH=false
        for inc in {' '.join(include_remotes)}; do
            if [[ \"$REMOTE\" == *$inc* ]]; then
                INCLUDE_MATCH=true
            fi
        done

        for exc in {' '.join(exclude_remotes)}; do
            if [[ \"$REMOTE\" == *$exc* ]]; then
                echo \"[Ghostscale] Remote $REMOTE ist ausgeschlossen. Kein VPN aktiviert.\"
                SHOULD_ACTIVATE=false
            fi
        done

        if [[ {"true" if include_remotes else "false"} == true && $INCLUDE_MATCH == false ]]; then
            echo \"[Ghostscale] Remote $REMOTE ist nicht erlaubt. Kein VPN aktiviert.\"
            SHOULD_ACTIVATE=false
        fi
    fi
fi

if $SHOULD_ACTIVATE; then
    echo \"[Ghostscale] Aktiviere Exit Node...\"
    {self.tailscale_cmd} set --exit-node={exit_node_ip}
fi

{real_path} \"$@\"
""")
        os.chmod(wrapper_path, 0o755)
        print(f"Wrapper erstellt: {wrapper_path}")