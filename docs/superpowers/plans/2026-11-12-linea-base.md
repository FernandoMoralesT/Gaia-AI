# Línea base del entrenamiento (v1.1.0, paso 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Medir de forma repetible el ritmo del entrenamiento actual (tiempo por época, CPU, RAM y entorno) y dejarlo en `docs/linea_base.md` como punto de comparación para la v1.5.0.

**Architecture:** Un solo script, `scrips/medir_linea_base.py`. Reutiliza `pipeline_dataset_dem()` para los loaders y `paso_entrenamiento()` lote a lote, sin llamar a `entrenar()`, que escribe `salidas/historial.csv` y `salidas/checkpoints/ultimo.pt` en cada época. Un hilo con psutil muestrea CPU y RAM cada 0.5 s. El script arma el informe en Markdown y lo imprime o lo guarda con `--salida`.

**Tech Stack:** Python 3.13, PyTorch (CPU), psutil 7.2.2 (dependencia nueva), statistics, threading, argparse, pytest.

**Spec:** el mensaje del PASO 2 de la v1.1.0 (en la conversación), más `docs/ROADMAP_v2.md` § v1.1.0.

## Global Constraints

- No cambiar `src/model/entrenar.py`, `src/pipeline.py` ni los hiperparámetros.
- No escribir en `salidas/checkpoints/`, `modelos/` ni `salidas/historial.csv`: el script nunca llama a `entrenar()`, `guardar_muestras()` ni `guardar_checkpoint()`.
- Hiperparámetros idénticos al entrenamiento real: `batch_size=4` (288 muestras → 72 lotes por época), `nn.BCEWithLogitsLoss()`, Adam con `lr=2e-4` y `betas=(0.5, 0.999)` para G y D, `torch.manual_seed(42)` justo antes de crear G y D (igual que en `pipeline.py`).
- Valores por defecto: `--epocas 6` (1 de calentamiento y 5 medidas), `--repeticiones 3`, `--nota ""`.
- Tiempo con `time.perf_counter()`. Muestreo cada 0.5 s en un hilo aparte.
- Ningún número del informe se escribe a mano: todos salen de la corrida.
- Commits sin comillas internas. Sin push ni tags.

## Review Focus

1. `--epocas 1` (o menos) deja cero épocas medidas → debe terminar con un error claro de argparse y no producir un informe con estadísticas vacías.
2. Árbol de git con cambios sin commit → el hash del informe debe llevar `-dirty`, para que nadie crea que el número corresponde exactamente a ese commit.
3. Ejecutar el script desde otra carpeta → `cargar_etiquetas()` usa una ruta relativa; el script debe hacer `os.chdir(RAIZ)` y funcionar igual.
4. Un tramo medido de menos de 0.5 s (prueba con un loader falso) → el muestreador debe tomar al menos una muestra al detenerse, para no dividir entre cero.
5. `peak_wset` no existe fuera de Windows → el informe dice "no disponible" en lugar de fallar.

---

## Cómo está armado el entrenamiento hoy (contexto)

- **Loaders:** `pipeline_dataset_dem("data/raw", batch_size=4)` lee los 60 `.tif`, carga `data/etiquetas.json`, divide por tile (`dividir_tiles`, seed 42) y `procesar_tiles` reduce cada tile a 120×120, lo normaliza y genera 6 variantes. `DataLoader` de entrenamiento con `shuffle=True` y `num_workers=0` (todo en el proceso principal).
- **`paso_entrenamiento(g, d, mapas, ids, criterio, opt_g, opt_d)`:** un lote. Actualiza D con reales y falsos (`falso.detach()`), luego actualiza G. Devuelve `(perdida_d, perdida_g)`. No escribe nada.
- **`entrenar(...)`:** recorre las épocas llamando a `paso_entrenamiento` por lote. **Además**, en cada época sobrescribe `salidas/historial.csv` (lo abre con `"w"` al inicio, así que borraría el historial de la v1.0), guarda `salidas/checkpoints/ultimo.pt`, una imagen de muestras en la época 1 y cada 10, y un checkpoint numerado cada 50. **Por eso no se puede usar para medir.**
- **Consecuencia para el informe:** lo que se mide es el ciclo de lotes (carga del lote más `paso_entrenamiento`), sin el guardado por época. La época real de la v1.0 es un poco más lenta por ese guardado; el informe lo aclara.

