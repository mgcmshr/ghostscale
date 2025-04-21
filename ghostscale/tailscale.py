import subprocess
import json

class TailscaleManager:
    def __init__(self, command="tailscale"):
        self.command = command

    def get_exit_node(self):
        result = subprocess.run(
            [self.command, "status", "--json"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None
        try:
            data = json.loads(result.stdout)
            status = data.get("ExitNodeStatus")
            if status and status.get("Online"):
                return status["TailscaleIPs"][0].replace("/32", "")
            return None
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def set_exit_node(self, ip):
        subprocess.run([self.command, "set", f"--exit-node={ip}"])

    def unset_exit_node(self):
        subprocess.run([self.command, "set", "--exit-node="])