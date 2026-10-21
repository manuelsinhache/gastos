#!/usr/bin/env python3
"""Genera «Añadir gasto.shortcut» (sin firmar) para el Cuaderno de Gastos.

Uso:
    python3 crear_atajo.py
    shortcuts sign --mode anyone --input gasto-sin-firmar.shortcut --output "Añadir gasto.shortcut"

El segundo comando solo existe en macOS (12 o posterior). Después, envía el
archivo firmado al iPhone por AirDrop o iCloud Drive y ábrelo.
"""
import plistlib
import uuid

URL_BASE = "https://manuelsinhache.github.io/gastos/#nuevo-"
CATEGORIAS = ["Comida", "Transporte", "Entretenimiento", "Suscripciones",
              "Hogar", "Salud", "Compras", "Educacion", "Otros"]
SALIDA = "gasto-sin-firmar.shortcut"


def uid():
    return str(uuid.uuid4()).upper()


def salida(action_uuid, nombre):
    """Referencia a la salida de una acción anterior."""
    return {"OutputUUID": action_uuid, "Type": "ActionOutput", "OutputName": nombre}


def variable(action_uuid, nombre):
    return {"Value": salida(action_uuid, nombre), "WFSerializationType": "WFTextTokenAttachment"}


def texto_con_variables(partes):
    """partes: lista de str o (uuid, nombre). Devuelve un WFTextTokenString."""
    cadena, adjuntos = "", {}
    for p in partes:
        if isinstance(p, str):
            cadena += p
        else:
            # Los rangos se cuentan en unidades UTF-16; todo el texto aquí es ASCII.
            adjuntos[f"{{{len(cadena)}, 1}}"] = salida(*p)
            cadena += "￼"
    return {"Value": {"string": cadena, "attachmentsByRange": adjuntos},
            "WFSerializationType": "WFTextTokenString"}


def accion(ident, **params):
    params.setdefault("UUID", uid())
    return {"WFWorkflowActionIdentifier": ident, "WFWorkflowActionParameters": params}


# 1. Importe
pedir_importe = accion("is.workflow.actions.ask",
                       WFAskActionPrompt="¿Cuánto has gastado?",
                       WFInputType="Number")
# 2. Coma decimal → punto (el enlace no admite comas)
importe_punto = accion("is.workflow.actions.text.replace",
                       WFInput=texto_con_variables([(pedir_importe["WFWorkflowActionParameters"]["UUID"], "Provided Input")]),
                       WFReplaceTextFind=",",
                       WFReplaceTextReplace=".")
# 3. Categoría
lista = accion("is.workflow.actions.list", WFItems=CATEGORIAS)
elegir = accion("is.workflow.actions.choosefromlist",
                WFInput=variable(lista["WFWorkflowActionParameters"]["UUID"], "List"),
                WFChooseFromListActionPrompt="Categoría")
# 4. Concepto, con los espacios cambiados por «_»
pedir_concepto = accion("is.workflow.actions.ask",
                        WFAskActionPrompt="Concepto (sin tildes)",
                        WFInputType="Text",
                        WFAskActionDefaultAnswer="")
concepto_guiones = accion("is.workflow.actions.text.replace",
                          WFInput=texto_con_variables([(pedir_concepto["WFWorkflowActionParameters"]["UUID"], "Provided Input")]),
                          WFReplaceTextFind=" ",
                          WFReplaceTextReplace="_")
# 5. Construir y abrir el enlace
url = accion("is.workflow.actions.url",
             WFURLActionURL=texto_con_variables([
                 URL_BASE,
                 (importe_punto["WFWorkflowActionParameters"]["UUID"], "Updated Text"), "-",
                 (elegir["WFWorkflowActionParameters"]["UUID"], "Selected Item"), "-",
                 (concepto_guiones["WFWorkflowActionParameters"]["UUID"], "Updated Text"),
             ]))
abrir = accion("is.workflow.actions.openurl",
               WFInput=variable(url["WFWorkflowActionParameters"]["UUID"], "URL"))

atajo = {
    "WFWorkflowActions": [pedir_importe, importe_punto, lista, elegir,
                          pedir_concepto, concepto_guiones, url, abrir],
    "WFWorkflowClientVersion": "2302.0.4",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4292093695,  # verde
                       "WFWorkflowIconGlyphNumber": 59511},
    "WFWorkflowImportQuestions": [],
    "WFWorkflowTypes": [],
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowHasOutputFallback": False,
}

with open(SALIDA, "wb") as f:
    plistlib.dump(atajo, f, fmt=plistlib.FMT_BINARY)
print(f"Creado {SALIDA}. Fírmalo en un Mac con:")
print(f'  shortcuts sign --mode anyone --input {SALIDA} --output "Añadir gasto.shortcut"')
