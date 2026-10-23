"""Pruebas del esquema de norma.

La suite queda en verde cuando el validador rechaza lo inválido.
Un archivo inválido, pasado por la línea de comandos, termina con código distinto de cero.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))

import validar_normas  # noqa: E402

NORMAS = RAIZ / "normas"
ESQUEMA = RAIZ / "esquema" / "norma.schema.json"
FIXTURE_INVALIDA = RAIZ / "tests" / "fixtures" / "norma-invalida.json"
VALIDADOR = RAIZ / "herramientas" / "validar_normas.py"


def cargar(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class EsquemaNormaTest(unittest.TestCase):
    def test_ejemplos_cumplen_el_esquema(self) -> None:
        archivos = sorted(NORMAS.rglob("*.json"))
        self.assertGreaterEqual(len(archivos), 2)
        self.assertEqual(validar_normas.validar_entrada(NORMAS), [])
        for archivo in archivos:
            data = cargar(archivo)
            self.assertEqual(data["hash"], validar_normas.hash_texto(data["texto"]))
            self.assertIn(data["estado"], validar_normas.ESTADOS)

    def test_hay_una_norma_derogada_y_una_vigente(self) -> None:
        estados = {cargar(archivo)["estado"] for archivo in NORMAS.rglob("*.json")}
        self.assertIn("derogada", estados)
        self.assertIn("vigente", estados)

    def test_estado_modificada_acepta_derogada_por_nulo(self) -> None:
        data = cargar(next(NORMAS.rglob("*.json")))
        data = dict(data)
        data["estado"] = "modificada"
        data["derogada_por"] = None
        data["hash"] = validar_normas.hash_texto(data["texto"])
        self.assertEqual(validar_normas.validar_objeto(data), [])

    def test_hash_distinto_falla(self) -> None:
        data = cargar(next(NORMAS.rglob("*.json")))
        data = dict(data)
        data["hash"] = "sha256:" + "0" * 64
        errores = validar_normas.validar_objeto(data)
        self.assertTrue(any("hash no corresponde" in error for error in errores))

    def test_estado_desconocido_falla(self) -> None:
        data = cargar(next(NORMAS.rglob("*.json")))
        data = dict(data)
        data["estado"] = "revocada"
        data["derogada_por"] = None
        errores = validar_normas.validar_objeto(data)
        self.assertTrue(errores)

    def test_derogada_sin_referencia_falla(self) -> None:
        data = cargar(next(NORMAS.rglob("*.json")))
        data = dict(data)
        data["estado"] = "derogada"
        data["derogada_por"] = None
        errores = validar_normas.validar_objeto(data)
        self.assertTrue(any("derogada_por" in error for error in errores))

    def test_vigente_con_derogada_por_falla(self) -> None:
        data = cargar(next(NORMAS.rglob("*.json")))
        data = dict(data)
        data["estado"] = "vigente"
        data["derogada_por"] = "ley-1"
        errores = validar_normas.validar_objeto(data)
        self.assertTrue(any("derogada_por" in error for error in errores))

    def test_fixture_invalida_falla(self) -> None:
        errores = validar_normas.validar_archivo(FIXTURE_INVALIDA)
        self.assertTrue(errores)
        proceso = subprocess.run(
            [sys.executable, str(VALIDADOR), str(FIXTURE_INVALIDA)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proceso.returncode, 0)
        self.assertTrue(proceso.stderr.strip())

    def test_ruta_ministerial_y_ruta_cruzada(self) -> None:
        base = cargar(next((NORMAS / "congreso").rglob("*.json")))
        data = dict(base)
        data.update(
            {
                "id": "decreto-exento-1",
                "tipo": "decreto_exento",
                "numero": "1 EXENTO",
                "titulo": "Ejemplo sintético de ruta. No es una norma.",
                "organismo": "MINISTERIO DE PRUEBA",
                "fecha_publicacion": "2024-01-01",
                "estado": "vigente",
                "derogada_por": None,
                "fuente": "https://www.bcn.cl/leychile/navegar?idNorma=1&idVersion=2024-01-01",
                "version": "2024-01-01",
                "texto": "texto de prueba de ruta",
            }
        )
        data["hash"] = validar_normas.hash_texto(data["texto"])
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp) / "normas"
            archivo = (
                raiz
                / "ministerios"
                / "ministerio-de-prueba"
                / data["id"]
                / "2024-01-01.json"
            )
            archivo.parent.mkdir(parents=True)
            archivo.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(validar_normas.validar_archivo(archivo), [])

            cruzada = raiz / "congreso" / data["id"] / "2024-01-01.json"
            cruzada.parent.mkdir(parents=True)
            cruzada.write_text(json.dumps(data), encoding="utf-8")
            errores = validar_normas.validar_archivo(cruzada)
            self.assertTrue(any("no corresponde al nivel" in error for error in errores))

    def test_esquema_json_coincide_con_el_validador(self) -> None:
        esquema = cargar(ESQUEMA)
        self.assertEqual(esquema["required"], list(validar_normas.CAMPOS))
        self.assertEqual(esquema["properties"]["tipo"]["enum"], list(validar_normas.TIPOS))
        self.assertEqual(esquema["properties"]["estado"]["enum"], list(validar_normas.ESTADOS))
        self.assertEqual(esquema["properties"]["hash"]["pattern"], validar_normas.HASH_PATRON)
        self.assertIs(esquema["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main()
