"""Optional visual QA using Playwright and an installed Chrome browser."""

import json
from pathlib import Path


def main() -> None:
    """Capture desktop and mobile screens and exercise the main simulation flow."""
    from playwright.sync_api import sync_playwright

    output = Path("reports/ui")
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(
            viewport={"width": 1440, "height": 1060}, device_scale_factor=1, reduced_motion="reduce"
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8501", wait_until="networkidle")
        page.get_by_role("heading", name="Anticipez les départs.").wait_for(timeout=60000)
        page.locator('[data-testid="stPlotlyChart"]').last.wait_for()
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)"
        )
        page.wait_for_timeout(700)
        page.screenshot(path=str(output / "overview-desktop.png"), full_page=True)
        sidebar = page.get_by_test_id("stSidebar")
        sidebar.get_by_text("Simulateur", exact=True).click()
        page.get_by_role("button", name="Analyser le risque de churn").click()
        page.get_by_text("PROBABILITÉ ESTIMÉE DE CHURN", exact=True).wait_for()
        page.get_by_role("button", name="Télécharger cette analyse").wait_for()
        page.wait_for_function("!document.querySelector('[data-testid=stStatusWidget]')")
        page.wait_for_timeout(700)
        page.screenshot(path=str(output / "simulator-desktop.png"), full_page=True)
        sidebar.get_by_text("Le modèle", exact=True).click()
        page.get_by_role("heading", name="Un modèle simple. Des preuves concrètes.").wait_for()
        page.wait_for_function("!document.querySelector('[data-stale=true]')")
        page.wait_for_timeout(700)
        page.screenshot(path=str(output / "model-desktop.png"), full_page=True)
        sidebar.get_by_text("Explorer les données", exact=True).click()
        page.get_by_role("heading", name="Derrière les chiffres, des comportements.").wait_for()
        page.wait_for_function("!document.querySelector('[data-stale=true]')")
        page.get_by_role("button", name="Stop", exact=True).wait_for(state="hidden")
        page.locator('[data-testid="stPlotlyChart"]').last.wait_for()
        page.wait_for_timeout(700)
        if page.get_by_test_id("stException").count():
            raise RuntimeError("Explorer rendered an application exception")
        page.screenshot(path=str(output / "explorer-desktop.png"), full_page=True)
        sidebar.get_by_text("Vue d’ensemble", exact=True).click()
        page.get_by_role("heading", name="Anticipez les départs.").wait_for()
        page.set_viewport_size({"width": 390, "height": 844})
        collapse = page.get_by_test_id("stSidebarCollapseButton").get_by_role("button")
        if collapse.is_visible():
            collapse.click()
        page.wait_for_function(
            "document.querySelector('[data-testid=stSidebar]').getBoundingClientRect().right <= 0"
        )
        page.wait_for_timeout(700)
        page.screenshot(path=str(output / "overview-mobile.png"), full_page=True)
        page.mouse.wheel(0, 1200)
        page.wait_for_timeout(700)
        page.screenshot(path=str(output / "overview-mobile-detail.png"), full_page=True)
        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        (output / "browser-checks.json").write_text(
            json.dumps({"page_errors": errors, "mobile_horizontal_overflow": overflow}, indent=2)
        )
        browser.close()
        if errors or overflow:
            raise RuntimeError("Visual QA found browser errors or horizontal overflow")
        print("Desktop/mobile screenshots saved; prediction flow passed; no page errors.")


if __name__ == "__main__":
    main()
