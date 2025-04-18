# Ghostscale

**Ghostscale** ist ein CLI-Tool zur intelligenten Steuerung von Tailscale Exit Nodes.

## Features

- Automatische Aktivierung/Deaktivierung von Exit Nodes
- Smart-Modus für Git: VPN nur bei Push/Pull/Fetch
- YAML-Konfiguration
- Wrapper-Generierung für beliebige CLI-Programme

## Beispielkonfiguration

```yaml
git:
  mode: smart
  exit_node: 100.100.100.100
  trigger_commands:
    - push
    - pull
    - fetch
    - clone

ssh:
  mode: always
  exit_node: 100.100.100.100
```