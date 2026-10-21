#!/usr/bin/env python3
"""Convierte el Cuaderno de Gastos (versión Claude) en una página independiente: index.html.

Uso: python3 herramientas/build.py herramientas/cuaderno-gastos-claude.html
Guarda los datos solo en el navegador; no necesita cuenta ni inicio de sesión.
"""
import base64, io, sys
from pathlib import Path
from PIL import Image, ImageDraw

src = Path(sys.argv[1]).read_text(encoding="utf-8")
out_dir = Path(__file__).resolve().parent.parent


def must_replace(s, old, new):
    if old not in s:
        sys.exit(f"No encontrado en el original:\n{old[:120]}")
    return s.replace(old, new)


# Icono para la pantalla de inicio: franjas con los colores de las categorías
img = Image.new("RGB", (180, 180), "#3b3ad6")
d = ImageDraw.Draw(img)
for i, c in enumerate(["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]):
    h = [96, 70, 112, 58, 84][i]
    d.rounded_rectangle([22 + i * 28, 150 - h, 22 + i * 28 + 20, 150], radius=5, fill=c)
buf = io.BytesIO(); img.save(buf, "PNG")
icon = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

s = src
# La versión de Claude no lleva <head>; aquí escribimos el documento completo.
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
head = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Gastos">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#f3f5f9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1015" media="(prefers-color-scheme: dark)">
<link rel="apple-touch-icon" href="{icon}">
<link rel="icon" href="{icon}">
"""
s = head + s
s = s.replace("<style>\n", "<style>\n:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }\nbody { margin: 0; -webkit-text-size-adjust: 100%; }\n", 1)
s = s.replace('<div class="wrap">', '</head>\n<body>\n<div class="wrap">', 1)
s = s.rstrip() + "\n</body>\n</html>\n"

# Sin cuenta: todo se guarda en el navegador desde el principio.
s = must_replace(s, '<span class="pill" id="storage-pill" data-state="cargando">Conectando…</span>',
                 '<span class="pill" id="storage-pill" data-state="local">Guardado en este navegador</span>')
s = must_replace(s, '    mode: "cargando",    // cargando | cuenta | local', '    mode: "local",       // solo navegador en la versión independiente')
s = must_replace(s, "  connect();\n", "  try { navigator.storage && navigator.storage.persist && navigator.storage.persist(); } catch {}\n")
s = must_replace(s, '  setTimeout(() => { if (state.mode === "cargando") { state.mode = "local"; render(); } }, 11000);\n', "")
s = must_replace(s, '"Tus gastos se guardan solo en este navegador. Para llevarlos a otro dispositivo, exporta el CSV e impórtalo allí. Si abres el cuaderno con sesión iniciada y permiso de edición, se guardarán en tu cuenta."',
                 '"Tus gastos se guardan solo en este navegador y nadie más puede verlos. Para llevarlos a otro dispositivo o tener una copia, exporta el CSV e impórtalo allí."')

# Exportar: descarga directa del archivo en vez de la capacidad de Claude.
s = must_replace(s, """      const dl = await claude_use("downloads");
      if (dl) {
        try { await dl.save({ filename: `gastos-${iso(today())}.csv`, data: "\ufeff" + csv }); return; }
        catch (e) { if (e && e.code === "declined") return; }
      }
""", """      try {
        const url = URL.createObjectURL(new Blob(["\\ufeff" + csv], { type: "text/csv;charset=utf-8" }));
        const a = document.createElement("a"); a.href = url; a.download = `gastos-${iso(today())}.csv`;
        document.body.append(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 4000);
        return;
      } catch {}
""")

# Enlace a la guía publicada junto al cuaderno.
s = must_replace(s, '<p id="foot-storage"></p>', '<p id="foot-storage"></p>\n    <p><a href="guia/" style="color:var(--accent);font-weight:600">Guía paso a paso: abrir el cuaderno y crear los atajos del iPhone</a></p>')

# El ejemplo del atajo usa la dirección donde esté publicada la página.
s = must_replace(s, "  readHash();\n", "  $(\"#ios-example\").textContent = location.href.split(\"#\")[0] + \"#nuevo-12.50-comida-Cafe_con_leche\";\n  readHash();\n")

s = s.replace("https://claude.ai/artifact/CTUALRQUnos1nQUkc4uiVo#", "https://manuelsinhache.github.io/gastos/#")

(out_dir / "index.html").write_text(s, encoding="utf-8")
print("Creado", out_dir / "index.html", f"({len(s)//1024} KB)")
