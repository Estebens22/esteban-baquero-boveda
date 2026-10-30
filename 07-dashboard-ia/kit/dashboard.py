#!/usr/bin/env python3
"""Dashboard que decide con IA — kit de La Bóveda (Esteban Baquero).

Un tablero no sirve de nada si solo muestra números. Este lee la señal,
la interpreta y propone la SIGUIENTE acción.

Tres piezas:
  1. CARGA      — lee data/ventas.csv (fecha, ingresos, pedidos, gasto_ads).
  2. KPIs       — el código calcula las cifras y detecta señales (aritmética exacta).
  3. DECISIÓN   — modo MOCK (reglas) o LLM real (OPENAI_API_KEY) interpreta y recomienda.

Corre con **solo librería estándar** de Python.

Uso:
  python3 dashboard.py            # imprime KPIs + decisión y escribe dashboard.html
  python3 dashboard.py --demo     # self-check: valida KPIs y que la señal se dispare

ponytail: KPIs en memoria sobre un CSV. Para fuentes vivas (DB/API) o millones de
filas, la capa de CARGA se cambia por una query; KPIs y DECISIÓN no cambian.
"""
import os, sys, csv, json, html, urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "ventas.csv")
OUT = os.path.join(HERE, "dashboard.html")


# ---------- 1. CARGA ----------
def cargar(path=DATA):
    filas = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            filas.append({
                "fecha": datetime.strptime(r["fecha"], "%Y-%m-%d").date(),
                "ingresos": float(r["ingresos"]),
                "pedidos": int(r["pedidos"]),
                "gasto_ads": float(r["gasto_ads"]),
            })
    filas.sort(key=lambda x: x["fecha"])
    return filas


# ---------- 2. KPIs ----------
def _pct(nuevo, viejo):
    return (nuevo - viejo) / viejo if viejo else 0.0


def kpis(filas):
    """Cifras exactas + comparación última semana vs semana previa."""
    if not filas:
        raise ValueError("no hay datos")
    ing = sum(f["ingresos"] for f in filas)
    ped = sum(f["pedidos"] for f in filas)
    ads = sum(f["gasto_ads"] for f in filas)
    ult, prev = filas[-7:], filas[-14:-7]
    ing_ult = sum(f["ingresos"] for f in ult)
    ing_prev = sum(f["ingresos"] for f in prev)
    roas_ult = ing_ult / sum(f["gasto_ads"] for f in ult) if ult else 0.0
    roas_prev = ing_prev / sum(f["gasto_ads"] for f in prev) if prev else 0.0
    return {
        "dias": len(filas),
        "ingresos_total": round(ing),
        "pedidos_total": ped,
        "aov": round(ing / ped) if ped else 0,            # ticket promedio
        "roas": round(ing / ads, 2) if ads else 0.0,      # retorno sobre gasto en ads
        "ingresos_wow": round(_pct(ing_ult, ing_prev), 3),   # semana vs semana
        "roas_wow": round(_pct(roas_ult, roas_prev), 3),
        "roas_ult_semana": round(roas_ult, 2),
    }


def señales(k):
    """Reglas que convierten KPIs en banderas. Cada una es honesta y accionable."""
    s = []
    if k["ingresos_wow"] <= -0.05:
        s.append(("alta", f"Ingresos cayeron {k['ingresos_wow']*100:.0f}% semana a semana."))
    elif k["ingresos_wow"] >= 0.05:
        s.append(("info", f"Ingresos subieron {k['ingresos_wow']*100:.0f}% semana a semana."))
    if k["roas_wow"] <= -0.1:
        s.append(("alta", f"ROAS bajó {k['roas_wow']*100:.0f}%: estás gastando más en ads para vender menos."))
    if k["roas_ult_semana"] < 3:
        s.append(("media", f"ROAS de la última semana en {k['roas_ult_semana']} (por debajo de 3x)."))
    if not s:
        s.append(("info", "Métricas estables, sin señales de alerta."))
    return s


# ---------- 3. DECISIÓN ----------
def decidir_mock(k, s):
    """Sin API key: decisión por reglas (transparente, sin inventar)."""
    alertas = [m for sev, m in s if sev == "alta"]
    if alertas:
        accion = ("Baja el gasto en ads 15% esta semana y mide ROAS a 7 días. "
                  "Si el ROAS no mejora, el problema es de oferta/página, no de tráfico.")
        causa = "Más inversión en ads sin más ingresos: el tráfico extra no está convirtiendo."
        lectura = " ".join(alertas)
    elif any(sev == "media" for sev, _ in s):
        accion = "Revisa las 3 campañas con menor ROAS y pausa la peor; redistribuye su presupuesto."
        causa = "El retorno está por debajo del umbral sano aunque no haya caída brusca."
        lectura = "ROAS flojo pero sin desplome."
    else:
        accion = "Mantén el presupuesto y sube 10% la campaña de mejor ROAS para probar escala."
        causa = "Negocio estable; hay margen para probar crecimiento controlado."
        lectura = "Todo en verde."
    return (f"LECTURA: {lectura}\n"
            f"CAUSA PROBABLE: {causa}\n"
            f"SIGUIENTE ACCIÓN: {accion}\n\n"
            "ℹ️  Con OPENAI_API_KEY, el modelo redacta esta decisión con más matiz.")


