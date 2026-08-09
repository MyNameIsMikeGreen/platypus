import json
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


config = json.load(sys.stdin)
require(set(config["services"]) == {"app"}, "Compose must contain only the application service.")
require("volumes" not in config, "Compose must not define persistent volumes.")
require("secrets" not in config, "Compose must not define runtime secrets.")

app = config["services"]["app"]
require(app.get("read_only") is True, "The application root filesystem must be read-only.")
require(app.get("cap_drop") == ["ALL"], "The application must drop every Linux capability.")
require(
    "no-new-privileges:true" in app.get("security_opt", []),
    "The application must prohibit privilege escalation.",
)
require(app.get("pids_limit") == 64, "The application PID limit must remain enabled.")
require(app.get("mem_limit") == "268435456", "The 256 MiB memory limit must remain enabled.")
require(
    app.get("tmpfs") == ["/tmp:size=16m,mode=1777,noexec,nosuid,nodev"],
    "The temporary filesystem must retain its size and security restrictions.",
)
require("volumes" not in app, "The application must not mount persistent data.")
require("secrets" not in app, "The application must not receive secrets.")
require(app.get("privileged", False) is False, "The application must not be privileged.")
require(
    app.get("ports")
    == [
        {
            "mode": "ingress",
            "protocol": "tcp",
            "published": "8080",
            "target": 8000,
        }
    ],
    "Compose must publish only Gunicorn through the configured HTTP port.",
)