## File Structure

- Create: `scrips/medir_linea_base.py`: medición, muestreo, datos del entorno e informe.
- Create: `test/test_medir_linea_base.py`: pruebas de las partes puras y una corrida corta con un loader falso.
- Modify: `requirements.txt`: agregar `psutil==7.2.2`.
- Create (con la corrida real): `docs/linea_base.md`.
- Modify (al cerrar): `docs/bitacora.md` y `CLAUDE.md` (pendiente de la línea base).

---

### Task 1: Estadísticas de tiempos y conversión de CPU (funciones puras)

**Files:**
- Create: `scrips/medir_linea_base.py`
- Create: `test/test_medir_linea_base.py`
- Modify: `requirements.txt` (agregar `psutil==7.2.2` en orden alfabético) e instalarlo con `pip install psutil==7.2.2`

**Interfaces:**
- Produces: `resumir_tiempos(tiempos: list[float]) -> dict` con claves `calentamiento`, `n`, `media`, `mediana`, `min`, `max` (el primero de la lista es el calentamiento; las estadísticas usan el resto).
- Produces: `cpu_a_maquina(pct_proceso: float, nucleos_logicos: int) -> float` (porcentaje de la máquina completa) y `cpu_a_nucleos(pct_proceso: float) -> float` (núcleos equivalentes = pct / 100).

- [ ] **Step 1: Escribir las pruebas que fallan**

El test agrega `scrips/` a `sys.path`, como `test_comparar_simplex.py`.

```python
def test_resumir_tiempos_separa_calentamiento():
    r = resumir_tiempos([9.0, 5.0, 4.0, 6.0, 5.0, 5.0])
    assert r["calentamiento"] == 9.0
    assert r["n"] == 5
    assert r["media"] == pytest.approx(5.0)
    assert r["mediana"] == 5.0
    assert (r["min"], r["max"]) == (4.0, 6.0)

def test_resumir_tiempos_exige_una_medida():
    with pytest.raises(ValueError):
        resumir_tiempos([9.0])

def test_cpu_maquina_y_nucleos():
    assert cpu_a_maquina(400.0, 16) == pytest.approx(25.0)
    assert cpu_a_nucleos(400.0) == pytest.approx(4.0)
```

- [ ] **Step 2: Correr y ver que fallan**

Run: `python -m pytest test/test_medir_linea_base.py -v`
Expected: FAIL (`ModuleNotFoundError: medir_linea_base`)

- [ ] **Step 3: Implementar las tres funciones** con `statistics.mean` y `statistics.median`.

- [ ] **Step 4: Correr y ver que pasan**

Run: `python -m pytest test/test_medir_linea_base.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scrips/medir_linea_base.py test/test_medir_linea_base.py requirements.txt
git commit -m "test: estadisticas de tiempos y conversion de CPU para la linea base"
```

### Task 2: Muestreador de recursos en un hilo

**Files:**
- Modify: `scrips/medir_linea_base.py`
- Modify: `test/test_medir_linea_base.py`

**Interfaces:**
- Produces: `class Muestreador(intervalo: float = 0.5)` con `iniciar() -> None` y `detener() -> dict`. Claves de `detener()`: `cpu_proceso` (media de `Process.cpu_percent()`, en "% de un núcleo"), `cpu_sistema` (media de `psutil.cpu_percent()`), `rss_max` (bytes), `muestras` (int).

- [ ] **Step 1: Escribir la prueba que falla**

```python
def test_muestreador_toma_al_menos_una_muestra():
    m = Muestreador(intervalo=0.5)
    m.iniciar()
    sum(i * i for i in range(200_000))  # menos de 0.5 s de trabajo
    r = m.detener()
    assert r["muestras"] >= 1
    assert r["rss_max"] > 0
    assert r["cpu_proceso"] >= 0 and 0 <= r["cpu_sistema"] <= 100
```

