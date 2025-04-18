import yaml
import sys
from pathlib import Path
from ghostscale.utils import SingletonMeta

CONFIG_PATH = Path.home() / ".config/ghostscale/config.yaml"

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path

    def load_config(self):
        if not self.config_path.exists():
            print(f"Konfigurationsdatei fehlt: {self.config_path}")
            sys.exit(1)
        with open(self.config_path) as f:
            return yaml.safe_load(f)