# Guía de Parámetros — RVC Voice Converter

Explicación detallada de cada opción disponible en la interfaz, cómo funciona y cómo ajustarla según el resultado que busques.

---

## F0 Method

**Algoritmo de extracción de tono (pitch).** El pitch es la frecuencia fundamental de la voz (lo que percibimos como "grave" o "agudo"). RVC necesita extraerlo del audio original para transferirlo correctamente a la voz convertida.

| Opción | Calidad | Velocidad | Uso recomendado |
|---|---|---|---|
| **RMVPE** | Excelente | Media | **Opción por defecto.** Mejor balance general. Funciona bien en habla y canto. |
| **Crepe** | Muy buena | Lenta | Red neuronal. Máxima precisión en entornos con ruido, pero significativamente más lento. |
| **Harvest** | Buena | Media | Tradicional, preciso en voces limpias. Recomendado para canto melódico. |
| **PM** | Aceptable | Rápida | Algoritmo rápido, menos preciso. Útil para pruebas rápidas o audio muy limpio. |

**¿Cuándo cambiar?**

- Si la voz suena "desafinada" o con vibrato artificial: probar **Crepe** o **RMVPE**.
- Si el procesamiento es muy lento: probar **Harvest** o **PM**.
- Para canto: **Harvest** o **RMVPE** suelen dar mejores resultados.

---

## Transpose

**Desplazamiento de tono en semitonos.** Sube o baja la tonalidad de la voz convertida sin cambiar la velocidad.

| Valor | Efecto |
|---|---|
| `0` | Sin cambio de tono |
| `+12` | Una octava arriba (voz más aguda) |
| `-12` | Una octava abajo (voz más grave) |
| `+2` a `+5` | Voz ligeramente más aguda |
| `-2` a `-5` | Voz ligeramente más grave |

**Nota:** Valores extremos (más de ±12) pueden generar artefactos o distorsión. El valor por defecto `0` es el recomendado para conversión directa.

---

## Index Rate

**Ratio de recuperación de características (feature retrieval).** Controla cuánto se apoya el modelo en el archivo `.index` (si existe) para transferir el timbre de la voz original a la voz objetivo.

- **0.0**: No usa el índice. La conversión se basa únicamente en el modelo. Más flexible, menos fidelidad al personaje.
- **0.5**: **Valor por defecto.** Balance entre naturalidad y fidelidad al modelo.
- **1.0**: Usa el índice al máximo. Mayor similitud con la voz entrenada, pero puede sonar artificial si el índice no es de buena calidad.

**¿Cuándo ajustar?**

- Si la voz suena "genérica" o no se parece suficiente al personaje: **subir** (0.6–0.8).
- Si la voz suena "robótica" o con artefactos: **bajar** (0.2–0.4).
- Si no tienes archivo `.index`, este parámetro no tiene efecto.

---

## Protect

**Protección de consonantes sordas.** Las consonantes como **s, f, t, p, ch** son sonidos breves y de alta frecuencia que el modelo puede distorsionar. Este parámetro controla cuánto se "protegen" del proceso de conversión.

- **0.0**: Sin protección. Todo el audio se convierte por igual. Puede generar "s" silbantes o distorsión en consonantes.
- **0.33**: **Valor por defecto.** Balance estándar.
- **0.50**: Máxima protección. Las consonantes se toman mayormente del audio original. Voz más clara pero puede sentirse menos "convertida".

**¿Cuándo ajustar?**

- Si las "s" suenan como silbidos o hay distorsión en consonantes: **subir** (0.40–0.50).
- Si la voz suena "apagada" o poco convertida: **bajar** (0.10–0.25).

---

## RMS Mix Rate

**Mezcla de envolvente de volumen.** Controla qué tanto la dinámica de volumen del audio original influye en el resultado final.

