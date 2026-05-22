const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const dropText = document.getElementById("dropText");
const voiceSelect = document.getElementById("voiceSelect");
const transposeInput = document.getElementById("transpose");
const f0methodSelect = document.getElementById("f0methodSelect");
const indexRateRange = document.getElementById("indexRateRange");
const indexRateNumber = document.getElementById("indexRateNumber");
const indexRateValue = document.getElementById("indexRateValue");
const protectRange = document.getElementById("protectRange");
const protectNumber = document.getElementById("protectNumber");
const protectValue = document.getElementById("protectValue");
const rmsMixRange = document.getElementById("rmsMixRange");
const rmsMixNumber = document.getElementById("rmsMixNumber");
const rmsMixValue = document.getElementById("rmsMixValue");
const filterRadiusRange = document.getElementById("filterRadiusRange");
const filterRadiusNumber = document.getElementById("filterRadiusNumber");
const filterRadiusValue = document.getElementById("filterRadiusValue");
const resampleSrRange = document.getElementById("resampleSrRange");
const resampleSrNumber = document.getElementById("resampleSrNumber");
const resampleSrValue = document.getElementById("resampleSrValue");
const generateBtn = document.getElementById("generateBtn");
const resultSection = document.getElementById("resultSection");
const audioPlayer = document.getElementById("audioPlayer");
const downloadBtn = document.getElementById("downloadBtn");
const errorSection = document.getElementById("errorSection");
const errorMessage = document.getElementById("errorMessage");
const progressSection = document.getElementById("progressSection");
const progressText = document.getElementById("progressText");

let selectedFile = null;
let resultAudioUrl = null;
let chunkSeconds = 32;
let fileDuration = 0;

async function loadServerInfo() {
    try {
        const resp = await fetch("/api/info");
        const data = await resp.json();
        chunkSeconds = data.chunk_seconds || 32;
    } catch {
        chunkSeconds = 32;
    }
}

async function loadVoices() {
    try {
        const resp = await fetch("/api/voices");
        const data = await resp.json();
        voiceSelect.innerHTML = '<option value="">-- Select a voice --</option>';
        if (data.voices && data.voices.length > 0) {
            for (const voice of data.voices) {
                const option = document.createElement("option");
                option.value = voice;
                option.textContent = voice;
                voiceSelect.appendChild(option);
            }
        } else {
            voiceSelect.innerHTML = '<option value="">No voices found</option>';
        }
    } catch {
        voiceSelect.innerHTML = '<option value="">Error loading voices</option>';
    }
}

function updateGenerateButton() {
    const hasFile = selectedFile !== null;
    const hasVoice = voiceSelect.value !== "";
    generateBtn.disabled = !(hasFile && hasVoice);
}

function syncDualControl(source, value, rangeEl, numberEl, valueEl, min, max, decimals) {
    const numVal = parseFloat(value);
    if (isNaN(numVal)) return;
    const clamped = Math.min(max, Math.max(min, numVal));
    const formatted = decimals === 0 ? String(Math.round(clamped)) : clamped.toFixed(decimals);

    if (source !== rangeEl) {
        rangeEl.value = clamped;
    }
    if (source !== numberEl) {
        numberEl.value = formatted;
    }
    valueEl.textContent = formatted;
    generateBtn.disabled = !(selectedFile && voiceSelect.value);
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorSection.style.display = "block";
}

function hideError() {
    errorSection.style.display = "none";
}

function showResult(audioUrl, voice, filename) {
    audioPlayer.src = audioUrl;
    downloadBtn.dataset.audioUrl = audioUrl;
    downloadBtn.dataset.voice = voice;
    downloadBtn.dataset.filename = filename || `converted_${voice}.wav`;
    resultSection.style.display = "block";
}

function hideResult() {
    resultSection.style.display = "none";
}

function hideProgress() {
    progressSection.style.display = "none";
}

function getChunkText() {
    if (fileDuration <= 0) return "Converting audio...";
    const chunks = Math.ceil(fileDuration / chunkSeconds);
    return `Converting audio... (~${chunks} chunk${chunks !== 1 ? "s" : ""}, ${chunkSeconds}s each)`;
}

dropZone.addEventListener("click", () => {
    fileInput.click();
});

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});

