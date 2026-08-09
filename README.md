# Platypus

Platypus is Mike Green's small, self-hosted recipe collection. It presents the same versioned recipes and familiar recipe, search, tag, and meal-planning workflows as the original application, rebuilt for a Raspberry Pi and a private LAN.

## Quick start

Prerequisites: a [supported 64-bit Raspberry Pi OS](https://www.raspberrypi.com/software/operating-systems/),
[Docker Engine](https://docs.docker.com/engine/install/debian/), and the
[Docker Compose plugin](https://docs.docker.com/compose/install/linux/).

1. Reserve a stable LAN IP address for the Pi.
2. Copy `.env.example` to `.env` and set `PLATYPUS_ALLOWED_HOSTS` and `PLATYPUS_PORT`.
3. Build and start Platypus:

   ```shell
   docker compose up --build -d
   ```

4. Open Platypus using any address listed in `PLATYPUS_ALLOWED_HOSTS`, for example `http://192.168.1.50:8080` or `http://raspberrypi:8080`.

The single container reads recipes directly from the validated, checked-in catalog. Gunicorn serves the application and WhiteNoise serves its stylesheet.

## Documentation

- [`docs/development.md`](docs/development.md): local setup, tests, formatting, and IDE configuration
- [`docs/recipes.md`](docs/recipes.md): adding and changing versioned recipes
- [`docs/deployment.md`](docs/deployment.md): Raspberry Pi deployment, Tailscale access, and updates
- [`docs/security-boundary.md`](docs/security-boundary.md): accepted HTTP/LAN risks and the
  required plan before adding writes or public-internet access
- [`docs/architecture.md`](docs/architecture.md): design decisions and official guidance

## Technology

Python 3.14, Django 6.1, Gunicorn, WhiteNoise, Docker Compose, uv, Ruff, and pytest.
