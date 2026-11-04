#!/usr/bin/env python3
"""Genera guias/<palabra>/index.html desde los .md de las guías prometidas en los reels (Comenta PALABRA).
  python3 guias/generar.py <carpeta-con-RED.md-REVISA.md-AGENTES.md>
Solo entiende lo que usan esas guías: #, ##, tablas, - [ ], listas con «Campo:», 1., **negrita** y [enlaces](url)."""
import html, os, re, sys

SRC = sys.argv[1]
OUT = os.path.dirname(os.path.abspath(__file__))
GUIAS = ["RED", "REVISA", "AGENTES"]

CSS = """
:root{--ink:#0A0E14;--ink2:#111723;--line:#232c3b;--text:#EAF0F8;--muted:#9AA6B8;--sig:#FFD400;--cob:#4D7CFE}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ink);color:var(--text);font:400 17px/1.6 'Geist','Inter',system-ui,sans-serif}
main{max-width:720px;margin:0 auto;padding:28px 20px 64px}
.top{display:flex;align-items:center;gap:10px;font:500 13px/1 'Geist Mono','JetBrains Mono',monospace;color:var(--muted);margin-bottom:28px}
.top a{color:var(--muted);text-decoration:none}
.palabra{display:inline-block;background:var(--sig);color:var(--ink);font:700 13px/1 'Geist Mono','JetBrains Mono',monospace;padding:6px 9px;border-radius:6px;letter-spacing:.04em}
h1{font-size:clamp(28px,7vw,40px);line-height:1.12;letter-spacing:-.02em;margin:14px 0 6px;font-weight:700;text-wrap:balance}
.meta{color:var(--muted);font-size:14px;margin:0 0 26px}
h2{font-size:20px;margin:34px 0 10px;font-weight:650}
p{margin:0 0 14px}
a{color:var(--cob)}
ul,ol{padding-left:22px;margin:0 0 16px}
li{margin:6px 0}
ul.check,ul.campos{list-style:none;padding:0}
ul.check li{display:flex;gap:12px;align-items:flex-start;padding:12px 14px;background:var(--ink2);border:1px solid var(--line);border-radius:10px;margin:8px 0}
ul.check input{appearance:none;flex:0 0 22px;height:22px;margin:1px 0 0;border:2px solid var(--muted);border-radius:6px;cursor:pointer;transition:background .15s,border-color .15s}
ul.check input:checked{background:var(--sig);border-color:var(--sig);box-shadow:inset 0 0 0 3px var(--ink2)}
ul.check label{cursor:pointer}
ul.campos li{padding:12px 0 14px;border-bottom:1px solid var(--line);margin:0}
ul.campos span{display:block;color:var(--muted);font-size:14px;margin-bottom:6px}
ul.campos input{width:100%;background:transparent;border:0;color:var(--text);font:inherit;padding:2px 0;outline:none}
ul.campos input:focus{box-shadow:0 2px 0 var(--sig)}
.tabla{overflow-x:auto;margin:0 0 18px;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:560px;font-size:14px}
th{background:var(--ink2);color:var(--muted);text-align:left;font-weight:600;padding:10px 12px}
td{border-top:1px solid var(--line);padding:0}
td input{width:100%;background:transparent;border:0;color:var(--text);font:inherit;padding:12px;outline:none}
.acciones{display:flex;gap:10px;flex-wrap:wrap;margin:30px 0 0}
button{font:600 15px/1 'Geist',system-ui,sans-serif;padding:13px 18px;border-radius:10px;border:0;background:var(--sig);color:var(--ink);cursor:pointer;transition:transform .12s ease-out}
button:active{transform:scale(.97)}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
footer a{color:var(--text)}
@media print{
 :root{--ink:#fff;--ink2:#fff;--line:#bbb;--text:#111;--muted:#555;--cob:#1a3fb0}
 body{font-size:12pt}.acciones,.top a{display:none}
 ul.check li{break-inside:avoid}ul.check input{border-color:#333}
 .palabra{border:1px solid #111;background:#fff;color:#111}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener" target="_blank">\1</a>', t)


def convertir(md):
    lineas = md.strip().split("\n")
    titulo = lineas[0].lstrip("# ").strip()
    meta = lineas[1].strip() if len(lineas) > 1 and not lineas[1].startswith("#") else ""
    cuerpo, i, n = [], 2 if meta else 1, 0
    while i < len(lineas):
        l = lineas[i].rstrip()
        if not l:
            i += 1; continue
        if l.startswith("## "):
            cuerpo.append(f"<h2>{inline(l[3:])}</h2>"); i += 1; continue
        if l.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                if not re.match(r"^\|[\s\-|]+\|$", lineas[i]):
                    filas.append([c.strip() for c in lineas[i].strip("|").split("|")])
                i += 1
            cab = "".join(f"<th>{inline(c)}</th>" for c in filas[0])
            vacia = "<tr>" + "<td><input aria-label='celda'></td>" * len(filas[0]) + "</tr>"
            cuerpo.append(f"<div class='tabla'><table><thead><tr>{cab}</tr></thead><tbody>{vacia * 6}</tbody></table></div>")
            continue
        if l.startswith("- [ ] "):
            items = []
            while i < len(lineas) and lineas[i].startswith("- [ ] "):
                n += 1
                items.append(f"<li><input type='checkbox' id='c{n}'><label for='c{n}'>{inline(lineas[i][6:])}</label></li>")
                i += 1
            cuerpo.append("<ul class='check'>" + "".join(items) + "</ul>"); continue
        if l.startswith("- "):
            items, campos = [], True
            while i < len(lineas) and lineas[i].startswith("- "):
                t = lineas[i][2:].strip()
                if t.endswith(":"):
                    n += 1
                    items.append(f"<li><label for='f{n}'><span>{inline(t[:-1])}</span></label><input id='f{n}'></li>")
                else:
                    campos = False
                    items.append(f"<li>{inline(t)}</li>")
                i += 1
            cuerpo.append(f"<ul class='{'campos' if campos else ''}'>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\d+\. ", l):
            items = []
            while i < len(lineas) and re.match(r"^\d+\. ", lineas[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\. ', '', lineas[i]))}</li>"); i += 1
            cuerpo.append("<ol>" + "".join(items) + "</ol>"); continue
        cuerpo.append(f"<p>{inline(l)}</p>"); i += 1
    return titulo, meta, "\n".join(cuerpo)


def pagina(palabra, titulo, meta, cuerpo):
    nombre = titulo.split("·", 1)[-1].strip()
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(nombre)} · Stiwall Labs</title>
<meta name="description" content="Guía gratuita de Stiwall Labs: {html.escape(nombre)}.">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700&family=Geist+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><main>
<div class="top"><a href="/">stiwall.dev</a><span>/</span><span>guías</span></div>
<span class="palabra">{palabra}</span>
<h1>{html.escape(nombre)}</h1>
<p class="meta">{inline(meta)}</p>
{cuerpo}
<div class="acciones"><button onclick="print()">Imprimir o guardar en PDF</button></div>
<footer>Lo que escribas aquí no se envía a ningún sitio ni se guarda al cerrar. Para conservarlo, guárdalo en PDF.<br>Más cada semana en <a href="https://instagram.com/stiwall" rel="noopener" target="_blank">@stiwall</a>.</footer>
</main></body></html>
"""


for g in GUIAS:
    titulo, meta, cuerpo = convertir(open(os.path.join(SRC, f"{g}.md"), encoding="utf-8").read())
    d = os.path.join(OUT, g.lower())
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina(g, titulo, meta, cuerpo))
    print("ok", g.lower())
