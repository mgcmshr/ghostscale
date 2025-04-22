import subprocess
import json

class TailscaleManager:
    def __init__(self, command="tailscale"):
        self.command = command

    def set_exit_node(self, ip):
        subprocess.run([self.command, "set", f"--exit-node={ip}"])

    def unset_exit_node(self):
        subprocess.run([self.command, "set", "--exit-node="])

    def list_exit_nodes(self):
        data = self.get_status_json()
        exit_nodes = []
        for peer in data.get("Peer", {}).values():
            if peer.get("ExitNode", False):
                exit_nodes.append({
                    "host": peer.get("HostName"),
                    "ip": peer.get("TailscaleIPs", ["?"])[0],
                    "online": peer.get("Online", False)
                })
        return exit_nodes
        
    def get_status_json(self):
        result = subprocess.run([self.command, "status", "--json"], capture_output=True, text=True)
        if result.returncode != 0:
            return {}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}

    def get_exit_node(self):
        data = self.get_status_json()
        status = data.get("ExitNodeStatus")
        if status and status.get("Online"):
            return status["TailscaleIPs"][0].replace("/32", "")
        return None

    def get_exit_nodes(self):
        data = self.get_status_json()
        peers = data.get("Peer", {})
        exit_nodes = []
        for peer in peers.values():
            allowed_ips = peer.get("AllowedIPs", [])
            if any(ip in ["0.0.0.0/0", "::/0"] for ip in allowed_ips):
                exit_nodes.append({
                    "host": peer.get("HostName"),
                    "ip": peer.get("TailscaleIPs", ["?"])[0],
                    "online": peer.get("Online", False)
                })
        return exit_nodes

    def get_self_info(self):
        data = self.get_status_json()
        return data.get("Self", {})