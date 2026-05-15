"""Google OAuth helpers for protecting the Streamlit app."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st


_CREDENTIALS_FILE = Path(
    os.getenv(
        "GOOGLE_AUTH_CREDENTIALS_PATH", "/tmp/steel_suite_google_credentials.json"
    )
)
_DEFAULT_REDIRECT_URI = "https://prototypestructuralreportv1.streamlit.app/"
_DEFAULT_COOKIE_NAME = "steel_suite_auth"
_SECRET_HELP = "Configure Google OAuth in Streamlit secrets under [google_auth]."


def _secrets() -> dict[str, Any]:
    """Return Streamlit secrets as a plain mapping when they are configured."""
    try:
        return dict(st.secrets)
    except Exception:
        return {}


def _secret_value(*keys: str, default: str | None = None) -> str | None:
    """Return the first configured Streamlit secret or environment value."""
    secrets = _secrets()
    google_auth_secrets = secrets.get("google_auth", {})

    for key in keys:
        env_value = os.getenv(key)
        if env_value:
            return env_value

        if key in google_auth_secrets and google_auth_secrets[key]:
            return str(google_auth_secrets[key])

        if key in secrets and secrets[key]:
            return str(secrets[key])

    return default


def _secret_list(*keys: str) -> set[str]:
    """Return normalized values from a comma-delimited env var or secret list."""
    secrets = _secrets()
    google_auth_secrets = secrets.get("google_auth", {})

    for key in keys:
        value: Any = os.getenv(key)
        if value is None:
            value = google_auth_secrets.get(key)
        if value is None:
            value = secrets.get(key)
        if value is None:
            continue

        if isinstance(value, str):
            return {item.strip().lower() for item in value.split(",") if item.strip()}

        return {str(item).strip().lower() for item in value if str(item).strip()}

    return set()


def _write_google_credentials_file() -> Path:
    """Create the Google client secrets file required by streamlit-google-auth."""
    credentials_json = _secret_value("GOOGLE_CREDENTIALS_JSON", "credentials_json")
    if credentials_json:
        credentials = json.loads(credentials_json)
    else:
        client_id = _secret_value("GOOGLE_CLIENT_ID", "client_id")
        client_secret = _secret_value("GOOGLE_CLIENT_SECRET", "client_secret")

        if not client_id or not client_secret:
            st.error("Google OAuth is not configured.")
            st.info(
                f"{_SECRET_HELP} Required values: client_id, client_secret, "
                "and cookie_secret."
            )
            st.stop()

        credentials = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": (
                    "https://www.googleapis.com/oauth2/v1/certs"
                ),
                "redirect_uris": [_redirect_uri()],
            }
        }

    _CREDENTIALS_FILE.write_text(json.dumps(credentials), encoding="utf-8")
    _CREDENTIALS_FILE.chmod(0o600)
    return _CREDENTIALS_FILE


def _redirect_uri() -> str:
    """Return the OAuth redirect URI configured for this deployment."""
    return (
        _secret_value(
            "GOOGLE_REDIRECT_URI", "redirect_uri", default=_DEFAULT_REDIRECT_URI
        )
        or _DEFAULT_REDIRECT_URI
    )


def _cookie_secret() -> str:
    """Return the cookie encryption secret."""
    cookie_secret = _secret_value(
        "GOOGLE_COOKIE_SECRET", "cookie_secret", "secret_token"
    )
    if not cookie_secret:
        st.error("Google OAuth cookie secret is not configured.")
        st.info(f"{_SECRET_HELP} Required value: cookie_secret.")
        st.stop()

    return cookie_secret


def _authenticator() -> Any:
    """Initialize and cache the Google authenticator in Streamlit session state."""
    from streamlit_google_auth import Authenticate

    if "authenticator" not in st.session_state:
        st.session_state["authenticator"] = Authenticate(
            secret_credentials_path=str(_write_google_credentials_file()),
            redirect_uri=_redirect_uri(),
            cookie_name=_secret_value(
                "GOOGLE_COOKIE_NAME", "cookie_name", default=_DEFAULT_COOKIE_NAME
            )
            or _DEFAULT_COOKIE_NAME,
            cookie_key=_cookie_secret(),
        )

    return st.session_state["authenticator"]


def _user_is_authorized() -> bool:
    """Check optional email/domain allowlists after Google login succeeds."""
    allowed_emails = _secret_list("GOOGLE_AUTHORIZED_EMAILS", "authorized_emails")
    allowed_domains = _secret_list("GOOGLE_AUTHORIZED_DOMAINS", "authorized_domains")

    if not allowed_emails and not allowed_domains:
        return True

    user_info = st.session_state.get("user_info", {})
    email = str(user_info.get("email", "")).lower()
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""

    return email in allowed_emails or domain in allowed_domains


def require_google_auth() -> None:
    """Stop the page until the visitor logs in with an authorized Google account."""
    authenticator = _authenticator()
    check_auth = getattr(authenticator, "check_authenticator", None) or getattr(
        authenticator, "check_authentification"
    )
    check_auth()

    if not st.session_state.get("connected"):
        st.title("🔒 IS Steel Design Suite")
        st.info("Please login with your authorised Google account to proceed.")
        authenticator.login()
        st.stop()

    if not _user_is_authorized():
        st.error("This Google account is not authorized to access the app.")
        if st.button("Log out", use_container_width=True):
            authenticator.logout()
            st.rerun()
        st.stop()

    user_name = st.session_state.get("user_info", {}).get("name", "there")
    st.success(f"Welcome, {user_name}!")

    with st.sidebar:
        if st.button("Log out", use_container_width=True):
            authenticator.logout()
            st.rerun()
