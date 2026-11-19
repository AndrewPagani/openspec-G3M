import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import reflex as rx

from app.state.auth_state import AuthState


class AuthStateTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.state.auth_state.clear_operational_state", new_callable=AsyncMock)
    @patch(
        "app.state.auth_state.client.async_login",
        return_value={
            "authToken": "session-token",
            "user": {
                "id": 17,
                "UNome": "Gerente",
                "perfil": {"Cargo": "Gerente"},
            },
        },
    )
    async def test_login_saves_account_identifier_for_local_preferences(self, login, clear) -> None:
        state = SimpleNamespace(
            email="user@example.test",
            password="secret",
            busy=False,
            error="",
            notice="",
            account_id="",
            token="",
            user_name="",
            profile="",
        )

        await AuthState.login.fn(state)

        self.assertEqual(state.account_id, "17")
        self.assertEqual(state.user_name, "Gerente")
        login.assert_called_once_with("user@example.test", "secret")

    @patch("app.state.auth_state.clear_operational_state", new_callable=AsyncMock)
    async def test_logout_clears_session_and_returns_login_redirect(self, clear) -> None:
        state = SimpleNamespace(
            token="session-token",
            user_name="Gerente",
            profile="Gerente",
            account_id="user-17",
            email="user@example.test",
            password="secret",
            busy=True,
            error="Falha",
            notice="Aviso",
        )

        event = await AuthState.logout.fn(state)

        self.assertEqual(
            vars(state),
            {
                "token": "",
                "user_name": "",
                "profile": "",
                "account_id": "",
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
