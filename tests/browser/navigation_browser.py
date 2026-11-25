"""Opt-in Edge/Playwright verification against navigation_fixture.py + Vite.

No remote Xano/ASAAS requests are permitted by the fixture backend.
Writes artifacts under the ignored .impeccable/review/navigation directory.
"""

import json
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

OUT = Path(".impeccable/review/navigation")
PREFIX = "reflex___state____state.app___state___auth_state____auth_state."
OUT.mkdir(parents=True, exist_ok=True)


def run():
    results, errors = {}, []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        values = {
            PREFIX + key + "_rx_state_": value
            for key, value in {
                "token": "fixture-account-a",
                "profile": "Gerente",
                "account_id": "17",
                "user_name": "Conta A",
            }.items()
        }
        context.add_init_script(
            "if(!sessionStorage.fixtureInitialized){Object.entries("
            + json.dumps(values)
            + ").forEach(([k,v])=>localStorage.setItem(k,v));sessionStorage.fixtureInitialized='1';}"
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))

        def control(mode="normal", delay=0.35, reset=False):
            return page.request.post(
                "http://127.0.0.1:8001/fixture-control",
                data={"mode": mode, "delay": delay, "reset": reset},
            )

        def goto(path):
            # React Router observes popstate: keep the same websocket/session.
            page.evaluate(
                "path => {window.history.pushState({idx:(history.state?.idx??0)+1},'',path);window.dispatchEvent(new PopStateEvent('popstate'));}",
                path,
            )
            page.wait_for_url("**" + path)

        control(reset=True)
        start = time.monotonic()
        page.goto("http://localhost:3000/veiculos", wait_until="domcontentloaded")
        expect(page.get_by_text("Veículo visual 2", exact=True)).to_be_visible()
        results["cold_vehicles_ms"] = round((time.monotonic() - start) * 1000, 1)
        navigation = []
        for label, path, first, last in [
            ("Peças e estoque", "/pecas", "Peça visual 1", "Peça visual 2"),
            ("Clientes", "/clientes", "Cliente visual 1", "Cliente visual 2"),
            ("Veículos", "/veiculos", "Veículo visual 1", "Veículo visual 2"),
        ]:
            page.evaluate(
                """([path,first,last])=>{
                window.fixtureObserver?.disconnect();
                const marks=window.fixtureMarks={start:performance.now()};
                window.fixtureObserver=new MutationObserver(()=>{
                    if(location.pathname!==path)return;
                    const text=document.querySelector('.content')?.innerText||'';
                    const elapsed=performance.now()-marks.start;
                    if(text.includes('Carregando dados')&&!marks.feedback)marks.feedback=elapsed;
                    if(marks.feedback&&text.includes(first)&&!marks.first)marks.first=elapsed;
                    if(marks.feedback&&text.includes(last)&&!marks.complete)marks.complete=elapsed;
                });
                window.fixtureObserver.observe(document.body,{childList:true,subtree:true,characterData:true});
            }""",
                [path, first, last],
            )
            start = time.monotonic()
            page.get_by_role("link", name=label, exact=True).click()
            page.wait_for_url("**" + path)
            route_ms = (time.monotonic() - start) * 1000
            expect(page.get_by_text("Carregando dados…", exact=True)).to_be_visible()
            feedback_ms = (time.monotonic() - start) * 1000
            early = page.locator(".content").inner_text()
            assert not ("Veículo visual" in early and path != "/veiculos"), early
            assert not ("Cliente visual" in early and path != "/clientes"), early
            expect(page.get_by_text(first, exact=True).first).to_be_visible()
            first_ms = (time.monotonic() - start) * 1000
            expect(page.get_by_text(last, exact=True).first).to_be_visible()
            complete_ms = (time.monotonic() - start) * 1000
            marks = page.evaluate("window.fixtureMarks")
            feedback_ms, first_ms, complete_ms = (
                marks["feedback"],
                marks["first"],
                marks["complete"],
            )
            assert feedback_ms < first_ms < complete_ms, marks
            navigation.append(
                {
                    "path": path,
                    "route_ms": round(route_ms, 1),
                    "feedback_ms": round(feedback_ms, 1),
                    "first_data_ms": round(first_ms, 1),
                    "complete_ms": round(complete_ms, 1),
                    "early_content": early,
                }
            )
        results["navigations"] = navigation
        results["measurement_calls"] = page.request.get(
            "http://127.0.0.1:8001/fixture-control"
        ).json()["calls"]

        # Interaction is accepted before slow HTTP returns; no old resource cards.
        control(delay=1.2, reset=True)
        page.get_by_role("link", name="Clientes", exact=True).click()
        expect(page.get_by_text("Carregando dados…", exact=True)).to_be_visible()
        page.get_by_role("textbox", name="Buscar clientes").fill("Ana")
        page.wait_for_timeout(400)
        start = time.monotonic()
        page.get_by_role("link", name="Vendas", exact=True).click()
        expect(page.get_by_role("heading", name="Vendas realizadas")).to_be_visible()
        results["navigate_while_pending_ms"] = round(
            (time.monotonic() - start) * 1000, 1
        )
        assert results["navigate_while_pending_ms"] < 1200
        page.wait_for_timeout(1500)
        assert (
            "Ana"
            not in page.get_by_placeholder(
                "Pesquisar cliente, vendedor ou ID"
            ).input_value()
        )

        # Slow catalogs cannot hold back the main sales list.
        control("slow-methods", reset=True)
        goto("/pecas")
        goto("/vendas")
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_be_visible()
        expect(page.get_by_role("combobox").first).to_be_disabled()
        expect(page.get_by_role("combobox").first).to_be_enabled(timeout=5000)

        # Query B wins over a slower query A, including final loading state.
        control("race", delay=0.2)
        search = page.get_by_placeholder("Pesquisar cliente, vendedor ou ID")
        search.fill("old")
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Filtrar", exact=True).click()
        page.wait_for_timeout(100)
        search.fill("new")
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Filtrar", exact=True).click()
        expect(page.get_by_text("newCliente visual 1", exact=True)).to_be_visible()
        page.wait_for_timeout(1500)
        expect(page.get_by_text("newCliente visual 1", exact=True)).to_be_visible()
        expect(page.get_by_text("oldCliente visual 1", exact=True)).to_have_count(0)

        # Details A/B in the same browser session; old errors never surface.
        for mode in ("race", "stale-error"):
            control(mode, delay=0.2)
            goto("/clientes/1")
            page.wait_for_timeout(100)
            goto("/clientes/2")
            expect(
                page.get_by_role("heading", name="Detalhe visual 2", exact=True)
            ).to_be_visible()
            page.wait_for_timeout(1600)
            expect(
                page.get_by_role("heading", name="Detalhe visual 2", exact=True)
            ).to_be_visible()
            expect(
                page.get_by_text("Erro antigo do detalhe 1", exact=True)
            ).to_have_count(0)
        control("stale-error", delay=.1)
        goto("/clientes/1")
        expect(page.get_by_text("Erro antigo do detalhe 1", exact=True)).to_be_visible()
        control(delay=.8)
        goto("/clientes/2")
        expect(page.get_by_text("Erro antigo do detalhe 1", exact=True)).to_have_count(0)
        expect(page.get_by_role("heading", name="Detalhe visual 2", exact=True)).to_be_visible()
        goto("/vendas/1")
        expect(
            page.get_by_role("heading", name="Pagamento da venda #1")
        ).to_be_visible()
        goto("/vendas/2")
        expect(
            page.get_by_role("heading", name="Pagamento da venda #2")
        ).to_be_visible()
        expect(
            page.get_by_role("link", name="Abrir link de pagamento")
        ).to_have_attribute("href", "https://sandbox.asaas.com/i/fixture-2")

        # Auxiliary failure is local to its indicators; main clients remain usable.
        control("sales-error", delay=0.2)
        goto("/clientes")
        page.get_by_role("textbox", name="Buscar clientes").fill("")
        expect(page.get_by_text("Cliente visual 2", exact=True)).to_be_visible()
        expect(page.get_by_text("Indisponível", exact=True).first).to_be_visible()
        assert "Vendas indisponíveis" not in page.locator(".content").inner_text()

        # Retain page one on page-two failure; partial search isn't final empty.
        control("page-error", delay=0.2)
        page.get_by_role("link", name="Peças e estoque", exact=True).click()
        expect(page.get_by_text("Peça visual 1", exact=True)).to_be_visible()
        expect(
            page.get_by_text(
                "Falha controlada na segunda página. Atualize a lista.", exact=True
            )
        ).to_be_visible()
        page.get_by_role("textbox", name="Buscar registros").fill("inexistente")
        expect(
            page.get_by_text(
                "Sem correspondências nas peças carregadas até agora.", exact=True
            )
        ).to_be_visible()
        control(delay=0.2)
        page.get_by_role("textbox", name="Buscar registros").fill("")
        page.get_by_role("button", name="Atualizar lista").click()
        expect(page.get_by_text("Peça visual 2", exact=True)).to_be_visible()

        # Editing a row while a later page is pending invalidates that read.
        control("write-during-read", delay=0.2)
        page.get_by_role("link", name="Clientes", exact=True).click()
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_be_visible()
        page.get_by_role("button", name="Opções do cliente").first.click()
        page.get_by_role("menuitem", name="Editar cliente").click()
        page.get_by_role("textbox", name="Nome completo", exact=True).fill(
            "Cliente atualizado"
        )
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Salvar alterações").click()
        expect(page.get_by_text("Cliente atualizado", exact=True)).to_be_visible()
        expect(page.get_by_role("status").filter(has_text="Cadastro do cliente atualizado.")).to_be_visible()
        page.wait_for_timeout(1800)
        expect(page.get_by_text("Cliente atualizado", exact=True)).to_be_visible()
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_have_count(0)

        # Timeout remains recoverable. No automatic repeat of writes exists.
        control("timeout", delay=0.2)
        page.get_by_role("link", name="Peças e estoque", exact=True).click()
        expect(
            page.get_by_text(
                "Não foi possível conectar ao Xano. Verifique a URL e a rede.",
                exact=True,
            )
        ).to_be_visible()
        control("empty", delay=0.2)
        page.get_by_role("button", name="Atualizar lista").click()
        expect(
            page.get_by_text("A API não retornou peças para esta consulta.", exact=True)
        ).to_be_visible()

        # Large collection: first client page precedes completeness and auxiliary sales.
        control("large", delay=0.12, reset=True)
        start = time.monotonic()
        page.get_by_role("link", name="Clientes", exact=True).click()
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_be_visible()
        large_first = (time.monotonic() - start) * 1000
        expect(page.get_by_text("1000", exact=True).first).to_be_visible(timeout=15000)
        large_complete = (time.monotonic() - start) * 1000
        results["large_1000_clients"] = {
            "first_ms": round(large_first, 1),
            "complete_ms": round(large_complete, 1),
        }

        # Preserve preferences, keyboard focus, and responsive feedback in all themes.
        control(delay=0.2)
        for theme in ("dark", "light"):
            page.evaluate(
                "theme=>document.documentElement.setAttribute('data-app-theme',theme)",
                theme,
            )
            for width in (1440, 768, 390):
                page.set_viewport_size({"width": width, "height": 900})
                page.keyboard.press("Tab")
                assert page.evaluate("document.activeElement.tagName") != "BODY"
                assert page.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth + 1"
                )
                page.screenshot(path=str(OUT / f"clients-{theme}-{width}.png"))
        page.emulate_media(color_scheme="light")
        page.evaluate(
            "document.documentElement.setAttribute('data-app-theme', matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')"
        )
        results["automatic_theme"] = page.locator("html").get_attribute(
            "data-app-theme"
        )
        page.set_viewport_size({"width": 1440, "height": 900})

        page.get_by_role("link", name="Configurações", exact=True).click()
        page.get_by_role("textbox", name="Nome de exibição").fill("Nome personalizado")
        page.get_by_role("textbox", name="Título do Dashboard").fill("Meu painel")
        page.get_by_role("button", name="Automático").click()
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Salvar personalização").click()
        page.get_by_role("link", name="Dashboard", exact=True).click()
        expect(page.locator("html")).to_have_attribute("data-app-theme", "light")
        expect(page.locator(".radix-themes.light")).to_have_count(1)
        expect(
            page.get_by_role("heading", name="Meu painel", exact=True)
        ).to_be_visible()
        expect(
            page.get_by_text("Gerente: Nome personalizado", exact=True)
        ).to_be_visible()
        page.reload()
        expect(page.locator("html")).to_have_attribute("data-app-theme", "light")
        expect(page.locator(".radix-themes.light")).to_have_count(1)
        expect(
            page.get_by_role("heading", name="Meu painel", exact=True)
        ).to_be_visible()
        page.emulate_media(color_scheme="dark")
        expect(page.locator("html")).to_have_attribute("data-app-theme", "dark")
        expect(page.locator(".radix-themes.dark")).to_have_count(1)
        page.emulate_media(color_scheme="light")
        expect(page.locator("html")).to_have_attribute("data-app-theme", "light")
        expect(page.locator(".radix-themes.light")).to_have_count(1)
        with page.expect_download() as download:
            page.get_by_role("button", name="Exportar Excel").click()
        assert download.value.suggested_filename.endswith(".xlsx")
        assert download.value.path().read_bytes().startswith(b"PK\x03\x04")
        expect(page.get_by_role("link", name="Auditoria", exact=True)).to_have_count(0)
        page.get_by_role("link", name="Clientes", exact=True).click()
        expect(page.get_by_role("button", name="Atualizar lista")).to_be_enabled()

        # Logout during a pending read, then log into a different fixture account.
        control(delay=1, reset=True)
        page.get_by_role("button", name="Atualizar lista").click()
        page.get_by_role("button", name="Sair", exact=True).click()
        page.wait_for_url("**/login")
        expect(
            page.get_by_role("heading", name="Acesse sua concessionária")
        ).to_be_visible()
        page.get_by_role("textbox", name="E-mail", exact=True).fill(
            "contab@example.test"
        )
        page.get_by_role("textbox", name="Senha", exact=True).fill("fixture-secret")
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Entrar", exact=True).click()
        expect(page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible(
            timeout=8000
        )
        page.get_by_role("link", name="Clientes", exact=True).click()
        expect(page.get_by_text("Conta B Cliente visual 1", exact=True)).to_be_visible(
            timeout=8000
        )
        expect(page.get_by_text("Cliente atualizado", exact=True)).to_have_count(0)
        stored = page.evaluate(
            "Object.entries(localStorage).find(([k])=>k.endsWith('preferences_json_rx_state_'))?.[1]"
        )
        assert stored and json.loads(stored)["17"]["dashboard_title"] == "Meu painel"
        expect(
            page.get_by_text("Gerente: Nome personalizado", exact=True)
        ).to_have_count(0)
        results["scenarios_passed"] = [
            "pending-navigation-keyboard",
            "sales-before-methods",
            "query-race",
            "detail-race-and-old-error",
            "payment-detail-ID",
            "auxiliary-error-isolation",
            "partial-page-retry-search",
            "write-during-read",
            "timeout-empty",
            "large-progress",
            "responsive-themes-focus",
            "logout-login",
            "personalization-system-theme-excel",
        ]
        results["errors"] = errors
        assert not errors, errors
        (OUT / "final-browser.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(results, ensure_ascii=True))
        browser.close()


if __name__ == "__main__":
    run()
