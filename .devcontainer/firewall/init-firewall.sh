#!/usr/bin/env bash
# Firewall de salida por allowlist (D26). Resuelve dominios a IPs y bloquea el resto.
# TODO-VERIFY: probar en un dev container real; no se ha ejecutado en la Oleada 0.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
ipset destroy allowed-domains 2>/dev/null || true
ipset create allowed-domains hash:ip family inet

grep -vE '^\s*(#|$)' "$DIR/allowlist.txt" | while read -r domain; do
  for ip in $(dig +short A "$domain" | grep -E '^[0-9.]+$'); do
    ipset add -exist allowed-domains "$ip"
  done
done

iptables -F OUTPUT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited
echo "firewall: salida limitada a $(ipset list allowed-domains | grep -c '^[0-9]') IPs de la allowlist"
