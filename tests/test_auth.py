import unittest
from unittest.mock import patch

from utils import auth


class SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class FakeForm:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class StopCalled(RuntimeError):
    pass


class RerunCalled(RuntimeError):
    pass


class FakeColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeStreamlit:
    def __init__(self, *, password_input="", submitted=False):
        self.session_state = SessionState()
        self.password_input = password_input
        self.submitted = submitted
        self.warnings = []
        self.errors = []
        self.infos = []

    def error(self, message):
        self.errors.append(message)

    def info(self, message):
        self.infos.append(message)

    def warning(self, message):
        self.warnings.append(message)

    def stop(self):
        raise StopCalled

    def rerun(self):
        raise RerunCalled

    def title(self, _message):
        return None

    def caption(self, _message):
        return None

    def form(self, _key):
        return FakeForm()

    def text_input(self, _label, type=None):
        return self.password_input

    def form_submit_button(self, _label, use_container_width=False):
        return self.submitted

    def columns(self, _spec):
        return [FakeColumn(), FakeColumn()]

    def button(self, *args, **kwargs):
        return False


class AuthTests(unittest.TestCase):
    def test_successful_login_stores_password_fingerprint(self):
        fake_st = FakeStreamlit(password_input="secret", submitted=True)

        with patch.object(auth, "st", fake_st), patch.dict(
            "os.environ", {"APP_PASSWORD": "secret"}, clear=False
        ):
            with self.assertRaises(RerunCalled):
                auth.require_password()

        self.assertTrue(fake_st.session_state["password_authenticated"])
        self.assertEqual(
            fake_st.session_state["password_fingerprint"],
            auth._password_fingerprint("secret"),
        )
        self.assertNotEqual(fake_st.session_state["password_fingerprint"], "secret")

    def test_authenticated_session_is_invalidated_when_password_changes(self):
        fake_st = FakeStreamlit()
        fake_st.session_state.password_authenticated = True
        fake_st.session_state.password_fingerprint = auth._password_fingerprint("old")

        with patch.object(auth, "st", fake_st), patch.dict(
            "os.environ", {"APP_PASSWORD": "new"}, clear=False
        ):
            with self.assertRaises(StopCalled):
                auth.require_password()

        self.assertFalse(fake_st.session_state["password_authenticated"])
        self.assertNotIn("password_fingerprint", fake_st.session_state)
        self.assertEqual(
            fake_st.warnings, ["Application password changed. Please sign in again."]
        )

    def test_authenticated_session_with_current_password_reuses_session(self):
        fake_st = FakeStreamlit()
        fake_st.session_state.password_authenticated = True
        fake_st.session_state.password_fingerprint = auth._password_fingerprint("secret")

        with patch.object(auth, "st", fake_st), patch.dict(
            "os.environ", {"APP_PASSWORD": "secret"}, clear=False
        ):
            auth.require_password()

        self.assertTrue(fake_st.session_state["password_authenticated"])


if __name__ == "__main__":
    unittest.main()
