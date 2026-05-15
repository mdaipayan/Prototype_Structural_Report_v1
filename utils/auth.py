"""Password gate helpers for the Streamlit app."""

from __future__ import annotations

import hmac
import os

import streamlit as st


_PASSWORD_HELP = (
    "Set APP_PASSWORD in the environment or add app_password to Streamlit secrets."
)


def _configured_password() -> str | None:
    """Return the configured application password, if one is available."""
    env_password = os.getenv("APP_PASSWORD")
    if env_password:
        return env_password

    try:
        secrets = st.secrets
        for key in ("APP_PASSWORD", "app_password", "password"):
            if key in secrets and secrets[key]:
                return str(secrets[key])
    except Exception:
        # Streamlit can raise when no secrets file exists. In that case the
        # environment variable path above remains the supported configuration.
        return None

    return None


def _log_out() -> None:
    """Clear the authenticated session and restart the Streamlit run."""
    st.session_state.password_authenticated = False
    st.rerun()


def _show_logout_controls() -> None:
    """Render visible logout controls in the main page."""
    status_col, logout_col = st.columns([4, 1])
    with status_col:
        st.caption("🔓 Authenticated session")
    with logout_col:
        st.button(
            "Log out",
            key="logout_main",
            use_container_width=True,
            on_click=_log_out,
        )


def require_password() -> None:
    """Stop the page until the visitor enters the configured password."""
    expected_password = _configured_password()

    if not expected_password:
        st.error("Application password is not configured.")
        st.info(_PASSWORD_HELP)
        st.stop()

    if st.session_state.get("password_authenticated"):
        _show_logout_controls()
        return

    st.title("🔒 Protected Application")
    st.caption("Enter the application password to access the design suite.")

    with st.form("password_gate"):
        entered_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Unlock", use_container_width=True)

    if submitted:
        if hmac.compare_digest(entered_password, expected_password):
            st.session_state.password_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    st.stop()
