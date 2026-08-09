from django.conf import settings
from django.core.checks import run_checks
from django.utils.csp import CSP


def test_critical_django_security_settings():
    assert settings.DEBUG is False
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.dummy"
    assert settings.ALLOWED_HOSTS
    assert "*" not in settings.ALLOWED_HOSTS
    assert len(settings.SECRET_KEY) >= 50

    assert settings.MIDDLEWARE[0] == "django.middleware.security.SecurityMiddleware"
    assert "django.middleware.common.CommonMiddleware" in settings.MIDDLEWARE
    assert "django.middleware.csp.ContentSecurityPolicyMiddleware" in settings.MIDDLEWARE
    assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in settings.MIDDLEWARE

    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.SECURE_REFERRER_POLICY == "strict-origin-when-cross-origin"
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.SECURE_CSP["default-src"] == [CSP.SELF]
    assert settings.SECURE_CSP["connect-src"] == [CSP.NONE]
    assert settings.SECURE_CSP["frame-ancestors"] == [CSP.NONE]
    assert settings.SECURE_CSP["object-src"] == [CSP.NONE]
    assert settings.SECURE_CSP["script-src"] == [CSP.SELF]


def test_only_intentional_deployment_warnings_remain():
    warnings = run_checks(include_deployment_checks=True)

    assert {warning.id for warning in warnings} == {
        "security.W003",  # No writes, forms using POST, sessions, or authentication.
        "security.W004",  # HTTP-only private LAN deployment cannot use HSTS.
        "security.W008",  # HTTP-only private LAN deployment cannot redirect to HTTPS.
    }
