#!/usr/bin/env python3
"""Convierte la guía (versión Claude) en guia/index.html apuntando a GitHub Pages.

Uso: python3 herramientas/build_guia.py herramientas/guia-claude.html
"""
import sys
from pathlib import Path

BASE = "https://manuelsinhache.github.io/gastos/"
OLD = "https://claude.ai/artifact/CTUALRQUnos1nQUkc4uiVo"
s = Path(sys.argv[1]).read_text(encoding="utf-8")


def rep(old, new):
    global s
    if old not in s:
        sys.exit(f"No encontrado en la guía:\n{old[:120]}")
    s = s.replace(old, new)


rep(OLD + "#", BASE + "#")
rep(OLD, BASE)
rep("https://claude.ai/…#nuevo-", "…/gastos/#nuevo-")
rep("<span>claude.ai</span>", "<span>manuelsinhache.github.io</span>")
rep("🔒 claude.ai", "🔒 manuelsinhache.github.io")
rep("<p>Si te pide iniciar sesión, entra con una cuenta de Claude. Es gratuita.</p>",
    "<p>No necesitas cuenta ni contraseña: se abre directamente.</p>")
rep("<li>Si el enlace se abre a veces en Safari y a veces en la app de Claude, verás dos cuadernos distintos. Usa siempre la misma vía. Los atajos de esta guía abren Safari.</li>",
    "<li>Si lo abres a veces en Safari y a veces desde un icono creado con <span class=\"ui\">Añadir a pantalla de inicio</span> de Safari, verás dos cuadernos distintos, cada uno con sus datos. Usa siempre la misma vía. Los atajos de esta guía abren Safari.</li>")
rep("<p>Seguramente se abrió en la app de Claude en vez de en Safari, y la app no recibe la parte del enlace con el gasto. Puedes escribir el gasto a mano, o abrir el cuaderno en Safari y repetir el atajo. Recuerda que los gastos de la app y los de Safari se guardan por separado.</p>",
    "<p>Revisa la acción <span class=\"ui\">Abrir URL</span>: debe terminar en <code>#nuevo-</code> seguido de las tres variables separadas por guiones. Mientras lo arreglas, puedes escribir el gasto a mano.</p>")
rep("como la app de Claude, otro navegador o una pestaña privada.",
    "como otro navegador, el icono de la pantalla de inicio o una pestaña privada.")
rep("<p>Las pantallas del iPhone de esta guía son ilustraciones;",
    "<p><a href=\"../\">Abrir el Cuaderno de Gastos</a></p>\n    <p>Las pantallas del iPhone de esta guía son ilustraciones;")

# Documento completo (la versión Claude no lleva <head>)
rep('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
s = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
     '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + s)
s = s.replace("<style>\n", "<style>\n:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }\nbody { margin: 0; -webkit-text-size-adjust: 100%; }\n", 1)
s = s.replace('<div class="wrap">', '</head>\n<body>\n<div class="wrap">', 1)
s = s.rstrip() + "\n</body>\n</html>\n"
if "claude" in s.lower():
    sys.exit("Quedan referencias a Claude en la guía")

out = Path(__file__).resolve().parent.parent / "guia" / "index.html"
out.write_text(s, encoding="utf-8")
print("Creado", out)