- [ ] **Step 2: Correr y ver que falla** (`NameError: Muestreador`)

- [ ] **Step 3: Implementar.** `iniciar()` llama una vez a `cpu_percent(None)` del proceso y del sistema para descartar la primera lectura (psutil devuelve 0.0 la primera vez) y arranca un `threading.Thread(daemon=True)` que repite `Event.wait(intervalo)` y toma una muestra. `detener()` activa el `Event`, hace `join()` y toma una última muestra (Review Focus 4).

- [ ] **Step 4: Correr y ver que pasa.** Run: `python -m pytest test/test_medir_linea_base.py -v`. Expected: 4 passed

- [ ] **Step 5: Commit** `feat: muestreador de CPU y RAM para la linea base`

### Task 3: Medir una repetición sin escribir en salidas/

**Files:**
- Modify: `scrips/medir_linea_base.py`
- Modify: `test/test_medir_linea_base.py`

**Interfaces:**
- Consumes: `Generador`, `Discriminador` y `paso_entrenamiento` de `src/` (agregar `src/` a `sys.path` como en `exportar_generador.py`); `Muestreador` (Task 2).
- Produces: `medir_repeticion(loader, epocas: int) -> tuple[list[float], dict]`: tiempos por época (incluido el calentamiento) y el resultado del `Muestreador`. Hace `torch.manual_seed(42)`, crea G, D, `BCEWithLogitsLoss` y los dos Adam con los valores de Global Constraints. Cada época mide con `perf_counter()` el ciclo `for mapas, ids in loader: paso_entrenamiento(...)`. El `Muestreador` arranca **después** de la época de calentamiento.

- [ ] **Step 1: Escribir la prueba que falla** (loader falso: 2 lotes de 4 mapas aleatorios de 1×120×120 con ids 0 a 5; corre en una carpeta temporal)

```python
def test_medir_repeticion_no_escribe_archivos(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tiempos, recursos = medir_repeticion(loader_falso(), epocas=2)
    assert len(tiempos) == 2 and all(t > 0 for t in tiempos)
    assert recursos["muestras"] >= 1
    assert list(tmp_path.iterdir()) == []
```

- [ ] **Step 2: Correr y ver que falla** (`NameError: medir_repeticion`)
- [ ] **Step 3: Implementar `medir_repeticion`**
- [ ] **Step 4: Correr y ver que pasa.** Expected: 5 passed
- [ ] **Step 5: Commit** `feat: medicion por epoca con paso_entrenamiento sin tocar salidas`

### Task 4: Datos del entorno, informe y CLI

**Files:**
- Modify: `scrips/medir_linea_base.py`
- Modify: `test/test_medir_linea_base.py`

**Interfaces:**
- Produces: `datos_entorno() -> dict` con `cpu` (en Windows, `ProcessorNameString` del registro con `winreg`; si no, `platform.processor()`), `nucleos_fisicos`, `nucleos_logicos`, `hilos_torch` (`torch.get_num_threads()`), `hilos_interop` (`torch.get_num_interop_threads()`), `ram_total`, `python`, `torch`, `numpy`, `so` (`platform.platform()`), `commit` (`git rev-parse --short HEAD`, más `-dirty` si `git status --porcelain` no está vacío, o `desconocido`; Review Focus 2) y `fecha` (ISO local, al minuto).
- Produces: `armar_informe(entorno: dict, repeticiones: list[tuple[list[float], dict]], peak_wset: int | None, nota: str) -> str` en Markdown con:
  1. Entorno y condiciones (`--nota`).
  2. Una tabla por repetición (calentamiento, media, mediana, mín., máx.) y una global con las 5 × 3 épocas medidas.
  3. CPU: el uso del proceso como % de la máquina y como núcleos equivalentes, más el uso del sistema. Incluye esta explicación fija: *psutil mide el proceso en "% de un núcleo", así que 400 % son 4 núcleos ocupados. Dividido entre los núcleos lógicos da el % de la máquina completa (400 % en 16 núcleos = 25 %). El uso del sistema incluye a todos los programas: si es mucho mayor que el del proceso, había otros programas ocupando CPU.*
  4. RAM: RSS máximo muestreado, `peak_wset` (o "no disponible"; Review Focus 5) y RAM total.
  5. Qué se mide y qué no: el ciclo de lotes, sin el guardado por época de `entrenar()`.
  6. El comando exacto para repetir la medición.
