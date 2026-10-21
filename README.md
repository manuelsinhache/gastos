# Cuaderno de Gastos

Registro de gastos personal con gráficos mensuales por categoría, resumen semanal y filtro por fechas. Funciona en el navegador, sin cuenta: cada persona guarda sus gastos en su propio dispositivo.

- **Cuaderno:** https://manuelsinhache.github.io/gastos/
- **Guía para iPhone y Atajos:** https://manuelsinhache.github.io/gastos/guia/

## Añadir gastos desde un enlace

`https://manuelsinhache.github.io/gastos/#nuevo-IMPORTE-CATEGORIA-CONCEPTO` abre el formulario rellenado. Usa punto decimal y `_` en lugar de espacios. Por ejemplo: `#nuevo-12.50-comida-Cafe_con_leche`.

Categorías: `comida`, `transporte`, `entretenimiento`, `suscripciones`, `hogar`, `salud`, `compras`, `educacion`, `otros`.

## Herramientas

Los archivos publicados se generan a partir de las versiones originales en `herramientas/`:

```
python3 herramientas/build.py herramientas/cuaderno-gastos-claude.html   # → index.html (necesita Pillow)
python3 herramientas/build_guia.py herramientas/guia-claude.html         # → guia/index.html
python3 herramientas/crear_atajo.py                                      # → atajo sin firmar (se firma en macOS)
```
