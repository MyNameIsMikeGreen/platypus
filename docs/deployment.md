# Raspberry Pi deployment

## Host preparation

Use a [supported 64-bit Raspberry Pi OS](https://www.raspberrypi.com/software/operating-systems/)
and reserve a stable IP in the router's DHCP configuration. Install current
[Docker Engine for Debian](https://docs.docker.com/engine/install/debian/) and the
[Compose plugin](https://docs.docker.com/compose/install/linux/) from Docker's official
repository. Keep the OS and Docker patched.

Only the configured HTTP port must be reachable from the home LAN and the Pi's Tailscale interface. Do not expose Docker's daemon socket. Use the host firewall to reject access from untrusted networks while allowing the LAN and `tailscale0`.

## Start and stop

After completing the [README quick start](../README.md#quick-start):

```shell
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 app
```

Stop Platypus:

```shell
docker compose down
```

## LAN and Tailscale access

List every IP address or hostname that visitors will put in their browser in `.env`:

```dotenv
PLATYPUS_ALLOWED_HOSTS=192.168.1.50,raspberrypi
PLATYPUS_PORT=8080
```

Use `http://192.168.1.50:8080` on the home LAN. While connected to the tailnet, use
`http://raspberrypi:8080`, replacing the example with the Pi's actual
[MagicDNS](https://tailscale.com/kb/1081/magicdns) name. Add both the short and fully qualified
`*.ts.net` forms if both will be used.

Platypus does not integrate with or detect Tailscale. Django validates the standard HTTP `Host` header against this generic allow-list; MagicDNS is simply another hostname a browser may send.

HTTP is an intentional fit for this deployment. Platypus contains no authentication, private
user data, browser-side updates, or sensitive recipe content.
[Tailscale encrypts](https://tailscale.com/security) remote traffic between tailnet devices using
WireGuard, while the trusted home LAN carries only read-only recipe responses. Visitors therefore
need no certificate installation or warning bypass.

HTTP does not protect LAN traffic from observation or modification by a compromised local device. Reintroduce HTTPS before adding accounts, authentication cookies, private data, write operations, or access from any untrusted network.

Do not add router port forwarding or a public tunnel for this deployment. Before adding any write
capability or public-internet exposure, complete the applicable plan in
[`security-boundary.md`](security-boundary.md).

## Updates

Follow the dependency and quality-check workflow in
[`development.md`](development.md#quality-checks), then:

```shell
docker compose build --pull
docker compose up -d
```

The image build validates the recipe catalog before deployment.

## Backup

Recipes are versioned using the catalog described in [`recipes.md`](recipes.md), and Platypus has
no runtime data. Back up the repository through the normal source-control workflow. A fresh image
fully reconstructs the application.

## Resource use

The single container is limited to 256 MiB. Gunicorn's default single worker is sufficient for the expected one-device-at-a-time workload and avoids unnecessary processes.
