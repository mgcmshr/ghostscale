import subprocess

class TailscaleManager:
    def __init__(self, command="tailscale"):
        self.command = command

    def get_exit_node(self):
        result = subprocess.run([self.command, "status"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Exit" in line:
                return line
        return None

    def set_exit_node(self, ip):
        subprocess.run([self.command, "set", f"--exit-node={ip}"])

    def unset_exit_node(self):
        subprocess.run([self.command, "set", "--exit-node="])