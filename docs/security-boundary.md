# Security boundary and upgrade plan

## Current boundary

Platypus currently assumes:

- access only from trusted home-LAN devices or authenticated Tailscale devices;
- no router port forwarding, public host, or public tunnel;
- firewall access limited to the LAN and Tailscale interface;
- read-only `GET`/`HEAD` endpoints with no accounts, private data, uploads, or runtime writes;
- recipe changes made only through the [checked-in catalogue](recipes.md).

HTTP is a deliberate simplicity trade-off. Tailscale encrypts remote traffic, but home-LAN HTTP
can be observed or modified by a compromised local device. Anyone who can reach the port can read
the recipes.

`PLATYPUS_ALLOWED_HOSTS` validates host headers; it is not authentication or a firewall. The
current deployment must not gain writes, private data, accounts, or public exposure without
completing the applicable plan below. See [architecture](architecture.md) and
[deployment](deployment.md) for the implemented controls.

## Before adding write capabilities

Complete this plan even if writes remain LAN/Tailscale-only:

1. **Define access:** specify who may create, edit, and delete each resource; enforce
   authorisation in every write view; keep public registration disabled unless required.
2. **Add persistent storage:** replace the immutable runtime catalogue with Django models,
   migrations, and a persistent database. Define catalogue import/export so recipes remain
   versioned. Add and test backup, restore, migration, and rollback procedures.
3. **Add identity and secrets:** enable Django authentication, sessions, and content types. Use
   Django's password handling, least-privilege accounts, and a stable `SECRET_KEY` supplied
   through a [Docker secret](https://docs.docker.com/compose/how-tos/use-secrets/). Do not expose
   Django admin unless it is the chosen editor.
4. **Enable HTTPS first:** terminate trusted TLS at a maintained reverse proxy; redirect HTTP;
   configure `SECURE_PROXY_SSL_HEADER` only for that proxy; enable secure session/CSRF cookies;
   add HSTS only after HTTPS is reliable.
5. **Restore write protections:** enable
   [`CsrfViewMiddleware`](https://docs.djangoproject.com/en/6.1/howto/csrf/); never write from
   `GET`; narrowly configure `CSRF_TRUSTED_ORIGINS`; validate and limit all input and uploads.
6. **Preserve container isolation:** keep the application filesystem read-only. Mount only
   dedicated data storage, or use an internal-only database service with no published port. Add
   readiness checks for new dependencies.
7. **Extend tests and operations:** cover anonymous rejection, roles, CSRF, validation,
   concurrency, and destructive actions. Add security audit logs without recording secrets.
   Update the [development checks](development.md#quality-checks) and recipe workflow.

## Before public-internet exposure

Complete this plan even if Platypus remains read-only:

1. **Reconsider exposure:** Tailscale is safer and simpler. Modest self-hosted hardware cannot
   resist volumetric denial-of-service attacks; use a protective CDN, tunnel, or hosted proxy if
   that risk must be accepted.
2. **Add a public ingress:** use a real domain and publicly trusted TLS through a maintained
   reverse proxy such as [Caddy](https://caddyserver.com/docs/automatic-https). Expose only 443
   and, if needed for certificate issuance or redirect, 80. Never expose Gunicorn directly.
3. **Separate networks:** remove the application host-port mapping; connect proxy and app through
   a private [Docker network](https://docs.docker.com/engine/network/); use a default-deny host
   firewall; keep SSH and administration on Tailscale; never mount the Docker socket.
4. **Configure proxy trust exactly:** use the precise public `ALLOWED_HOSTS` value; trust forwarded
   HTTPS headers only when overwritten by the proxy; enforce HTTPS; enable HSTS after certificate
   renewal is proven; do not use wildcard hosts.
5. **Limit hostile traffic:** set body, header, connection, and request-rate limits; retain method
   and input validation; return generic errors without tracebacks or settings.
6. **Operate and review:** patch the OS, Docker, proxy, images, and dependencies; monitor
   certificates, restarts, disk, failures, and traffic; keep bounded logs and off-device backups.
   Perform a fresh threat model and security review before launch.

If public exposure also includes writes, accounts, or private data, both plans apply.

## Release gates

Before deploying either change:

- trusted HTTPS is automatically renewed and enforced;
- `python manage.py check --deploy` has no unexplained warnings;
- authentication, authorisation, CSRF, validation, and security-header tests pass;
- secrets are absent from source, images, and logs;
- only proxy ports are public; Gunicorn and databases are private;
- off-device backups and restoration have been tested;
- monitoring, patching, incident response, rollback, and the new threat model are documented.

Re-check the current [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/),
[Django security guidance](https://docs.djangoproject.com/en/6.1/topics/security/), and
[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) during
implementation.
