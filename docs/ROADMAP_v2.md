# Gaia-AI: Roadmap v2.0

Documento de planeación de la versión 2.0. Es la versión simplificada del 12 de noviembre de 2026, basada en el roadmap del 6 de noviembre. Los criterios "Listo cuando" son una propuesta para revisar con el equipo.

## Objetivo

La v2.0 busca terrenos de uso general que otras personas puedan usar como base y completar con lo que quieran. Para eso suma cuatro cosas:

- Elegir el tamaño del mapa.
- Un dataset ampliado, con más clases.
- Un entrenamiento que aproveche el CPU al máximo.
- Un visor integrado que descargue mapas en formatos que abren las apps de visualización y de diseño 3D.

## Cómo se versiona

Desde la v1.0.1 se deja de trabajar por sprints y se trabaja por versiones X.Y.Z:

- **X:** cambio mayor, tras testeo y verificación.
- **Y:** cambios medios (funcionalidades en prueba, depuración, optimización).
- **Z:** cambios menores, como la 1.0.1 (solo gráficos del visor).

Cada versión cierra con tests en verde, entrada en `docs/bitacora.md`, commit y tag `vX.Y.Z`.

## Decisiones tomadas

- **Tamaños:** de 64×64 (mínimo) a 2048×2048 (máximo). Accesos rápidos: 64, 128, 512, 1024 y 2048 (se quitó el 256). Opción personalizada con cualquier múltiplo de 8 entre 64 y 2048, y mapas rectangulares.
- **Un mapa más grande es más territorio**, no el mismo territorio con más detalle.
- **Fuera de la 2.0:** tamaños de 4096 o menores de 64, y el agua y la costa.
- **Clases nuevas:** cañón (id 6) y duna (id 7), agregadas al final de `CLASES`. Nunca se reordena la lista. Preocupa que duna se confunda con lomas.
- **Mundos con más de una clase:** un mapa de clases indica qué terreno va en cada zona.
- **El modelo de la v1.0** (120×120, época 150) se conserva como respaldo del demo y no se sobrescribe.

## Resumen

| Versión | Tema | Depende de |
| --- | --- | --- |
| 1.1.0 | Limpieza y línea base | Nada |
| 1.2.0 | Dataset v3 | Decidir la escala |
| 1.3.0 | Etiquetador automático de clases | 1.2.0 |
| 1.4.0 | Generador totalmente convolucional | 1.2.0 y 1.3.0 |
| 1.5.0 | Entrenamiento a tope de CPU y estabilidad | 1.4.0 y la línea base de 1.1.0 |
| 1.6.0 | Exportación a formatos 3D | Puede empezar en paralelo |
| 1.7.0 | Visor integral | 1.4.0 y 1.6.0 |
| 1.9.x | Candidata a release | Todas las anteriores |
| 2.0.0 | Release con tag y `.exe` | 1.9.x |

## Detalle por versión

### v1.1.0: limpieza y línea base

**Actividades**
- Corregir las inconsistencias conocidas del repo:
  - Documentación: marcadores `[fecha]` y `[10/14/2026]` y errata en `docs/dataset.md`; `preprocesamiento.py` en la bitácora del Sprint 4; llanura 10 y lomas 11 en la del Sprint 6 (son 9 y 12); "18 tests" en `docs/grafo.md` (son 23); la cuenta 260+170 en la bitácora y en `prueba_sombras.gd`.
  - Código: el import de `src.model.discriminador` en `pipeline.py`; el bloque `__main__` viejo de `cargar_dem.py`; `pandas` de `sanos.py`, que no está en `requirements.txt`; `notebooks/` vacío y los 2 archivos versionados de `data/processed/`; los restos `tempCodeRunnerFile.py` y `comprobacion_reduccion.py` (vacío).
- Medir la línea base del entrenamiento: segundos por época, porcentaje de CPU y RAM, junto con los datos de la máquina.

**Listo cuando:** los 42 tests de Python y las 10 pruebas de Godot pasan, `docs/linea_base.md` tiene números reales y hay tag `v1.1.0`.

### v1.2.0: dataset v3