- Produces: `main(argv: list[str] | None = None) -> None` con argparse `--epocas` (int, default 6, error si es menor que 2; Review Focus 1), `--repeticiones` (int, default 3, mínimo 1), `--nota` (str, default `""`) y `--salida` (ruta; si falta, solo imprime). Hace `os.chdir(RAIZ)` (Review Focus 3), construye los loaders con `pipeline_dataset_dem("data/raw", batch_size=4)` y comprueba que `len(loader_train) == 72` antes de medir.

- [ ] **Step 1: Escribir las pruebas que fallan**

```python
def test_epocas_menor_que_2_es_error():
    with pytest.raises(SystemExit):
        main(["--epocas", "1"])

def test_informe_contiene_secciones():
    entorno = {k: "x" for k in ["cpu", "python", "torch", "numpy", "so", "commit", "fecha"]}
    entorno.update(nucleos_fisicos=8, nucleos_logicos=16, hilos_torch=8, hilos_interop=8, ram_total=16 * 2**30)
    recursos = {"cpu_proceso": 400.0, "cpu_sistema": 30.0, "rss_max": 2**30, "muestras": 10}
    texto = armar_informe(entorno, [([9.0, 5.0, 5.0], recursos)], None, "enchufada")
    assert "25.0 %" in texto and "4.00 núcleos" in texto
    assert "enchufada" in texto and "no disponible" in texto
    assert "python scrips/medir_linea_base.py" in texto

def test_datos_entorno_tiene_claves():
    e = datos_entorno()
    assert e["nucleos_logicos"] >= e["nucleos_fisicos"] >= 1
    assert e["hilos_torch"] >= 1 and e["commit"]
```

- [ ] **Step 2: Correr y ver que fallan**
- [ ] **Step 3: Implementar `datos_entorno`, `armar_informe` y `main`**
- [ ] **Step 4: Correr la suite completa.** Run: `python -m pytest test/ -q`. Expected: 42 + 8 = 50 passed
- [ ] **Step 5: Commit** `feat: script medir_linea_base con informe y opciones de linea de comandos`

### Task 5: Corrida real, informe y cierre

**Files:**
- Create: `docs/linea_base.md` (lo genera el script)
- Modify: `docs/bitacora.md`, `CLAUDE.md`

- [ ] **Step 1: Comprobar que `salidas/` no cambia.** Guardar el hash de `salidas/historial.csv` y la lista de `salidas/checkpoints/` antes de la corrida.
- [ ] **Step 2: Corrida real** con las condiciones que Fernando dicte para `--nota`:
  `python scrips/medir_linea_base.py --salida docs/linea_base.md --nota "<condiciones>"`
  Se espera 72 lotes por época y unos 2 minutos en total (3 × 6 épocas de ~5 s, más la carga del dataset).
- [ ] **Step 3: Verificar** que el hash y la lista del Step 1 no cambiaron, que la carpeta de checkpoints y `modelos/` siguen igual, y que el informe no tiene campos vacíos.
- [ ] **Step 4: Entrada en `docs/bitacora.md`** (v1.1.0: limpieza y línea base) con los números copiados del informe, y quitar el pendiente de CLAUDE.md.
- [ ] **Step 5: Tests en verde** (`python -m pytest test/` y las 10 pruebas de Godot), regenerar el grafo y hacer el commit `docs: linea base del entrenamiento v1.1.0`. Sin tag ni push.