function handleFile(file) {
    const validTypes = ["audio/wav", "audio/mpeg", "audio/mp3"];
    const validExts = [".wav", ".mp3"];
    const ext = "." + file.name.split(".").pop().toLowerCase();

    if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
        showError("Please select a WAV or MP3 file.");
        return;
    }

    selectedFile = file;
    hideError();
    hideResult();
    updateGenerateButton();

    const audioEl = new Audio();
    const objectUrl = URL.createObjectURL(file);
    audioEl.src = objectUrl;
    audioEl.onloadedmetadata = () => {
        fileDuration = audioEl.duration;
        const chunks = Math.ceil(fileDuration / chunkSeconds);
        dropText.textContent = `${file.name}  (~${chunks} chunk${chunks !== 1 ? "s" : ""})`;
        URL.revokeObjectURL(objectUrl);
    };
    audioEl.onerror = () => {
        fileDuration = 0;
        dropText.textContent = file.name;
        URL.revokeObjectURL(objectUrl);
    };
}

voiceSelect.addEventListener("change", () => {
    hideError();
    hideResult();
    updateGenerateButton();
});

transposeInput.addEventListener("input", updateGenerateButton);
f0methodSelect.addEventListener("change", updateGenerateButton);

indexRateRange.addEventListener("input", function () {
    syncDualControl(indexRateRange, this.value, indexRateRange, indexRateNumber, indexRateValue, 0, 1, 2);
});
indexRateNumber.addEventListener("input", function () {
    syncDualControl(indexRateNumber, this.value, indexRateRange, indexRateNumber, indexRateValue, 0, 1, 2);
});

protectRange.addEventListener("input", function () {
    syncDualControl(protectRange, this.value, protectRange, protectNumber, protectValue, 0, 0.5, 2);
});
protectNumber.addEventListener("input", function () {
    syncDualControl(protectNumber, this.value, protectRange, protectNumber, protectValue, 0, 0.5, 2);
});

rmsMixRange.addEventListener("input", function () {
    syncDualControl(rmsMixRange, this.value, rmsMixRange, rmsMixNumber, rmsMixValue, 0, 1, 2);
});
rmsMixNumber.addEventListener("input", function () {
    syncDualControl(rmsMixNumber, this.value, rmsMixRange, rmsMixNumber, rmsMixValue, 0, 1, 2);
});

filterRadiusRange.addEventListener("input", function () {
    syncDualControl(filterRadiusRange, this.value, filterRadiusRange, filterRadiusNumber, filterRadiusValue, 0, 7, 0);
});
filterRadiusNumber.addEventListener("input", function () {
    syncDualControl(filterRadiusNumber, this.value, filterRadiusRange, filterRadiusNumber, filterRadiusValue, 0, 7, 0);
});

resampleSrRange.addEventListener("input", function () {
    syncDualControl(resampleSrRange, this.value, resampleSrRange, resampleSrNumber, resampleSrValue, 0, 48000, 0);
});
resampleSrNumber.addEventListener("input", function () {
    syncDualControl(resampleSrNumber, this.value, resampleSrRange, resampleSrNumber, resampleSrValue, 0, 48000, 0);
});

generateBtn.addEventListener("click", async () => {
    if (!selectedFile || !voiceSelect.value) return;

    hideError();
    hideResult();
    hideProgress();

    generateBtn.disabled = true;
    const originalText = generateBtn.innerHTML;
    generateBtn.innerHTML = '<span class="spinner"></span>Processing...';

    progressText.textContent = getChunkText();
    progressSection.style.display = "block";

    try {
        const formData = new FormData();
        formData.append("audio", selectedFile);
        formData.append("voice", voiceSelect.value);
        formData.append("transpose", transposeInput.value || "0");
        formData.append("f0_method", f0methodSelect.value);
        formData.append("index_rate", indexRateNumber.value);
        formData.append("protect", protectNumber.value);
        formData.append("rms_mix_rate", rmsMixNumber.value);
        formData.append("filter_radius", filterRadiusNumber.value);
        formData.append("resample_sr", resampleSrNumber.value);

        const resp = await fetch("/api/convert", {
            method: "POST",
            body: formData,
        });

        if (!resp.ok) {
            const errData = await resp.json().catch(() => null);
            const detail = errData?.detail || `Server error: ${resp.status}`;
            throw new Error(detail);
        }

        const data = await resp.json();
        showResult(data.url, voiceSelect.value, data.filename);
    } catch (err) {
        showError(err.message);
    } finally {
        hideProgress();
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalText;
        updateGenerateButton();
    }
});

downloadBtn.addEventListener("click", () => {
    const audioUrl = downloadBtn.dataset.audioUrl;
    const filename = downloadBtn.dataset.filename || "converted.wav";
    if (!audioUrl) return;

    const a = document.createElement("a");
    a.href = audioUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

Promise.all([loadServerInfo(), loadVoices()]);
