#!/usr/bin/env python3
"""Valida archivos de norma contra el esquema de curia_normativas.

No descarga normas ni llama a la API de Ley Chile. Solo revisa JSON local.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

CAMPOS = (
    "id",
    "tipo",
    "numero",
    "titulo",
    "organismo",
    "fecha_publicacion",
    "estado",
    "derogada_por",
    "fuente",
    "version",
    "texto",
    "hash",
)

TIPOS = (
    "constitucion",
    "ley",
    "decreto",
    "decreto_exento",
    "resolucion",
    "resolucion_exenta",
    "ordenanza",
)

ESTADOS = ("vigente", "derogada", "modificada")

NIVEL_TIPOS = {
    "constitucion": frozenset({"constitucion"}),
    "congreso": frozenset({"ley"}),
    "ministerios": frozenset(
        {"decreto", "decreto_exento", "resolucion", "resolucion_exenta"}
    ),
    "municipalidades": frozenset({"ordenanza"}),
}

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HASH_PATRON = r"^sha256:[0-9a-f]{64}$"
HASH_RE = re.compile(HASH_PATRON)
FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HOSTS_FUENTE = frozenset(
    {"bcn.cl", "www.bcn.cl", "leychile.cl", "www.leychile.cl"}
)


def hash_texto(texto: str) -> str:
    digest = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _fecha(valor: object, campo: str, errores: list[str]) -> None:
    if not isinstance(valor, str) or FECHA_RE.match(valor) is None:
        errores.append(f"{campo} debe ser una fecha AAAA-MM-DD")
        return
    try:
        date.fromisoformat(valor)
    except ValueError:
        errores.append(f"{campo} no es una fecha de calendario")


def validar_objeto(data: object) -> list[str]:
    errores: list[str] = []
    if not isinstance(data, dict):
        return ["la norma debe ser un objeto JSON"]

    faltan = [campo for campo in CAMPOS if campo not in data]
    if faltan:
        errores.append("faltan campos: " + ", ".join(faltan))
    sobran = sorted(campo for campo in data if campo not in CAMPOS)
    if sobran:
        errores.append("campos no permitidos: " + ", ".join(sobran))

    identificador = data.get("id")
    if "id" in data and (not isinstance(identificador, str) or SLUG.match(identificador) is None):
        errores.append("id debe ser un slug en minúsculas (ej. ley-21206)")

    tipo = data.get("tipo")
    if "tipo" in data and tipo not in TIPOS:
        errores.append("tipo debe ser uno de: " + ", ".join(TIPOS))

    for campo in ("numero", "titulo", "organismo", "texto"):
        valor = data.get(campo)
        if campo in data and (not isinstance(valor, str) or not valor.strip()):
            errores.append(f"{campo} debe ser un texto no vacío")

    if "fecha_publicacion" in data:
        _fecha(data.get("fecha_publicacion"), "fecha_publicacion", errores)
    if "version" in data:
        _fecha(data.get("version"), "version", errores)

    estado = data.get("estado")
    if "estado" in data and estado not in ESTADOS:
        errores.append("estado debe ser vigente, derogada o modificada")

    derogada_por = data.get("derogada_por")
    if "derogada_por" in data and "estado" in data and estado in ESTADOS:
        if estado == "derogada":
            if not isinstance(derogada_por, str) or SLUG.match(derogada_por) is None:
                errores.append(
                    "derogada_por debe identificar la norma derogatoria cuando estado es derogada"
                )
        elif derogada_por is not None:
            errores.append("derogada_por debe ser null cuando la norma no está derogada")

    fuente = data.get("fuente")
    if "fuente" in data:
        if not isinstance(fuente, str):
            errores.append("fuente debe ser una URL https de bcn.cl o leychile.cl")
        else:
            partes = urlparse(fuente)
            if partes.scheme != "https" or partes.hostname not in HOSTS_FUENTE:
                errores.append("fuente debe ser una URL https de bcn.cl o leychile.cl")

    texto = data.get("texto")
    huella = data.get("hash")
    if "hash" in data and (not isinstance(huella, str) or HASH_RE.match(huella) is None):
        errores.append("hash debe ser sha256: seguido de 64 hexadecimales en minúsculas")
    elif isinstance(texto, str) and isinstance(huella, str) and HASH_RE.match(huella):
        esperado = hash_texto(texto)
        if huella != esperado:
            errores.append("hash no corresponde al texto UTF-8 almacenado")

    return errores


def _raiz_normas(path: Path) -> Path | None:
    candidatos = [path, *path.parents] if path.is_dir() else list(path.parents)
    for candidato in candidatos:
        if candidato.name == "normas" and candidato.is_dir():
            return candidato
    return None


def validar_ruta(path: Path, data: object) -> list[str]:
    raiz = _raiz_normas(path)
    if raiz is None or not isinstance(data, dict):
        return []

    errores: list[str] = []
    try:
        partes = path.resolve().relative_to(raiz.resolve()).parts
    except ValueError:
        return []

    nivel = partes[0] if partes else ""
    if nivel not in NIVEL_TIPOS:
        errores.append(
            "la carpeta de nivel debe ser constitucion, congreso, ministerios o municipalidades"
        )
        return errores

    if nivel in ("constitucion", "congreso"):
        if len(partes) != 3:
            errores.append(
                f"ruta esperada: normas/{nivel}/<id>/<version>.json"
            )
            return errores
        id_dir, archivo = partes[1], partes[2]
    else:
        if len(partes) != 4:
            errores.append(
                f"ruta esperada: normas/{nivel}/<organismo>/<id>/<version>.json"
            )
            return errores
        organismo_dir, id_dir, archivo = partes[1], partes[2], partes[3]
        if SLUG.match(organismo_dir) is None:
            errores.append("la carpeta de organismo o comuna debe ser un slug")

    if id_dir != data.get("id"):
        errores.append("la carpeta de la norma debe llamarse igual que id")
    version = data.get("version")
    if isinstance(version, str) and archivo != f"{version}.json":
        errores.append("el archivo debe llamarse <version>.json")
    tipo = data.get("tipo")
    if tipo in TIPOS and tipo not in NIVEL_TIPOS[nivel]:
        errores.append(f"el tipo {tipo} no corresponde al nivel {nivel}")
    return errores


def validar_archivo(path: Path) -> list[str]:
    try:
        contenido = path.read_text(encoding="utf-8")
        data = json.loads(contenido)
    except json.JSONDecodeError as exc:
        return [f"{path}: JSON inválido ({exc.msg})"]
    except OSError as exc:
        return [f"{path}: no se pudo leer ({exc.strerror})"]

    errores = [f"{path}: {mensaje}" for mensaje in validar_objeto(data)]
    errores.extend(f"{path}: {mensaje}" for mensaje in validar_ruta(path, data))
    return errores


def validar_entrada(entrada: Path) -> list[str]:
    if entrada.is_dir():
        archivos = sorted(entrada.rglob("*.json"))
        if not archivos:
            return [f"{entrada}: no hay archivos JSON"]
        errores: list[str] = []
        for archivo in archivos:
            errores.extend(validar_archivo(archivo))
        return errores
    if entrada.is_file():
        return validar_archivo(entrada)
    return [f"{entrada}: no existe"]


def main(argv: list[str]) -> int:
    entradas = [Path(argumento) for argumento in argv] or [Path("normas")]
    errores: list[str] = []
    for entrada in entradas:
        errores.extend(validar_entrada(entrada))
    if errores:
        for error in errores:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
