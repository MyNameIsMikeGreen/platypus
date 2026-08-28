# Architecture and standards

## Runtime

LAN and Tailscale clients connect directly to Gunicorn's default single worker in the
[`compose.yml`](../compose.yml) application container. WhiteNoise serves the single compiled
stylesheet, and Django reads the [checked-in recipe catalog](recipes.md) directly into memory.

The application omits a database, Django models, migrations, admin, authentication, sessions,
messages, CSRF processing, uploads, internationalization, frontend dependencies, background
workers, and compatibility routes because none are required. Django's common middleware remains
enabled because it triggers host-header validation; its optional trailing-slash redirects are
disabled. The [security boundary](security-boundary.md) explains when these decisions must change.

## Security posture

- Only Gunicorn's application port is published; the container has no persistent or writable application data.
- The container runs as a non-root user, drops Linux capabilities, prohibits privilege escalation, and uses a read-only root filesystem.
- Django accepts only configured hostnames, allows only GET and HEAD endpoints, applies a restrictive Content Security Policy, denies framing, and emits MIME-sniffing and referrer controls.
- Templates use Django's automatic escaping.
- Remote images are restricted by CSP to the existing Cloudinary host and are never proxied through the server.
- Logs use Docker's rotating `local` driver.
- The catalog rejects empty data, unknown or duplicate fields, invalid types, duplicate IDs or slugs, malformed dates, and unapproved image hosts.
- Django still requires a signing key, but this application has no sessions, authentication, CSRF tokens, messages, or other signed browser state. A fresh random key is therefore generated in memory for each process instead of creating a secret-management workflow with no security benefit.

HTTP is a deliberate scope-based decision. The application is read-only, has no accounts or private data, and is exposed only to the trusted home LAN and Tailscale. Tailscale provides encrypted WireGuard transport for remote connections. Avoiding a private certificate authority removes certificate warnings and device provisioning for household visitors. HTTPS becomes necessary if the application's data, trust boundary, or interaction model changes.

The precise assumptions, accepted risks, and mandatory upgrade plans for write capabilities or
public-internet exposure are documented in
[`security-boundary.md`](security-boundary.md). The current architecture must not be reused
outside that boundary without completing the applicable plan.

## Official guidance consulted

- [Django 6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [Django security guidance](https://docs.djangoproject.com/en/6.1/topics/security/)
- [Django Content Security Policy](https://docs.djangoproject.com/en/6.1/howto/csp/)
- [Django static-file deployment](https://docs.djangoproject.com/en/6.1/howto/static-files/deployment/)
- [Django initial data guidance](https://docs.djangoproject.com/en/6.1/howto/initial-data/)
- [Django with Gunicorn](https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/gunicorn/)
- [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [Docker logging configuration](https://docs.docker.com/engine/logging/configure/)
- [WhiteNoise with Django](https://whitenoise.readthedocs.io/en/stable/django.html)
- [Tailscale encryption](https://tailscale.com/security)
- [Tailscale MagicDNS](https://tailscale.com/kb/1081/magicdns)
- [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [uv lockfiles](https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile)
- [pytest usage](https://docs.pytest.org/en/stable/how-to/usage.html)

Version pins and the lockfile should be reviewed regularly because guidance and security releases continue to evolve.
