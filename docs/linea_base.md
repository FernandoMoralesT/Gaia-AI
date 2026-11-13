# Línea base del entrenamiento

Generado por `scrips/medir_linea_base.py`. Todos los números salen de esta corrida.

## Entorno

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 18:51 |
| Commit | `940b628` |
| CPU | AMD Ryzen 7 5825U with Radeon Graphics |
| Núcleos físicos / lógicos | 8 / 16 |
| Hilos de torch (intra / interop) | 8 / 8 |
| RAM total | 13.84 GiB |
| Python / torch / numpy | 3.13.14 / 2.14.0+cu126 / 2.5.2 |
| Sistema operativo | Windows-11-10.0.26300-SP0 |

## Condiciones

Laptop enchufada, modo de energía Performance, solo VS Code abierto con Claude Code corriendo en su terminal, encendida hace 1 hora, procesador entre 45 y 50 °C antes de la corrida.

## Tiempo por época (6 épocas por repetición: 1 de calentamiento y 5 medidas)

| Repetición | Calentamiento (s) | Media (s) | Mediana (s) | Mín. (s) | Máx. (s) |
|---|---|---|---|---|---|
| 1 | 5.10 | 5.16 | 5.13 | 4.95 | 5.39 |
| 2 | 5.01 | 6.59 | 4.93 | 4.70 | 13.25 |
| 3 | 4.85 | 4.84 | 4.83 | 4.79 | 4.89 |
| Todas (15 épocas) | — | 5.53 | 4.93 | 4.70 | 13.25 |

## CPU (durante las épocas medidas)

| Repetición | Proceso (% de la máquina) | Proceso (núcleos equivalentes) | Sistema (%) | Muestras |
|---|---|---|---|---|
| 1 | 49.1 % | 7.86 núcleos | 65.3 % | 51 |
| 2 | 38.6 % | 6.18 núcleos | 75.5 % | 65 |
| 3 | 49.5 % | 7.93 núcleos | 61.1 % | 48 |

psutil mide el proceso en "% de un núcleo": 400 % son 4 núcleos ocupados. Dividido entre los 16 núcleos lógicos da el % de la máquina completa (400 % en 16 núcleos = 25.0 %). El uso del sistema incluye a todos los programas: si es mucho mayor que el del proceso, había otros programas ocupando CPU.

## RAM

- RSS máximo muestreado (épocas medidas): 0.75 GiB
- Pico del proceso (`peak_wset`, toda la corrida, incluye la carga del dataset): 0.75 GiB
- RAM total de la máquina: 13.84 GiB

## Qué se mide y qué no

Se mide el ciclo de lotes de una época (cargar cada lote y `paso_entrenamiento()`), con los mismos hiperparámetros del entrenamiento real: lotes de 4, 72 lotes por época, Adam con lr 2e-4 y betas (0.5, 0.999), semilla 42. No se mide el guardado por época que hace `entrenar()` (historial, checkpoint y muestras), así que una época real de la v1.0 es un poco más lenta.

## Cómo repetir

```
python scrips/medir_linea_base.py --epocas 6 --repeticiones 3 --nota "..."
```

## Nota sobre esta corrida (agregada a mano, sin cambiar los números)

En la repetición 2, una época tardó 13.25 s, cuando las otras 14 están entre 4.70 y 5.39 s. En esa repetición el proceso bajó a 6.18 núcleos equivalentes y el sistema subió a 75.5 %: otro programa ocupó CPU durante unos segundos. Se decidió conservar la corrida tal cual en lugar de repetirla hasta obtener un resultado limpio. Por eso, **el número de referencia para comparar es la mediana: 4.93 s por época**, que casi no se mueve con un caso extremo. La media global (5.53 s) sí lo arrastra.

Referencia para la v1.5.0: mediana de 4.93 s por época, unos 7.9 núcleos equivalentes de 16 lógicos (torch usa 8 hilos, uno por núcleo físico) y un pico de 0.75 GiB de RAM. Para comparar, medir en las mismas condiciones.
