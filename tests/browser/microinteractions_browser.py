"""Verify sale feedback in Edge against navigation_fixture.py and Vite."""

import json
import re

from playwright.sync_api import expect, sync_playwright


def run():
    prefix = "reflex___state____state.app___state___auth_state____auth_state."
    auth = {
        prefix + key + "_rx_state_": value
        for key, value in {
            "token": "fixture-account-a", "profile": "Gerente", "account_id": "17", "user_name": "Conta A",
        }.items()
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 900}, has_touch=True, color_scheme="dark", reduced_motion="reduce",
        )
        context.add_init_script(
            "Object.entries(" + json.dumps(auth) + ").forEach(([k,v])=>localStorage.setItem(k,v));"
            "Object.defineProperty(navigator, 'clipboard', {value: {writeText: async url => {"
            "if (window.failCopy) throw new Error('Clipboard denied'); window.copiedUrl = url; }}});"
        )
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def control(mode, reset=False):
            return page.request.post(
                "http://127.0.0.1:8001/fixture-control", data={"mode": mode, "delay": 0.25, "reset": reset},
            ).json()["calls"]

        control("motion-link-error", reset=True)
        page.goto("http://localhost:3000/vendas/nova")
        customer = page.get_by_role("combobox", name="Cliente da venda")
        expect(customer).to_be_enabled()
        customer.press("Enter")
        page.get_by_role("option", name="Cliente visual 1", exact=True).press("Enter")
        vehicle = page.get_by_role("button", name="Selecionar veículo").first
        vehicle.tap()
        feedback = page.locator(".sale-item-feedback")
        expect(feedback).to_contain_text("Veículo visual 1 · adicionado")
        expect(feedback).to_have_css("animation-name", "none")
        feedback.evaluate("node => node.dataset.original = 'true'")
        vehicle.tap()
        expect(feedback).to_have_attribute("data-original", "true")
        page.get_by_role("button", name="Adicionar", exact=True).first.tap()
        expect(feedback).to_contain_text("Peça visual 1 · adicionada")
        total = page.locator(".sale-total-amount")
        expect(total).to_contain_text("40.150,00")
        page.get_by_role("button", name="Remover", exact=True).last.tap()
        expect(feedback).to_contain_text("removida")
        expect(total).to_contain_text("40.000,00")
        page.get_by_role("button", name="Remover", exact=True).tap()
        expect(total).to_contain_text("0,00")
        vehicle.tap()
        page.get_by_role("button", name="Adicionar", exact=True).first.tap()
        page.get_by_role("button", name="Criar venda e gerar link").tap()
        expect(page.get_by_text("Venda criada", exact=True)).to_be_visible()
        expect(page.locator(".interaction-panel")).to_have_css("animation-name", "none")
        expect(page.get_by_role("alert").filter(has_text="ASAAS indisponível")).to_be_visible()
        expect(page.get_by_text("Link disponível.", exact=False)).to_have_count(0)
        control("normal")
        page.get_by_role("button", name="Gerar ou recuperar link").tap()
        expect(page.get_by_text("Link disponível.", exact=False)).to_be_visible()
        calls = control("normal")
        assert sum((call["method"], call["path"]) == ("POST", "/vendas") for call in calls) == 1

        copy = page.get_by_role("button", name="Copiar link")
        copied = page.locator("#sale-copy-status")
        copy.tap()
        expect(copied).to_have_text("Link copiado")
        assert page.evaluate("window.copiedUrl") == "https://sandbox.asaas.com/i/fixture-42"
        page.evaluate("window.failCopy = true")
        copy.tap()
        expect(copied).to_have_text("Não foi possível copiar o link.")
        page.get_by_role("link", name="Ver detalhes da venda").tap()
        page.wait_for_url("**/vendas/42")
        pending = page.get_by_role("status").filter(has_text="Aguardando pagamento")
        expect(pending).to_be_visible()
        update = page.get_by_role("button", name="Atualizar pagamento")
        update.tap()
        expect(update).to_be_enabled()
        marker = re.compile(r"\binteraction-feedback\b")
        expect(pending).not_to_have_class(marker)
        control("motion-payment-confirmed")
        update.tap()
        confirmed = page.get_by_role("status").filter(has_text="Pagamento confirmado")
        expect(confirmed).to_have_class(marker)
        expect(confirmed).to_have_css("animation-name", "none")
        update.tap()
        expect(update).to_be_enabled()
        expect(confirmed).not_to_have_class(marker)
        expect(page.get_by_role("link", name="Vendas", exact=True)).to_have_attribute("aria-current", "page")

        control("motion-client-error")
        page.goto("http://localhost:3000/clientes/novo")
        for field, value in {"Nome": "Cliente teste", "CPF": "00000000000", "Telefone": "11900000000", "E-mail": "inválido"}.items():
            page.get_by_role("textbox", name=field, exact=True).fill(value)
        save = page.get_by_role("button", name="Salvar", exact=True)
        save.tap()
        email = page.get_by_role("textbox", name="E-mail", exact=True)
        expect(email).to_be_focused()
        assert email.evaluate("node => node.matches(':user-invalid')")
        email.fill("cliente@example.test")
        email.press("Enter")
        expect(page.get_by_role("alert").filter(has_text="Cadastro indisponível")).to_be_visible()
        control("normal")
        save.tap()
        expect(page.get_by_role("status").filter(has_text="Registro salvo")).to_be_visible()

        page.get_by_role("link", name="Clientes", exact=True).tap()
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_be_visible()
        page.get_by_role("button", name="Opções do cliente").first.tap()
        page.get_by_role("menuitem", name=re.compile("Excluir")).tap()
        delete = page.get_by_role("button", name="Confirmar exclusão")
        control("motion-client-error")
        delete.tap()
        expect(page.get_by_role("alert").filter(has_text="Exclusão indisponível")).to_be_visible()
        control("motion-delete")
        delete.tap()
        expect(page.get_by_role("status").filter(has_text="Cliente excluído")).to_be_visible()
        expect(page.locator("#client-search-focus")).to_be_focused()
        expect(page.get_by_text("Cliente visual 1", exact=True)).to_have_count(0)
        control("normal")
        assert not errors, errors
        browser.close()
    print("Microinterações de vendas e clientes verificadas.")


if __name__ == "__main__":
    run()
