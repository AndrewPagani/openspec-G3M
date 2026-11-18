import json
import unittest

from app.state.settings_state import (
    THEME_MODES,
    WIDGET_IDS,
    _account_preferences,
    _default_preferences,
    _decode_store,
    _validate_preferences,
)


class SettingsStateTests(unittest.TestCase):
    def test_defaults_include_existing_widgets_without_shortcuts(self) -> None:
        preferences = _default_preferences()

        self.assertEqual(preferences["visible_widgets"], list(WIDGET_IDS))
        self.assertEqual(preferences["widget_order"], list(WIDGET_IDS))
        self.assertNotIn("shortcuts", preferences)
        self.assertEqual(preferences["dashboard_title"], "Dashboard")
        self.assertEqual(preferences["appearance_mode"], "dark")

    def test_theme_modes_are_validated_and_legacy_preferences_default_to_dark(
        self,
    ) -> None:
        for mode in THEME_MODES:
            preferences = _default_preferences()
            preferences["appearance_mode"] = mode
            self.assertEqual(_validate_preferences(preferences)["appearance_mode"], mode)

        self.assertEqual(
            _validate_preferences({"dashboard_title": "Meu painel"})[
                "appearance_mode"
            ],
            "dark",
        )

        preferences = _default_preferences()
        preferences["appearance_mode"] = "sepia"
        with self.assertRaisesRegex(ValueError, "tema válido"):
            _validate_preferences(preferences)

    def test_preferences_are_isolated_by_account_key(self) -> None:
        first = {
            "dashboard_title": "Meu painel",
            "appearance_mode": "light",
            "visible_widgets": ["metrics"],
            "widget_order": list(WIDGET_IDS),
            "shortcuts": ["new_sale"],
        }
        second = {"dashboard_title": "Dashboard da loja"}
        raw = json.dumps({"user-1": first, "user-2": second})

        self.assertEqual(
            _account_preferences(raw, "user-1")["dashboard_title"],
            "Meu painel",
        )
        self.assertEqual(
            _account_preferences(raw, "user-2")["dashboard_title"],
            "Dashboard da loja",
        )
        self.assertEqual(
            _account_preferences(raw, "user-1")["appearance_mode"], "light"
        )
        self.assertEqual(
            _account_preferences(raw, "user-2")["appearance_mode"], "dark"
        )
        self.assertNotIn("shortcuts", _account_preferences(raw, "user-1"))

    def test_rejects_unknown_widget_and_invalid_title(self) -> None:
        preferences = _default_preferences()
        preferences["visible_widgets"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "seleção de widgets"):
            _validate_preferences(preferences)

        preferences = _default_preferences()
        preferences["dashboard_title"] = " "
        with self.assertRaisesRegex(ValueError, "título do Dashboard"):
            _validate_preferences(preferences)

    def test_invalid_local_storage_is_reported(self) -> None:
        with self.assertRaisesRegex(ValueError, "preferências locais"):
            _decode_store("{")


if __name__ == "__main__":
    unittest.main()
