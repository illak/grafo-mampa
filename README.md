# MAMPA — Jardín Digital de Contenidos

Visualización interactiva de fichas del repositorio MAMPA (Ministerio de Educación de la Provincia de Córdoba) como grafo multipartito. Desarrollado con D3.js v7.

## Estructura del proyecto

```
grafo_mampa/
├── mampa_jardin.html          # Visualización principal (D3.js)
├── data/
│   ├── export-Omeka-Mampa-ITEMS.xlsx   # Export de Omeka S (fuente de datos)
│   └── graph.json             # Grafo generado por el script Python
└── scripts/
    └── omeka_to_graph.py      # Transforma el XLSX en graph.json
```

## Requisitos

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (gestor de entornos Python)

## Actualizar los datos

Cada vez que se actualiza el repositorio en Omeka S:

**1.** Exportar los ítems desde Omeka S como `.xlsx` y reemplazar el archivo en `data/`.

**2.** Regenerar el grafo:

```bash
uv run --with pandas --with openpyxl scripts/omeka_to_graph.py
```

Esto genera `data/graph.json` con todos los nodos y aristas.

**3.** Pushear `data/graph.json` al repositorio. El HTML embebido en WordPress levanta los datos automáticamente desde:

```javascript
// mampa_jardin.html — línea ~297
const DATA_URL = 'https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/data/graph.json';
```

> Actualizá `TU_USUARIO/TU_REPO` con los valores reales del repositorio.

## Pruebas locales

El HTML hace `fetch()` para cargar los datos, por lo que necesita un servidor HTTP (no funciona abriendo el archivo directamente con doble click).

**1.** Generar `data/graph.json` (ver paso anterior).

**2.** Levantar el servidor desde la raíz del proyecto:

```bash
python3 -m http.server 8181
```

**3.** Abrir en el navegador:

```
http://localhost:8181/mampa_jardin.html
```

**4.** Para bajar el servidor, obtener el PID y terminarlo:

```bash
kill $(lsof -ti:8181)
```

## Despliegue en WordPress

El grafo se embebe en una página WordPress mediante un iframe. En un bloque HTML personalizado:

```html
<iframe
  src="https://tu-sitio.com/ruta/a/mampa_jardin.html"
  width="100%"
  height="800px"
  frameborder="0"
  style="border:none;">
</iframe>
```

El HTML puede estar alojado en cualquier servidor web accesible. Los datos se cargan desde GitHub directamente via `DATA_URL`.
