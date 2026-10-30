#!/usr/bin/env python3
"""
rpa.py — Un robot que opera la web como tú, con SOLO librería estándar.

Navega, lee formularios, los llena, los envía y extrae datos — respetando
robots.txt, con rate-limit (pausa entre pedidos) y reintentos con backoff.
Sin Selenium, sin Playwright, sin dependencias.

La honestidad del kit: esto opera la web por HTTP, no renderiza JavaScript.
Sirve para la mayoría de formularios y páginas con HTML en el servidor. Si el
sitio arma todo con JS en el navegador, ahí sí toca un navegador real (y lo
decís con ética, no lo escondés). Ver ETICA.md.

Uso:
  python3 rpa.py --demo            # self-check offline (no toca la red)
  python3 rpa.py get   <url>       # descarga la página y muestra su título
  python3 rpa.py form  <url>       # lista los formularios y sus campos
  python3 rpa.py table <url>       # extrae la primera tabla como filas
"""
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

# Identifícate siempre. Un bot honesto dice quién es y deja cómo contactarte.
USER_AGENT = "EstebanBaqueroRPA/1.0 (+https://estebanbaquero.com; robot educativo)"
DELAY = 1.0      # segundos entre pedidos: no martilles el servidor
RETRIES = 3      # reintentos ante fallos transitorios (5xx / red)


# ----------------------------------------------------------------------------
# 1) El navegador controlado: parsers de HTML con la librería estándar
# ----------------------------------------------------------------------------
class _FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._cur = {
                "action": a.get("action", ""),
                "method": (a.get("method") or "get").lower(),
                "fields": {},
            }
        elif self._cur is not None and tag in ("input", "select", "textarea"):
            name = a.get("name")
            if name and a.get("type") != "submit":
                # value del HTML = valor por defecto (incluye tokens/hidden)
                self._cur["fields"][name] = a.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form" and self._cur is not None:
            self.forms.append(self._cur)
            self._cur = None