- **0.00**: El volumen de salida sigue exactamente la dinámica del input (acentos, silencios, intensidad).
- **0.25**: **Valor por defecto.** Balance recomendado por la comunidad RVC. La voz suena natural sin perder la identidad del modelo.
- **1.00**: El volumen de salida usa la envolvente propia del modelo. Ignora la dinámica del input.

**¿Cuándo ajustar?**

- Si la voz suena **metálica**, **robótica** o con **cortes de volumen**: **bajar** (0.15–0.30). Este es el parámetro más importante para corregir ese problema.
- Si la voz suena demasiado "plana" o sin carácter: **subir** ligeramente (0.40–0.60).

---

## Filter Radius

**Radio del filtro de mediana para suavizado de pitch.** Aplica un filtro que promedia el pitch entre frames consecutivos para eliminar fluctuaciones bruscas.

- **0**: Sin suavizado. Máxima expresividad, pero puede tener vibrato artificial o saltos de tono.
- **3**: **Valor por defecto.** Suavizado medio. Buen balance.
- **7**: Suavizado máximo. Pitch muy estable pero puede sonar monótono o "plano".

**¿Cuándo ajustar?**

- Si la voz tiene **vibrato no deseado** o saltos de tono repentinos: **subir** (4–6).
- Si la voz suena **monótona** o sin expresión: **bajar** (0–2).

---

## Resample SR

**Frecuencia de muestreo (sample rate) de salida.** Define la calidad del audio final. Se mide en Hz (hercios).

| Valor | Significado |
|---|---|
| `0` | **Valor por defecto.** Mantiene la frecuencia nativa del modelo (la que usó durante el entrenamiento). |
| `22050` | 22 kHz — Calidad de radio. Archivos pequeños. |
| `32000` | 32 kHz — Calidad estándar para modelos v1. |
| `40000` | 40 kHz — Buena calidad. Frecuencia típica de modelos v2. |
| `44100` | 44.1 kHz — Calidad CD. Alta fidelidad. |
| `48000` | 48 kHz — Calidad profesional. Archivos grandes. |

**¿Cuándo cambiar?**

- `0` es seguro y funciona bien en todos los casos.
- Subir a `40000` o `44100` puede mejorar la claridad y reducir el sonido metálico, pero el archivo será más grande.
- Bajar a `22050` si necesitas archivos pequeños o el audio original es de baja calidad.

---

## Resumen — Configuración base recomendada

| Parámetro | Valor | Propósito |
|---|---|---|
| F0 Method | `rmvpe` | Mejor calidad general |
| Transpose | `0` | Sin cambio de tono |
| Index Rate | `0.50` | Balance fidelidad/naturalidad |
| Protect | `0.33` | Protección estándar de consonantes |
| RMS Mix Rate | **`0.25`** | Dinámica natural, reduce metallicidad |
| Filter Radius | `3` | Suavizado medio |
| Resample SR | `0` | Frecuencia nativa del modelo |

---

## Solución de problemas comunes

| Problema | Qué ajustar |
|---|---|
| **Voz metálica / robótica** | Bajar **RMS Mix Rate** a 0.15–0.25. Probar **RMVPE** o **Crepe** en F0 Method. |
| **Se pierde la voz o hay cortes** | Bajar **RMS Mix Rate** (0.15–0.25). Subir **Protect** a 0.40–0.50. |
| **Consonantes "s" silbantes** | Subir **Protect** a 0.40–0.50. |
| **Vibrato artificial / desafinación** | Subir **Filter Radius** a 4–6. Cambiar F0 Method a **Crepe**. |
| **Voz muy plana / sin expresión** | Bajar **Filter Radius** a 0–1. Subir **RMS Mix Rate** a 0.40–0.60. |
| **No se parece al personaje** | Subir **Index Rate** a 0.70–0.90 (si hay archivo .index). |
| **Procesamiento muy lento** | Cambiar F0 Method a **PM** o **Harvest**. Bajar **Resample SR** a 0. |
