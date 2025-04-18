# setup.py
from setuptools import setup, find_packages

setup(
    name="ghostscale",
    version="0.1.0",
    description="Wrapper-System zur intelligenten VPN-Steuerung per Tailscale",
    author="Dierk Zehe",
    author_email="mgcmshr@gmail.com",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "ghostscale = ghostscale.cli:cli"
        ]
    },
)
