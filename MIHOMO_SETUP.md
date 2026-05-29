# Mihomo Proxy Setup

This guide documents how to run `FreeAIchat-2api` through a local mihomo/Clash proxy on the server.

## Install Mihomo

For `x86_64` Linux servers, download the matching mihomo release asset and install it:

```bash
cd /root/devops
gunzip -c mihomo-linux-amd64-compatible-v1.19.25.gz > mihomo
chmod +x mihomo
install -m 755 mihomo /usr/local/bin/mihomo
/usr/local/bin/mihomo -v
```

Place geo data files in `/etc/mihomo` if mihomo cannot download them automatically:

```bash
mkdir -p /etc/mihomo
install -m 644 /root/devops/country.mmdb /etc/mihomo/Country.mmdb
install -m 644 /root/devops/geosite.dat /etc/mihomo/geosite.dat
install -m 644 /root/devops/geoip.dat /etc/mihomo/geoip.dat
```

## Configure Subscription

Download the Clash-compatible subscription into mihomo. Treat the subscription URL as a secret.

```bash
curl -L -A "Clash.Meta" 'YOUR_SUBSCRIPTION_URL' -o /etc/mihomo/config.yaml
```

Recommended local-only listener settings in `/etc/mihomo/config.yaml`:

```yaml
mixed-port: 7890
allow-lan: false
bind-address: 127.0.0.1
external-controller: 127.0.0.1:9090
```

Validate the config:

```bash
/usr/local/bin/mihomo -t -d /etc/mihomo
```

## Run Mihomo With Systemd

Create `/etc/systemd/system/mihomo.service`:

```ini
[Unit]
Description=mihomo proxy service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mihomo -d /etc/mihomo
Restart=on-failure
RestartSec=3
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Enable and test:

```bash
systemctl daemon-reload
systemctl enable --now mihomo
systemctl status mihomo
curl -x http://127.0.0.1:7890 https://api.ipify.org
```

## Select Proxy Node

List proxy groups and nodes:

```bash
python3 - <<'PY'
import json, urllib.request

data = json.load(urllib.request.urlopen("http://127.0.0.1:9090/proxies"))
g = data["proxies"]["GLOBAL"]

print("CURRENT:", g.get("now"))
for i, name in enumerate(g["all"], 1):
    print(f"{i}. {name}")
PY
```

Switch `GLOBAL` to a specific node:

```bash
python3 - <<'PY'
import json, urllib.parse, urllib.request

group = "GLOBAL"
node = "YOUR_NODE_NAME"

url = "http://127.0.0.1:9090/proxies/" + urllib.parse.quote(group)
req = urllib.request.Request(
    url,
    data=json.dumps({"name": node}).encode(),
    method="PUT",
    headers={"Content-Type": "application/json"},
)

resp = urllib.request.urlopen(req)
print("HTTP", resp.status)
print("SELECTED:", node)
PY
```

Verify:

```bash
python3 - <<'PY'
import json, urllib.request
data = json.load(urllib.request.urlopen("http://127.0.0.1:9090/proxies/GLOBAL"))
print("CURRENT:", data.get("now"))
PY
curl -x http://127.0.0.1:7890 https://api.ipify.org
```

## Configure FreeAIchat-2api

Use `COOKIE_B64` instead of raw `COOKIE` so Docker Compose does not expand `$...` fragments inside cookies.

Generate `COOKIE_B64` from the raw cookie:

```bash
printf '%s' 'YOUR_FULL_RAW_COOKIE' | base64 -w 0
```

Example `.env` shape:

```env
API_MASTER_KEY=sk-your-secret-key
COOKIE_B64="BASE64_ENCODED_COOKIE"
AJAX_NONCE="YOUR_AJAX_NONCE"
SESSION_ID="YOUR_SESSION_ID"
POST_ID="6"
UPSTREAM_PROXY=http://127.0.0.1:7890
NGINX_PORT=4001
```

Deploy:

```bash
cd /root/devops/FreeAIchat-2api
git pull
docker-compose config >/tmp/compose.out
docker-compose up -d --build --force-recreate
docker-compose logs -f app
```

Expected application log when the proxy is active:

```text
上游请求代理已启用。
```

## Troubleshooting

- `The "t1780037462" variable is not set`: raw `COOKIE` is still being parsed by Docker Compose. Use `COOKIE_B64` and remove raw `COOKIE`.
- `curl: (5) Could not resolve proxy: host.docker.internal`: use the current host network compose setup and `UPSTREAM_PROXY=http://127.0.0.1:7890`.
- `curl: (7) Could not connect to server`: mihomo is not running or not listening on `127.0.0.1:7890`.
- Check mihomo logs with `journalctl -u mihomo -f`.
