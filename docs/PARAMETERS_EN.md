# Parameters Guide — RVC Voice Converter

Detailed explanation of every option available in the interface, how it works, and how to adjust it for the desired result.

---

## F0 Method

**Pitch extraction algorithm.** The pitch is the fundamental frequency of the voice (what we perceive as "low" or "high"). RVC needs to extract it from the original audio to properly transfer it to the converted voice.

| Option | Quality | Speed | Recommended use |
|---|---|---|---|
| **RMVPE** | Excellent | Medium | **Default option.** Best overall balance. Works well for both speech and singing. |
| **Crepe** | Very good | Slow | Neural network. Highest accuracy in noisy environments, but significantly slower. |
| **Harvest** | Good | Medium | Traditional, accurate on clean audio. Recommended for melodic singing. |
| **PM** | Acceptable | Fast | Fast algorithm, less accurate. Useful for quick tests or very clean audio. |

**When to change?**

- If the voice sounds "out of tune" or has unwanted vibrato: try **Crepe** or **RMVPE**.
- If processing is too slow: try **Harvest** or **PM**.
- For singing: **Harvest** or **RMVPE** usually give better results.

---

## Transpose

**Pitch shift in semitones.** Raises or lowers the pitch of the converted voice without changing speed.

| Value | Effect |
|---|---|
| `0` | No pitch change |
| `+12` | One octave up (higher voice) |
| `-12` | One octave down (deeper voice) |
| `+2` to `+5` | Slightly higher voice |
| `-2` to `-5` | Slightly deeper voice |

**Note:** Extreme values (more than ±12) may cause artifacts or distortion. The default `0` is recommended for direct conversion.

---

## Index Rate

**Feature retrieval ratio.** Controls how much the model relies on the `.index` file (if one exists) to transfer the timbre from the original voice to the target voice.

- **0.0**: No index used. Conversion relies solely on the model. More flexible, less character fidelity.
- **0.5**: **Default value.** Balance between naturalness and model fidelity.
- **1.0**: Full index usage. Maximum similarity to the trained voice, but may sound artificial if the index quality is poor.

**When to adjust?**

- If the voice sounds "generic" or doesn't resemble the character enough: **increase** (0.6–0.8).
- If the voice sounds "robotic" or has artifacts: **decrease** (0.2–0.4).
- If you don't have an `.index` file, this parameter has no effect.

---

## Protect

**Voiceless consonant protection.** Consonants like **s, f, t, p, ch** are brief high-frequency sounds that the model can distort. This parameter controls how much they are "protected" from the conversion process.

- **0.0**: No protection. All audio is converted equally. May cause lisping "s" sounds or consonant distortion.
- **0.33**: **Default value.** Standard balance.
- **0.50**: Maximum protection. Consonants are mostly taken from the original audio. Clearer voice but may feel less "converted."

**When to adjust?**

- If "s" sounds like whistling or there's consonant distortion: **increase** (0.40–0.50).
- If the voice sounds "muffled" or not converted enough: **decrease** (0.10–0.25).

---

## RMS Mix Rate

**Volume envelope mixing.** Controls how much the original audio's volume dynamics influence the final result.

- **0.00**: Output volume follows the input dynamics exactly (accents, silences, intensity).
- **0.25**: **Default value.** Recommended balance by the RVC community. Natural-sounding voice without losing model identity.
- **1.00**: Output volume uses the model's own envelope. Ignores input dynamics.

**When to adjust?**

- If the voice sounds **metallic**, **robotic**, or has **volume cuts**: **lower** (0.15–0.30). This is the most important parameter for fixing that issue.
- If the voice sounds too "flat" or lacks character: **slightly increase** (0.40–0.60).

---

## Filter Radius

**Median filter radius for pitch smoothing.** Applies a filter that averages pitch across consecutive frames to remove abrupt fluctuations.

- **0**: No smoothing. Maximum expressiveness, but may have artificial vibrato or pitch jumps.
- **3**: **Default value.** Medium smoothing. Good balance.
- **7**: Maximum smoothing. Very stable pitch but may sound monotonous or "flat."

**When to adjust?**

- If the voice has **unwanted vibrato** or sudden pitch jumps: **increase** (4–6).
- If the voice sounds **monotonous** or lacks expression: **decrease** (0–2).

---

## Resample SR

**Output sample rate.** Defines the quality of the final audio. Measured in Hz.

| Value | Meaning |
|---|---|
| `0` | **Default value.** Keeps the model's native sample rate (the one used during training). |
| `22050` | 22 kHz — Radio quality. Small files. |
| `32000` | 32 kHz — Standard quality for v1 models. |
| `40000` | 40 kHz — Good quality. Typical sample rate for v2 models. |
| `44100` | 44.1 kHz — CD quality. High fidelity. |
| `48000` | 48 kHz — Professional quality. Large files. |

**When to change?**

- `0` is safe and works well in all cases.
- Increase to `40000` or `44100` to improve clarity and reduce metallic sound, but files will be larger.
- Decrease to `22050` if you need smaller files or the original audio is low quality.

---

## Summary — Recommended base configuration

| Parameter | Value | Purpose |
|---|---|---|
| F0 Method | `rmvpe` | Best overall quality |
| Transpose | `0` | No pitch change |
| Index Rate | `0.50` | Balance fidelity/naturalness |
| Protect | `0.33` | Standard consonant protection |
| RMS Mix Rate | **`0.25`** | Natural dynamics, reduces metallic sound |
| Filter Radius | `3` | Medium smoothing |
| Resample SR | `0` | Model's native sample rate |

---

## Troubleshooting common issues

| Issue | What to adjust |
|---|---|
| **Metallic / robotic voice** | Lower **RMS Mix Rate** to 0.15–0.25. Try **RMVPE** or **Crepe** for F0 Method. |
| **Voice cuts out or drops** | Lower **RMS Mix Rate** (0.15–0.25). Increase **Protect** to 0.40–0.50. |
| **Whistling "s" consonants** | Increase **Protect** to 0.40–0.50. |
| **Artificial vibrato / out of tune** | Increase **Filter Radius** to 4–6. Change F0 Method to **Crepe**. |
| **Flat voice / lacks expression** | Lower **Filter Radius** to 0–1. Increase **RMS Mix Rate** to 0.40–0.60. |
| **Doesn't sound like the character** | Increase **Index Rate** to 0.70–0.90 (if an .index file is available). |
| **Processing too slow** | Change F0 Method to **PM** or **Harvest**. Set **Resample SR** to 0. |