def decidir_llm(k, s):
    """Con OPENAI_API_KEY: el modelo interpreta los KPIs (no recalcula)."""
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    sys_prompt = ("Eres un analista de negocio. Te doy KPIs ya calculados y señales. "
                  "NO recalcules. Responde en español neutro en 3 bloques: LECTURA, "
                  "CAUSA PROBABLE, SIGUIENTE ACCIÓN (una sola, medible, esta semana).")
    user = (f"KPIs:\n{json.dumps(k, ensure_ascii=False, indent=2)}\n\n"
            f"Señales:\n" + "\n".join(f"- [{sev}] {m}" for sev, m in s) +
            "\n\nPregunta: ¿Qué está pasando y qué hago esta semana?")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user}],
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(f"{base}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def decidir(k, s):
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return decidir_llm(k, s)
        except Exception as e:
            return f"(LLM falló: {e} — caigo a reglas)\n\n" + decidir_mock(k, s)
    return decidir_mock(k, s)


# ---------- Dashboard HTML ----------
def render_html(k, s, decision):
    sev_color = {"alta": "#c2410c", "media": "#b45309", "info": "#0061fe"}
    cards = [
        ("Ingresos (total)", f"${k['ingresos_total']:,}"),
        ("Pedidos", f"{k['pedidos_total']:,}"),
        ("Ticket promedio", f"${k['aov']:,}"),
        ("ROAS", f"{k['roas']}x"),
        ("Ingresos sem/sem", f"{k['ingresos_wow']*100:+.0f}%"),
        ("ROAS sem/sem", f"{k['roas_wow']*100:+.0f}%"),
    ]
    kpi_html = "".join(
        f'<div class="card"><div class="lbl">{html.escape(l)}</div><div class="val">{html.escape(v)}</div></div>'
        for l, v in cards)
    sig_html = "".join(
        f'<li style="border-left:4px solid {sev_color.get(sev,"#999")}">{html.escape(m)}</li>'
        for sev, m in s)
    dec_html = html.escape(decision).replace("\n", "<br>")
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard que decide con IA</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#f6f8fa;color:#1a1d21;margin:0;padding:32px}}
.wrap{{max-width:900px;margin:0 auto}}
h1{{font-size:26px;margin:0 0 4px}}.sub{{color:#5b6675;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}}
.card{{background:#fff;border:1px solid #eef0f2;border-radius:14px;padding:18px}}
.card .lbl{{font-size:12px;color:#5b6675;font-weight:700;text-transform:uppercase;letter-spacing:.5px}}
.card .val{{font-size:24px;font-weight:800;margin-top:6px}}
h2{{font-size:16px;margin:28px 0 10px;text-transform:uppercase;letter-spacing:1px;color:#5b6675}}
ul{{list-style:none;padding:0;margin:0}}ul li{{background:#fff;border:1px solid #eef0f2;border-radius:10px;padding:12px 14px;margin-bottom:8px;padding-left:14px}}
.decision{{background:#fff;border:1px solid #eef0f2;border-radius:14px;padding:22px;line-height:1.6;font-size:15px}}
footer{{color:#5b6675;font-size:13px;margin-top:32px;text-align:center}}
</style></head><body><div class="wrap">
<h1>Dashboard que decide con IA</h1>
<p class="sub">Últimos {k['dias']} días · no solo muestra números: los interpreta.</p>
<div class="grid">{kpi_html}</div>
<h2>Señales detectadas</h2><ul>{sig_html}</ul>
<h2>Decisión</h2><div class="decision">{dec_html}</div>
<footer>Esteban Baquero · La Bóveda — De una idea a un sistema que funciona.</footer>
</div></body></html>"""


def demo():
    """Self-check: KPIs exactos sobre data de muestra y la señal de caída se dispara."""
    filas = cargar()
    assert len(filas) == 21, f"esperaba 21 filas, hay {len(filas)}"
    k = kpis(filas)
    assert k["pedidos_total"] == sum(f["pedidos"] for f in filas), "pedidos no cuadra"
    assert k["aov"] == round(k["ingresos_total"] / k["pedidos_total"]), "AOV mal calculado"
    # la muestra está armada con la última semana a la baja → debe haber señal 'alta'
    s = señales(k)
    assert any(sev == "alta" for sev, _ in s), f"esperaba una señal alta, salió {s}"
    assert k["ingresos_wow"] < 0, f"esperaba caída sem/sem, dio {k['ingresos_wow']}"
    d = decidir_mock(k, s)
    assert "SIGUIENTE ACCIÓN" in d, "la decisión no trae acción"
    print(f"✓ demo OK — ingresos sem/sem {k['ingresos_wow']*100:.0f}%, "
          f"ROAS {k['roas']}x, señales={len(s)}, decisión con acción concreta")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        filas = cargar()
        k = kpis(filas)
        s = señales(k)
        d = decidir(k, s)
        print("KPIs:\n" + json.dumps(k, ensure_ascii=False, indent=2))
        print("\nSeñales:")
        for sev, m in s:
            print(f"  [{sev}] {m}")
        print("\nDecisión:\n" + d)
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(render_html(k, s, d))
        print(f"\n→ Dashboard escrito en {OUT} (ábrelo en el navegador)")