class _TableParser(HTMLParser):
    """Extrae la PRIMERA <table> como lista de filas (lista de celdas)."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._in_table = False
        self._done = False
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table" and not self._done:
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._row = []
        elif self._in_table and tag in ("td", "th"):
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if not self._in_table:
            return
        if tag in ("td", "th") and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif tag == "table":
            self._in_table = False
            self._done = True  # solo la primera tabla


class _TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self._grab = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._grab = True

    def handle_data(self, data):
        if self._grab:
            self.title = (self.title or "") + data

    def handle_endtag(self, tag):
        if tag == "title":
            self._grab = False


def parse_forms(html):
    p = _FormParser()
    p.feed(html)
    return p.forms


def parse_table(html):
    p = _TableParser()
    p.feed(html)
    return p.rows


def parse_title(html):
    p = _TitleParser()
    p.feed(html)
    return (p.title or "").strip()


# ----------------------------------------------------------------------------
# 2) Los pasos repetibles: llenar un formulario sin pisar sus tokens
# ----------------------------------------------------------------------------
def fill(form, data):
    """Devuelve el cuerpo a enviar: campos del form + tus datos encima.

    Clave: partimos de los campos que trae el form (hidden, csrf, defaults) y
    solo sobreescribimos lo que tú indicás. Así no borrás el token anti-CSRF
    que el servidor espera de vuelta.
    """
    body = dict(form.get("fields", {}))
    body.update(data)
    return body


# ----------------------------------------------------------------------------
# 3) El manejo de errores y reintentos: backoff y rate-limit
# ----------------------------------------------------------------------------
def backoff(intento):
    """Espera creciente entre reintentos: 1s, 2s, 4s..."""
    return DELAY * (2 ** intento)


def robots_from_text(texto, base_url):
    """Construye un lector de robots.txt desde texto (útil para testear)."""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(base_url, "/robots.txt"))
    rp.parse(texto.splitlines())
    return rp


class Robot:
    def __init__(self, user_agent=USER_AGENT, delay=DELAY, retries=RETRIES):
        self.ua = user_agent
        self.delay = delay
        self.retries = retries
        self._robots = {}  # cache por host

    def _allowed(self, url):
        """Respeta robots.txt. Si no se puede leer, asumimos permitido pero
        avisamos (fail-open con aviso: la ética es tuya, no del script)."""
        parts = urllib.parse.urlsplit(url)
        host = (parts.scheme, parts.netloc)
        rp = self._robots.get(host)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
            try:
                rp.read()
            except Exception:
                print("  aviso: no pude leer robots.txt; verifica los permisos a mano",
                      file=sys.stderr)
                rp = None
            self._robots[host] = rp
        return True if rp is None else rp.can_fetch(self.ua, url)

    def _open(self, req):
        last = None
        for intento in range(self.retries):
            try:
                time.sleep(self.delay)  # rate-limit: no martilles
                with urllib.request.urlopen(req, timeout=20) as r:
                    return r.read().decode(r.headers.get_content_charset() or "utf-8",
                                           "replace")
            except Exception as e:  # red/5xx transitorios → reintenta
                last = e
                espera = backoff(intento)
                print(f"  fallo ({e}); reintento en {espera:.0f}s", file=sys.stderr)
                time.sleep(espera)
        raise last

    def get(self, url):
        if not self._allowed(url):
            raise PermissionError(f"robots.txt no permite {url} para este bot")
        req = urllib.request.Request(url, headers={"User-Agent": self.ua})
        return self._open(req)

    def submit(self, form, data, base_url):
        """Llena el form y lo envía (GET o POST) resolviendo el action relativo."""
        body = fill(form, data)
        action = urllib.parse.urljoin(base_url, form.get("action") or base_url)
        enc = urllib.parse.urlencode(body)
        if form.get("method") == "post":
            if not self._allowed(action):
                raise PermissionError(f"robots.txt no permite {action}")
            req = urllib.request.Request(action, data=enc.encode(),
                                         headers={"User-Agent": self.ua})
            return self._open(req)
        return self.get(f"{action}?{enc}")


# ----------------------------------------------------------------------------
# Self-check offline — no toca la red, falla ruidoso si algo se rompe
# ----------------------------------------------------------------------------
def demo():
    # 1) leer un formulario: nombres y token preservados
    html_login = (
        '<form action="/login" method="post">'
        '<input name="user" value="">'
        '<input name="pass" type="password">'
        '<input name="csrf" value="abc123">'
        '<input type="submit" value="entrar">'
        "</form>"
    )
    forms = parse_forms(html_login)
    assert len(forms) == 1, forms
    f = forms[0]
    assert f["action"] == "/login" and f["method"] == "post"
    assert set(f["fields"]) == {"user", "pass", "csrf"}, f["fields"]
    assert f["fields"]["csrf"] == "abc123"  # el submit NO entra como campo

    # 2) llenar sin pisar el token anti-CSRF
    body = fill(f, {"user": "ana", "pass": "secreto"})
    assert body == {"user": "ana", "pass": "secreto", "csrf": "abc123"}, body

    # 3) extraer una tabla a filas
    html_table = (
        "<table>"
        "<tr><th>Nombre</th><th>Edad</th></tr>"
        "<tr><td>Ana</td><td>30</td></tr>"
        "<tr><td>Luis</td><td>25</td></tr>"
        "</table><table><tr><td>otra</td></tr></table>"
    )
    rows = parse_table(html_table)
    assert rows == [["Nombre", "Edad"], ["Ana", "30"], ["Luis", "25"]], rows

    # 4) título con tildes intacto
    assert parse_title("<title>Envíos y Devoluciones</title>") == "Envíos y Devoluciones"

    # 5) robots.txt respetado
    rp = robots_from_text("User-agent: *\nDisallow: /privado\n", "https://ejemplo.co")
    assert rp.can_fetch(USER_AGENT, "https://ejemplo.co/publico")
    assert not rp.can_fetch(USER_AGENT, "https://ejemplo.co/privado/datos")

    # 6) el backoff crece (reintentos con espera creciente)
    assert backoff(0) < backoff(1) < backoff(2)

    print("demo OK ✓  (form, fill, table, title, robots, backoff)")


def main(argv):
    if not argv or argv[0] == "--demo":
        return demo()
    cmd, url = argv[0], (argv[1] if len(argv) > 1 else "")
    if not url:
        print("falta la URL", file=sys.stderr)
        return 2
    bot = Robot()
    if cmd == "get":
        print(parse_title(bot.get(url)) or "(sin título)")
    elif cmd == "form":
        for i, fm in enumerate(parse_forms(bot.get(url))):
            print(f"[{i}] {fm['method'].upper()} {fm['action']} -> {list(fm['fields'])}")
    elif cmd == "table":
        for row in parse_table(bot.get(url)):
            print(" | ".join(row))
    else:
        print(f"comando desconocido: {cmd}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
