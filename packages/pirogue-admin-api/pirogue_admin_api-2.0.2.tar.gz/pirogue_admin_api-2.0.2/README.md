# pirogue-admin-api

## Description
Common interface to PiRogue administration bricks.

## Motivation
PiRogue is now proudly supporting cloud deployment.
This project is the base local AND remote management system definition.
Both `pirogue-admin` and `pirogue-admin-client` are supposed to depreciate `pirogue-cli` package.
The `pirogue-admin-api` package is the common definition between `pirogue-admin` daemon and the `pirogue-admin-client` client (which also provides cli tools).

## Scope
Here are high-level features covered by PiRogue administration:
```yaml
System:
  - Query
  - Configuration
Networking:
  - External remote administration management
  - External network management
  - Isolated network management
  - Public access management
  - WiFi configuration
  - VPN administration
Services:
  - Grafana administration
  - Suricata detection rules management
```
