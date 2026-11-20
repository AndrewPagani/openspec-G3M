"""Run against navigation_fixture.py and the local Vite frontend.

Requires Playwright, Edge and openpyxl as a separate workbook reader.
"""

import json
from datetime import datetime
from pathlib import Path
from time import monotonic
from zipfile import ZipFile

from navigation_browser import PREFIX
from openpyxl import load_workbook
from playwright.sync_api import expect, sync_playwright

SITE = "http://localhost:3000"
CONTROL = "http://127.0.0.1:8001/fixture-control"
BASE_SHEETS = ["Dashboard", "Vendas", "Clientes", "Veículos", "Peças"]


def control(page, mode="excel", delay=0.035):
    return page.request.post(
        CONTROL, data={"mode": mode, "delay": delay, "reset": True}
    )


def open_dashboard(browser, profile, token, viewport):
    context = browser.new_context(viewport=viewport)
    auth = {
        "token": token,
        "profile": profile,
        "account_id": "17",
        "user_name": "Conta de teste",
    }
    values = {PREFIX + key + "_rx_state_": value for key, value in auth.items()}
    context.add_init_script(
        "if(!sessionStorage.fixtureInitialized){Object.entries("
        + json.dumps(values)
        + ").forEach(([k,v])=>localStorage.setItem(k,v));sessionStorage.fixtureInitialized='1';}"
    )
    page = context.new_page()
    control(page)
    page.goto(f"{SITE}/gerenciamento")
    export = page.get_by_role("button", name="Exportar Excel")
    expect(export).to_be_enabled(timeout=20000)
    page.get_by_label("Data final").fill("2026-10-31")
    page.get_by_label("Data final").fill(
        "2026-11-01" if profile == "Gerente" else "2026-11-02"
    )
    expect(export).to_be_disabled()
    page.get_by_label("Data inicial").fill("2026-11-01")
    page.get_by_role("button", name="Aplicar filtros").click()
    expect(export).to_be_enabled()
    return page, export


def verify_file(download, profile):
    path = download.path()
    assert download.suggested_filename.startswith("relatorio-2026-11-01")
    with ZipFile(path) as archive:
        assert all(
            b"PROIBIDO-EXPORTAR" not in archive.read(name)
            for name in archive.namelist()
        )
    with path.open("rb") as source:
        book = load_workbook(source)
    assert book.sheetnames == BASE_SHEETS + (
        ["Usuários"] if profile == "Administrador" else []
    )
    sales = book["Vendas"]
    ids = {cell[0].value for cell in sales.iter_rows(min_row=2)}
    assert {"1", "2", "6"} <= ids
    assert "5" not in ids
    expected = 104 if profile == "Gerente" else 105 if profile == "Vendedor" else 106
    assert len(ids) == expected
    assert ("3" in ids) == (profile != "Gerente")
    assert ("4" in ids) == (profile == "Administrador")
    assert sales["B2"].value == datetime(2026, 11, 1)
    assert sales["I2"].value == 150 and "R$" in sales["I2"].number_format
    assert book["Peças"]["E2"].value == 0
    assert book["Veículos"]["H2"].value == "Reservado"
    clients = book["Clientes"]
    assert clients.max_row == 1002
    assert clients["B2"].data_type == "s" and clients["B2"].value == "=Cliente 1"
    assert clients["C2"].value == "00000000001" and clients["D2"].value == "+550000001"
    dash = dict(book["Dashboard"].iter_rows(max_col=2, values_only=True))
    assert dash["Vendas no período"] == expected
    assert abs(dash["Percentual de cancelamentos"] - (1 / expected)) < 1e-12
    assert {
        "Vendas por status",
        "Vendas por forma de pagamento",
        "Mix de itens",
        "Veículos vendidos por marca",
        "Peças vendidas por categoria",
    } <= dash.keys()
    assert dash["Pix"] == expected
    assert dash["Motor"] == 1
    assert ("Veículos no status selecionado" in dash) == (profile != "Vendedor")
    return path.stat().st_size


