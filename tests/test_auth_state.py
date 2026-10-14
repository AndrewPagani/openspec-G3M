import unittest
from types import SimpleNamespace

import reflex as rx

from app.state.auth_state import AuthState


class AuthStateTests(unittest.TestCase):
    def test_logout_clears_session_and_returns_login_redirect(self) -> None:
        state = SimpleNamespace(
            token="session-token",
            user_name="Gerente",
            profile="Gerente",
            email="user@example.test",
            password="secret",
            busy=True,
            error="Falha",
            notice="Aviso",
        )

        event = AuthState.logout.fn(state)

        self.assertEqual(
            vars(state),
            {
                "token": "",
                "user_name": "",
                "profile": "",
                "email": "",
                "password": "",
                "busy": False,
                "error": "",
                "notice": "",
            },
        )
        self.assertIsInstance(event, rx.event.EventSpec)
        self.assertEqual(event.args[0][1]._var_value, "/login")


if __name__ == "__main__":
    unittest.main()
