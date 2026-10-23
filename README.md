# curia_normativas

Repositorio público de la normativa chilena que usa la plataforma cívica Curia Máxima. El código de la plataforma está en [nlecarosg/curia_maxima](https://github.com/nlecarosg/curia_maxima) y las propuestas en [nlecarosg/curia_propuestas](https://github.com/nlecarosg/curia_propuestas). Esas piezas enlazan normas de este repositorio. Aquí no está la aplicación.

El propósito es guardar, en archivos revisables, el texto y los datos mínimos de cada norma que haga falta citar. Una norma derogada no se borra: queda marcada `derogada`, con la norma que la derogó.

## Niveles

Hay tres niveles. Cada uno tiene su carpeta.

1. Constitución y leyes del Congreso: `normas/constitucion/` y `normas/congreso/`.
2. Decretos y resoluciones ministeriales: `normas/ministerios/<organismo>/`.
3. Ordenanzas municipales: `normas/municipalidades/<comuna>/`.

## Estructura de carpetas

Cada archivo es una versión de una norma. La carpeta de la norma se llama igual que su `id`.

```text
normas/
  constitucion/<id>/<AAAA-MM-DD>.json
  congreso/<id>/<AAAA-MM-DD>.json
  ministerios/<organismo>/<id>/<AAAA-MM-DD>.json
  municipalidades/<comuna>/<id>/<AAAA-MM-DD>.json
```

El nombre `<AAAA-MM-DD>` es la fecha de esa versión del texto.

En una ley, el campo `organismo` conserva el ministerio que registra Ley Chile, que es el que la promulga. La carpeta `congreso/` indica el nivel: es ley del Congreso.

Todavía no hay archivo de la Constitución. El texto completo es largo y los ejemplos de partida son normas cortas. La carpeta queda definida para cuando se cargue una versión. Tampoco hay todavía un decreto o una resolución de ejemplo: la regla de carpeta ministerial está descrita aquí y la cubre una prueba de ruta con un archivo sintético que no se publica entre las normas.

### Ejemplos cargados a mano

Copiados el 23 de octubre de 2026 desde la versión pública que muestra Ley Chile. No incluyen el resumen ni las notas de la Biblioteca del Congreso Nacional.

| Id | Estado | Fuente |
| --- | --- | --- |
| `ley-21206` | derogada por `ley-21477` | https://www.bcn.cl/leychile/navegar?idNorma=1141619&idVersion=2020-01-27 |
| `ley-21695` | vigente | https://www.bcn.cl/leychile/navegar?idNorma=1207313&idVersion=2024-10-10 |
| `providencia-ordenanza-6-1998` | derogada, según la marca de Ley Chile, por `providencia-ordenanza-6-2003` | https://www.bcn.cl/leychile/navegar?idNorma=120358&idVersion=1998-06-22 |

La ley 21.695 está vigente. Sus disposiciones transitorias fijan plazos de dos y cuatro años para la comercialización y de ciento ochenta días para el reglamento. Eso no cambia el estado de la ley.

La derogación expresa es la de la ley 21.206. El artículo tercero de la ley 21.477, publicada el 10 de agosto de 2022, dice: «Derógase la ley N° 21.206, que prorrogó por cinco años, a contar del 31 de enero de 2020, el procedimiento simplificado de regularización de loteos a que se refiere el artículo 1 de la ley N° 20.234». Fuente de la ley derogatoria: https://www.bcn.cl/leychile/navegar?idNorma=1179864&idVersion=2022-08-10. Esa ley no está copiada aquí; el enlace identifica `derogada_por`.

La ordenanza 6 de Providencia, de 1998, figura en el registro de Ley Chile como derogada el 2 de octubre de 2003. Ese día se publicó la ordenanza 6 de 2003 de la misma municipalidad (idNorma 215324): https://www.bcn.cl/leychile/navegar?idNorma=215324&idVersion=2003-10-02. Esa ordenanza cita la de 1998, dice que hace falta modificarla y aprueba un texto nuevo. En el texto de 2003 consultado no aparece el verbo «derogar». El estado `derogada` sigue la marca de Ley Chile (`derogado="derogado"`, `FechaDerogacion` 2003-10-02), no una cláusula expresa leída en la norma nueva. La ordenanza de 2003 no está copiada en este repositorio.

En el numeral final de la ordenanza de 1998, el XML público de Ley Chile traía el carácter de reemplazo Unicode U+FFFD en lugar de la o de «Notificaciones» y de «Resoluciones». El texto guardado sigue la página renderizada de Ley Chile, que escribe esas dos palabras completas. El resto del texto es el que entregó esa versión.

## Versiones y derogaciones

`version` es la fecha de esa versión del texto, la misma que Ley Chile llama `fechaVersion`. `fecha_publicacion` es la publicación original en el Diario Oficial. En el texto original las dos fechas coinciden. Si la norma se modifica, la versión nueva es otro archivo, con la fecha en que empieza ese texto. El archivo anterior permanece.

- `vigente`: esa versión es la que rige.
- `modificada`: esa versión fue sustituida por una posterior y la norma sigue existiendo. `derogada_por` queda en null.
- `derogada`: la norma fue dejada sin efecto. No se elimina. `derogada_por` es el `id` de la norma derogatoria.

No se abre un archivo vacío en la fecha de derogación. Se marca la versión cuyo texto se conserva.

El `id` de una norma nacional es el tipo y el número, sin puntos: `ley-21206`. En una ordenanza el número se repite en cada comuna, así que el `id` lleva comuna, tipo, número y año: `providencia-ordenanza-6-1998`. `derogada_por` usa el mismo criterio. No se exige que el archivo de la norma derogatoria ya esté en el repositorio.

## Esquema

El esquema de una norma (F2-11) está en [`esquema/norma.schema.json`](esquema/norma.schema.json). Las claves van sin tilde para que el archivo sea fácil de validar.

| Clave | Contenido |
| --- | --- |
| `tipo` | `constitucion`, `ley`, `decreto`, `decreto_exento`, `resolucion`, `resolucion_exenta` u `ordenanza` |
| `numero` | Número como lo registra Ley Chile, sin separador de miles. Ejemplo: `21206` |
| `organismo` | Organismo que Ley Chile asocia a la norma |
| `fecha_publicacion` | Fecha de publicación original, `AAAA-MM-DD` |
| `estado` | `vigente`, `derogada` o `modificada` |
| `derogada_por` | Id de la norma derogatoria, o null |
| `fuente` | URL https de esa versión en `bcn.cl` o `leychile.cl` |
| `version` | Fecha de la versión del texto, `AAAA-MM-DD` |
| `hash` | SHA-256 del campo `texto` |

También hacen falta `id`, `titulo` y `texto`. El id enlaza las derogaciones, el título identifica la norma y el texto es lo que cubre el hash. Sin esos tres el archivo no se puede comprobar.

`hash` es `sha256:` seguido de 64 hexadecimales en minúsculas. Se calcula sobre los bytes UTF-8 exactos de `texto`, sin otra normalización. Identifica el texto guardado en este repositorio. No certifica una copia byte a byte del PDF del Diario Oficial.

## De dónde vienen los datos

Los tres ejemplos se copiaron a mano. No hay programa de ingesta en este repositorio y no hay clave de la API.

La ingesta futura usará la API de Ley Chile, de la Biblioteca del Congreso Nacional. La clave no se guarda aquí. Las condiciones de uso, consultadas el 23 de octubre de 2026 en https://www.bcn.cl/leychile/api/condiciones-de-uso, fijan en la sección 6.a un límite estándar de 500 solicitudes por cada 24 horas, salvo que la documentación oficial indique otra cosa. La caché de lo consultado será este repositorio, con una versión por fecha de publicación de esa versión del texto.

La sección 3.e, numerales vi y vii, prohíbe la extracción masiva para replicar Ley Chile o para armar una base equivalente sin autorización expresa de la Biblioteca. No está verificado si un acervo creciente, el día que exista la clave, caería en esa prohibición. Este cambio no llama a la API. Tampoco está verificado el trámite para obtener la clave: todavía no la tenemos.

La misma página pide no presentar resultados obtenidos desde la API como interpretación oficial de la Biblioteca. Este repositorio guarda textos y datos de identificación. No interpreta.

El Diario Oficial es la publicación oficial. La URL que pide el esquema, y la que guardamos, es la de Ley Chile.

## Textos oficiales y licencia

### Qué dice el artículo 11 de la Ley 17.336

Se consultó el texto vigente en Ley Chile (idNorma 28933, https://www.bcn.cl/leychile/navegar?idNorma=28933) y el texto original publicado el 2 de octubre de 1970. En los dos, el artículo 11 no habla de textos oficiales de leyes, decretos, reglamentos ni sentencias. Dice que pertenecen al patrimonio cultural común:

- las obras cuyo plazo de protección se extinguió;
- la obra de autor desconocido, incluidas las expresiones del acervo folklórico;
- las obras cuyos titulares renunciaron a la protección de esa ley;
- las obras de autores extranjeros que no estén protegidas según el artículo 2;
- las obras expropiadas por el Estado, salvo que la ley señale un beneficiario.

El inciso final vigente, ajustado por la ley 19.166, permite usar esas obras si se respeta la paternidad y la integridad. En el texto original de 1970 ese inciso remitía al reglamento el pago por usarlas.

Leer en el artículo 11 una exclusión de los textos oficiales no coincide con el texto de la ley. Una exclusión de ese tipo está, por ejemplo, en el artículo 13 del texto refundido español de propiedad intelectual. No está en el artículo 11 chileno.

### Qué afirma la Biblioteca, y qué quedó sin confirmar

La sección 9.d de las condiciones de uso de la API, consultada el mismo día, afirma que los textos legales, reglamentarios, administrativos o judiciales difundidos por Ley Chile están fuera del derecho de autor, «conforme al principio reconocido en la legislación nacional y en los estándares internacionales», y que la Biblioteca no tiene derechos de autor sobre esos textos. Agrega que las licencias Creative Commons de la Biblioteca alcanzan a metadatos, esquemas, descriptores, compilaciones y demás contenidos complementarios, y que debe citarse «Ley Chile – Biblioteca del Congreso Nacional».

Eso es la posición publicada por la Biblioteca. No cita el artículo 11. No es una sentencia ni un dictamen pedido para este repositorio.

Quedó sin verificar:

- Que la ley chilena excluya del derecho de autor los textos oficiales. No aparece en el artículo 11. El artículo 1 protege las obras literarias, artísticas y científicas. El artículo 71 S permite, sin autorización ni pago, reproducir o comunicar una obra para actuaciones judiciales, administrativas y legislativas. Es una excepción acotada a esas actuaciones, no una licencia para publicar el conjunto de las normas.
- El artículo 88 entrega al Estado, a los municipios y a otras personas jurídicas estatales el derecho de autor sobre las obras que sus funcionarios producen en el cargo, y permite liberarlas al patrimonio cultural común. No está resuelto aquí el límite entre esa regla y el texto de una ley, un decreto o una ordenanza.
- Si la frase de la Biblioteca autoriza a copiar, alojar y redistribuir los textos. Aquí se cita. No se convierte en conclusión jurídica.
- La eficacia de CC0 en Chile, sobre todo respecto de los derechos morales. El artículo 16 los declara inalienables y nulo cualquier pacto en contrario. CC0 intenta una renuncia que incluye derechos morales. La letra c) del artículo 11 habla de la renuncia del titular a la protección de la ley, y no está verificado qué forma exige esa renuncia en Chile.
- La relación entre la sección 9.a y la sección 9.d de las condiciones. La 9.a dice que, salvo indicación en contrario, los contenidos de Ley Chile están bajo Creative Commons Atribución-NoComercial-SinDerivadas 4.0. La 9.d limita esa licencia a metadatos y contenidos complementarios elaborados por la Biblioteca. Si esas dos frases se leen en tensión, este repositorio no resuelve cuál prevalece.

No se copian resúmenes, notas ni marcas de la Biblioteca. El campo `texto` es el de la norma.

### Licencia que se propone

Se propone CC0 1.0 Universal, en el archivo [`LICENSE`](LICENSE) y en https://creativecommons.org/publicdomain/zero/1.0/legalcode, para lo que produce este repositorio: el esquema, la estructura de carpetas, los identificadores, las pruebas, el validador y el texto original de esta documentación.

Un abogado tiene que confirmar esa propuesta antes de tratarla como una renuncia eficaz. Hasta entonces es una intención de dedicación al dominio público, no un dictamen.

CC0 no se usa para decir que este repositorio es autor de los textos oficiales ni para relicenciarlos. Quien reutilice una norma debe mirar la URL de `fuente` y las condiciones de la Biblioteca.

## Validación

En cada pull request, GitHub Actions solo valida el esquema. No hay ingesta ni despliegue. El flujo está en [`.github/workflows/validar-esquema.yml`](.github/workflows/validar-esquema.yml) y ejecuta, con la biblioteca estándar de Python:

```bash
python3 herramientas/validar_normas.py normas
python3 -m unittest tests.test_esquema -v
```

`tests/fixtures/norma-invalida.json` no es una norma: le faltan datos, la fecha no existe, dice estar derogada sin `derogada_por` y su URL no es de Ley Chile. El validador lo rechaza y el comando termina con un código distinto de cero. La prueba `test_fixture_invalida_falla` comprueba ese rechazo. La suite puede quedar en verde y, al mismo tiempo, un archivo inválido falla.

## Qué no hace este cambio

No implementa la ingesta desde la API, no guarda una clave, no despliega nada y no interpreta las normas. Los ejemplos son tres y están copiados a mano.