**Actividades**
- Fijar la escala del dataset (ver "Decisiones pendientes").
- Hacer descargas grandes y recortarlas en local. La API limita las llamadas por día (50 por 24 h), así que conviene pedir regiones amplias y sacar los tiles de ahí. Confirmar el área máxima por petición en la documentación de OpenTopography.
- Definir un criterio medible por clase (por ejemplo, rangos de relieve), con atención a separar duna de lomas.
- Agregar las clases cañón (id 6) y duna (id 7).
- Rehacer los tiles de Paricutín y Colima, donde el cono no domina el centro.
- Dejar más de un tile por clase en validación y prueba.
- Pasar a normalización global.

**Listo cuando:** `docs/dataset.md` describe la v3 con el conteo por clase y el criterio de cada una, no hay píxeles sin dato, y validación y prueba tienen más de un tile por clase.

### v1.3.0: etiquetador automático

**Actividades**
- Entrenar una CNN pequeña que genere mapas de clases por zonas a partir del terreno.
- Revisar a mano una muestra de sus resultados.

**Listo cuando:** hay mapas de clases para el dataset y un reporte de acierto sobre la muestra revisada.

### v1.4.0: generador totalmente convolucional

**Actividades**
- Quitar la capa `Linear` del generador y usar ruido espacial.
- Condicionar con el mapa de clases.
- Entrenar con recortes de 128.
- Inferencia por bloques con traslape, para generar cualquier tamaño.

**Listo cuando:** genera mapas de varios tamaños, incluido uno rectangular, sin costuras visibles entre bloques, con tests nuevos.

### v1.5.0: entrenamiento a tope de CPU y estabilidad

**Actividades**
- Aprovechar todos los núcleos disponibles.
- Estabilizar el entrenamiento: frenar al discriminador y aplicar label smoothing.
- Comparar contra la línea base de la v1.1.0.

**Listo cuando:** hay un reporte de segundos por época y porcentaje de CPU frente a la línea base, una curva de pérdidas más equilibrada y un checkpoint elegido con criterio documentado.

### v1.6.0: exportación (puede empezar en paralelo)

**Actividades**
- Exportar a PNG de 16 bits, OBJ, STL y GLB, con metros reales.
- Ajustar los tamaños para Unity (2ⁿ+1) y para Unreal.

**Listo cuando:** los archivos abren en al menos una aplicación de visualización o de diseño 3D, y hay tests del formato.

### v1.7.0: visor integral

**Actividades**
- Selector de tamaño de 64 a 2048, con los accesos rápidos, la opción personalizada y los mapas rectangulares.
- Terreno por pedazos con niveles de detalle (LOD).
- Mapa de clases aleatorio. El mapa pintado a mano pasa a la 2.1 si el tiempo aprieta.
- Botón de descarga con los formatos de la v1.6.0.

**Listo cuando:** el visor genera y descarga un mapa de 2048 sin congelarse y mantiene los respaldos para cuando el servidor no responde.

### v1.9.x y v2.0.0

- **1.9.x:** candidata a release, con pruebas de punta a punta.
- **2.0.0:** tag, `.exe`, notas de release y documentación actualizada.

## Camino crítico

- **1.2.0 marca el ritmo.** El límite de descargas por día puede tardar varios días de reloj aunque el código sea corto, así que conviene lanzar las descargas apenas esté decidida la escala.
- **La cadena principal** es 1.2.0 → 1.3.0 → 1.4.0 → 1.5.0 → 1.7.0.
- **La 1.6.0** no depende del dataset ni del modelo, solo de tener un mapa de altura, así que puede avanzar en paralelo.

## Decisiones pendientes

- **Escala del dataset:** 60 m/px (recomendada) o 90 m/px.

## Si el tiempo aprieta (pasa a la v2.1)

- Pintado de regiones.
- Costa.
- Valle glaciar.
- Superresolución.

## Riesgos

- **Entrenar mapas más grandes en CPU** tarda más que los 5 s por época de hoy. La línea base de la v1.1.0 sirve para estimarlo.
- **Duna y lomas** pueden confundirse; el criterio medible de la v1.2.0 existe para evitarlo.
- **Un mapa de 2048×2048** exige LOD y memoria cuidadosa en el visor y en la inferencia por bloques.