def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        for profile, token in (
            ("Vendedor", "fixture-seller"),
            ("Gerente", "fixture-account-a"),
            ("Administrador", "fixture-admin"),
        ):
            viewport = (
                {"width": 390, "height": 844}
                if profile == "Gerente"
                else {"width": 1440, "height": 900}
            )
            page, export = open_dashboard(browser, profile, token, viewport)
            if profile == "Gerente":
                page.get_by_role("combobox", name="Tipo de item").click()
                page.get_by_role("option", name="Peça", exact=True).click()
                expect(export).to_be_disabled()
                page.get_by_role("button", name="Aplicar filtros").click()
                expect(export).to_be_enabled()
            page.get_by_role("button", name="Atualizar dados").press("Tab")
            expect(export).to_be_focused()
            assert (
                export.evaluate("(button) => getComputedStyle(button).outlineStyle")
                == "solid"
            )
            assert (
                page.locator("body").evaluate("(el) => el.scrollWidth")
                <= viewport["width"]
            )
            start = monotonic()
            with page.expect_download(timeout=20000) as download:
                export.press("Enter")
                expect(page.get_by_role("button", name="Exportando…")).to_be_disabled()
                expect(
                    page.get_by_role("status").filter(has_text="Consultando")
                ).to_be_visible()
                if profile == "Vendedor":
                    page.get_by_role("link", name="Clientes", exact=True).click()
                    page.wait_for_url("**/clientes")
            size = verify_file(download.value, profile)
            print(f"{profile}: {size} bytes, {(monotonic() - start):.2f} s")

            if profile == "Gerente":
                requests = page.request.get(CONTROL).json()["calls"]
                assert any(
                    call["path"] == "/gerenciamento/indicadores"
                    and call["params"].get("tipo_item") == "peca"
                    for call in requests
                )
                assert all(
                    "tipo_item" not in call["params"]
                    for call in requests
                    if call["path"] == "/vendas"
                )
                control(page, mode="excel-error")
                downloads = []
                page.on(
                    "download",
                    lambda download, observed=downloads: observed.append(download),
                )
                export.click()
                alert = page.get_by_role("alert").filter(has_text="consultar Clientes")
                expect(alert).to_be_visible()
                expect(alert).to_have_css("color", "rgb(254, 205, 211)")
                expect(export).to_be_enabled()
                assert not downloads
                output = Path(".impeccable/review/navigation")
                page.screenshot(path=output / "excel-erro-mobile.png")
                page.evaluate("document.documentElement.dataset.appTheme = 'light'")
                expect(alert).to_have_css("color", "rgb(190, 18, 60)")
                page.screenshot(path=output / "excel-erro-mobile-claro.png")

                control(page, mode="excel-timeout")
                export.click()
                expect(
                    page.get_by_role("alert").filter(has_text="demorou mais")
                ).to_be_visible()
                expect(export).to_be_enabled()
                assert not downloads
                control(page)
                with page.expect_download() as download:
                    export.click()
                verify_file(download.value, profile)
                count = len(downloads)

                control(page, delay=0.45)
                export.click()
                expect(page.get_by_role("button", name="Exportando…")).to_be_disabled()
                page.get_by_role("button", name="Sair", exact=True).click()
                page.wait_for_url("**/login")
                page.get_by_role("textbox", name="E-mail", exact=True).fill(
                    "contab@example.test"
                )
                page.get_by_role("textbox", name="Senha", exact=True).fill(
                    "fixture-secret"
                )
                page.get_by_role("button", name="Entrar", exact=True).click()
                page.wait_for_url("**/gerenciamento")
                expect(export).to_be_enabled()
                page.wait_for_timeout(650)
                assert len(downloads) == count
            elif profile == "Administrador":
                page.screenshot(
                    path=Path(".impeccable/review/navigation") / "excel-desktop.png"
                )
            page.context.close()
        browser.close()


if __name__ == "__main__":
    run()
