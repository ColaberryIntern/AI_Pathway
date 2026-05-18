from playwright.sync_api import sync_playwright
import time

BASE = "http://95.216.199.47:3000"
ANALYSIS_ID = "9b692fe9-1f13-4ddf-8c8c-27376e96a6d0"

JS = r"""() => {
  const buttons = Array.from(document.querySelectorAll('button')).filter(
    b => /^\s*1\s*Aware\b/i.test(b.textContent || '')
  );
  return buttons.slice(0, 4).map((btn, idx) => {
    const ancestors = [];
    let el = btn.parentElement;
    for (let i = 0; i < 10 && el; i++) {
      const text = (el.innerText || '').slice(0, 120).replace(/\n/g, ' | ');
      ancestors.push({
        tag: el.tagName,
        cls: (el.className || '').slice(0, 100),
        text
      });
      el = el.parentElement;
    }
    return { idx, ancestors };
  });
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(f"{BASE}/analysis/{ANALYSIS_ID}?view=skill_selection", wait_until="load")
    time.sleep(3)
    info = pg.evaluate(JS)
    for bi in info:
        print(f"=== L1 BUTTON #{bi['idx']} ===")
        for h, a in enumerate(bi["ancestors"]):
            print(f"  hop {h}: <{a['tag']} class={a['cls']!r}>")
            print(f"          text: {a['text']!r}")
    b.close()
