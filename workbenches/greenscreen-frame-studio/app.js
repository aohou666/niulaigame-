(() => {
  "use strict";

  const DB_NAME = "greenscreen-frame-studio-local-eraser";
  const DB_VERSION = 1;
  const DEFAULT_PRESET_ID = "4:3-1440x1080";

  const PRESETS = [
    { id: "16:9-1920x1080", label: "16:9 1920x1080", width: 1920, height: 1080 },
    { id: "16:9-1280x720", label: "16:9 1280x720", width: 1280, height: 720 },
    { id: "4:3-1440x1080", label: "4:3 1440x1080", width: 1440, height: 1080 },
    { id: "4:3-1024x768", label: "4:3 1024x768", width: 1024, height: 768 },
    { id: "1:1-1080x1080", label: "1:1 1080x1080", width: 1080, height: 1080 },
    { id: "3:4-1080x1440", label: "3:4 1080x1440", width: 1080, height: 1440 },
    { id: "9:16-1080x1920", label: "9:16 1080x1920", width: 1080, height: 1920 },
  ];

  const $ = (selector) => document.querySelector(selector);
  const els = {
    newProjectBtn: $("#newProjectBtn"),
    saveBtn: $("#saveBtn"),
    exportCurrentBtn: $("#exportCurrentBtn"),
    exportAllBtn: $("#exportAllBtn"),
    deleteProjectBtn: $("#deleteProjectBtn"),
    projectSelect: $("#projectSelect"),
    frameInput: $("#frameInput"),
    dropTarget: $("#dropTarget"),
    frameList: $("#frameList"),
    presetSelect: $("#presetSelect"),
    bgColorInput: $("#bgColorInput"),
    thresholdInput: $("#thresholdInput"),
    thresholdValue: $("#thresholdValue"),
    guidesToggle: $("#guidesToggle"),
    stageWrap: $("#stageWrap"),
    stage: $("#stage"),
    emptyHint: $("#emptyHint"),
    statusBar: $("#statusBar"),
    projectNameInput: $("#projectNameInput"),
    centerXInput: $("#centerXInput"),
    centerYInput: $("#centerYInput"),
    scaleInput: $("#scaleInput"),
    rotationInput: $("#rotationInput"),
    fitBtn: $("#fitBtn"),
    centerLeftBtn: $("#centerLeftBtn"),
    bottomAlignBtn: $("#bottomAlignBtn"),
    rotateLeftBtn: $("#rotateLeftBtn"),
    rotateRightBtn: $("#rotateRightBtn"),
    removeFrameBtn: $("#removeFrameBtn"),
    clearReferenceBtn: $("#clearReferenceBtn"),
    onionToggle: $("#onionToggle"),
    onionOpacityInput: $("#onionOpacityInput"),
    onionOpacityValue: $("#onionOpacityValue"),
  };

  let db = null;
  let project = null;
  let projectSummaries = [];
  let frameRuntime = new Map();
  let referenceRuntime = null;
  let saveTimer = null;
  let dragState = null;
  let renderPending = false;
  let isHydrating = false;

  function uid(prefix) {
    if (crypto.randomUUID) return `${prefix}-${crypto.randomUUID()}`;
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
  }

  function nowName() {
    const date = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `绿幕项目 ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}${pad(date.getMinutes())}`;
  }

  function setStatus(text) {
    els.statusBar.textContent = text;
  }

  function presetById(id) {
    return PRESETS.find((preset) => preset.id === id) || PRESETS.find((preset) => preset.id === DEFAULT_PRESET_ID);
  }

  function currentFrame() {
    if (!project || !project.selectedFrameId) return null;
    return project.frames.find((frame) => frame.id === project.selectedFrameId) || null;
  }

  function referenceObject() {
    if (!project) return null;
    if (project.referenceFrameId) {
      return project.frames.find((frame) => frame.id === project.referenceFrameId) || null;
    }
    return project.reference || null;
  }

  function activeObject() {
    if (!project) return null;
    return currentFrame();
  }

  function objectRuntime(obj) {
    if (!obj) return null;
    if (obj.kind === "reference") return referenceRuntime;
    return frameRuntime.get(obj.id) || null;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function openDb() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const database = request.result;
        if (!database.objectStoreNames.contains("projects")) {
          database.createObjectStore("projects", { keyPath: "id" });
        }
        if (!database.objectStoreNames.contains("settings")) {
          database.createObjectStore("settings", { keyPath: "key" });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  function txStore(name, mode = "readonly") {
    return db.transaction(name, mode).objectStore(name);
  }

  function requestToPromise(request) {
    return new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function getAllProjects() {
    return requestToPromise(txStore("projects").getAll());
  }

  async function getProject(id) {
    return requestToPromise(txStore("projects").get(id));
  }

  async function putProject(projectData) {
    return requestToPromise(txStore("projects", "readwrite").put(projectData));
  }

  async function deleteProject(id) {
    return requestToPromise(txStore("projects", "readwrite").delete(id));
  }

  async function getSetting(key) {
    const row = await requestToPromise(txStore("settings").get(key));
    return row ? row.value : null;
  }

  async function putSetting(key, value) {
    return requestToPromise(txStore("settings", "readwrite").put({ key, value }));
  }

  function makeProject() {
    const preset = presetById(DEFAULT_PRESET_ID);
    return {
      id: uid("project"),
      name: nowName(),
      createdAt: Date.now(),
      updatedAt: Date.now(),
      presetId: preset.id,
      canvas: { width: preset.width, height: preset.height },
      bgColor: "#00ff00",
      keyThreshold: 64,
      guidesEnabled: true,
      onionEnabled: true,
      onionOpacity: 0.35,
      selectedFrameId: null,
      referenceFrameId: null,
      frames: [],
      reference: null,
    };
  }

  function plainFrame(frame) {
    return {
      id: frame.id,
      kind: "frame",
      name: frame.name,
      blob: frame.blob,
      width: frame.width,
      height: frame.height,
      bbox: frame.bbox,
      transform: frame.transform,
      createdAt: frame.createdAt,
      eraseStrokes: frame.eraseStrokes || [],
    };
  }

  function plainReference(reference) {
    if (!reference) return null;
    return {
      id: reference.id,
      kind: "reference",
      name: reference.name,
      blob: reference.blob,
      width: reference.width,
      height: reference.height,
      bbox: reference.bbox,
      transform: reference.transform,
      createdAt: reference.createdAt,
    };
  }

  function serializeProject() {
    return {
      id: project.id,
      name: project.name,
      createdAt: project.createdAt,
      updatedAt: Date.now(),
      presetId: project.presetId,
      canvas: { ...project.canvas },
      bgColor: project.bgColor,
      keyThreshold: project.keyThreshold,
      guidesEnabled: project.guidesEnabled,
      onionEnabled: project.onionEnabled,
      onionOpacity: project.onionOpacity,
      selectedFrameId: project.selectedFrameId,
      referenceFrameId: project.referenceFrameId || null,
      frames: project.frames.map(plainFrame),
      reference: plainReference(project.reference),
    };
  }

  async function saveProjectNow(silent = false) {
    if (!project) return;
    project.updatedAt = Date.now();
    await putProject(serializeProject());
    await putSetting("lastProjectId", project.id);
    await refreshProjectList();
    if (!silent) setStatus(`已保存：${project.name}`);
  }

  function scheduleSave() {
    if (isHydrating) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      saveProjectNow(true).catch((error) => setStatus(`保存失败：${error.message}`));
    }, 650);
  }

  async function refreshProjectList() {
    const projects = await getAllProjects();
    projectSummaries = projects
      .map((item) => ({
        id: item.id,
        name: item.name,
        updatedAt: item.updatedAt || item.createdAt || 0,
      }))
      .sort((a, b) => b.updatedAt - a.updatedAt);

    els.projectSelect.innerHTML = "";
    for (const summary of projectSummaries) {
      const option = document.createElement("option");
      option.value = summary.id;
      option.textContent = summary.name;
      els.projectSelect.appendChild(option);
    }
    if (project) els.projectSelect.value = project.id;
  }

  function clearRuntime() {
    for (const runtime of frameRuntime.values()) {
      URL.revokeObjectURL(runtime.url);
    }
    frameRuntime = new Map();
    if (referenceRuntime) URL.revokeObjectURL(referenceRuntime.url);
    referenceRuntime = null;
  }

  function loadImage(blob) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(blob);
      const image = new Image();
      image.onload = () => resolve({ image, url });
      image.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("图片读取失败"));
      };
      image.src = url;
    });
  }

  function median(values) {
    if (!values.length) return 0;
    values.sort((a, b) => a - b);
    return values[Math.floor(values.length / 2)];
  }

  function sampleBackground(data, width, height) {
    const band = Math.max(1, Math.min(16, Math.floor(width / 2), Math.floor(height / 2)));
    const reds = [];
    const greens = [];
    const blues = [];
    const allReds = [];
    const allGreens = [];
    const allBlues = [];

    function collect(x, y) {
      const index = (y * width + x) * 4;
      const r = data[index];
      const g = data[index + 1];
      const b = data[index + 2];
      const a = data[index + 3];
      if (a < 8) return;
      allReds.push(r);
      allGreens.push(g);
      allBlues.push(b);
      if (g > r + 20 && g > b + 20) {
        reds.push(r);
        greens.push(g);
        blues.push(b);
      }
    }

    for (let x = 0; x < width; x += 1) {
      for (let y = 0; y < band; y += 1) collect(x, y);
      for (let y = height - band; y < height; y += 1) collect(x, y);
    }
    for (let y = band; y < height - band; y += 1) {
      for (let x = 0; x < band; x += 1) collect(x, y);
      for (let x = width - band; x < width; x += 1) collect(x, y);
    }

    const sourceR = reds.length ? reds : allReds;
    const sourceG = greens.length ? greens : allGreens;
    const sourceB = blues.length ? blues : allBlues;
    return {
      r: median(sourceR) || 0,
      g: median(sourceG) || 255,
      b: median(sourceB) || 0,
    };
  }

  function keyImage(image, threshold) {
    const canvas = document.createElement("canvas");
    canvas.width = image.naturalWidth || image.width;
    canvas.height = image.naturalHeight || image.height;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(image, 0, 0);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const bg = sampleBackground(data, canvas.width, canvas.height);

    let minX = canvas.width;
    let minY = canvas.height;
    let maxX = -1;
    let maxY = -1;

    for (let y = 0; y < canvas.height; y += 1) {
      for (let x = 0; x < canvas.width; x += 1) {
        const index = (y * canvas.width + x) * 4;
        const r = data[index];
        const g = data[index + 1];
        const b = data[index + 2];
        const a = data[index + 3];
        const dr = r - bg.r;
        const dg = g - bg.g;
        const db = b - bg.b;
        const distance = Math.sqrt(dr * dr + dg * dg + db * db);
        const genericGreen = g >= 110 && g - r >= 40 && g - b >= 40;
        const isBackground = a < 8 || distance <= threshold || genericGreen;

        if (isBackground) {
          data[index + 3] = 0;
        } else {
          minX = Math.min(minX, x);
          minY = Math.min(minY, y);
          maxX = Math.max(maxX, x);
          maxY = Math.max(maxY, y);
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);
    const bbox = maxX >= 0
      ? { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 }
      : { x: 0, y: 0, w: canvas.width, h: canvas.height };
    return { canvas, bbox, bg };
  }

  async function hydrateFrame(frame, force = false) {
    if (!force && frameRuntime.has(frame.id)) return;
    const previous = frameRuntime.get(frame.id);
    if (previous) URL.revokeObjectURL(previous.url);
    const { image, url } = await loadImage(frame.blob);
    const keyed = keyImage(image, project.keyThreshold);
    frame.width = image.naturalWidth || image.width;
    frame.height = image.naturalHeight || image.height;
    frame.bbox = keyed.bbox;
    if (!frame.transform) frame.transform = defaultTransform(frame);
    normalizeTransform(frame);
    const baseCanvas = document.createElement("canvas");
    baseCanvas.width = keyed.canvas.width; baseCanvas.height = keyed.canvas.height;
    baseCanvas.getContext("2d").drawImage(keyed.canvas, 0, 0);
    frameRuntime.set(frame.id, { image, url, keyedCanvas: keyed.canvas, baseCanvas, bg: keyed.bg });
    rebuildErased(frame);
  }

  async function hydrateReference(force = false) {
    if (!project.reference) {
      if (referenceRuntime) URL.revokeObjectURL(referenceRuntime.url);
      referenceRuntime = null;
      return;
    }
    if (!force && referenceRuntime) return;
    if (referenceRuntime) URL.revokeObjectURL(referenceRuntime.url);
    const { image, url } = await loadImage(project.reference.blob);
    const keyed = keyImage(image, project.keyThreshold);
    project.reference.width = image.naturalWidth || image.width;
    project.reference.height = image.naturalHeight || image.height;
    project.reference.bbox = keyed.bbox;
    if (!project.reference.transform) project.reference.transform = defaultTransform(project.reference);
    normalizeTransform(project.reference);
    referenceRuntime = { image, url, keyedCanvas: keyed.canvas, bg: keyed.bg };
  }

  async function hydrateProject() {
    isHydrating = true;
    clearRuntime();
    for (const frame of project.frames) {
      frame.kind = "frame";
      await hydrateFrame(frame);
    }
    if (project.reference) {
      project.reference.kind = "reference";
      await hydrateReference();
    }
    isHydrating = false;
  }

  function defaultTransform(obj) {
    const bbox = obj.bbox || { x: 0, y: 0, w: obj.width || 1, h: obj.height || 1 };
    const canvasW = project.canvas.width;
    const canvasH = project.canvas.height;
    const maxW = canvasW * 0.84;
    const targetH = canvasH * 0.72;
    const scale = Math.min(targetH / bbox.h, maxW / bbox.w);
    const anchorX = canvasW * 0.44;
    const baselineY = canvasH * 0.86;
    return {
      x: anchorX - (bbox.x + bbox.w / 2) * scale,
      y: baselineY - (bbox.y + bbox.h) * scale,
      scale,
      rotation: 0,
    };
  }

  function normalizeTransform(obj) {
    if (!obj.transform) obj.transform = defaultTransform(obj);
    if (typeof obj.transform.rotation !== "number" || Number.isNaN(obj.transform.rotation)) {
      obj.transform.rotation = 0;
    }
  }

  function objectRect(obj) {
    const bbox = obj.bbox || { x: 0, y: 0, w: obj.width || 1, h: obj.height || 1 };
    return {
      x: obj.transform.x + bbox.x * obj.transform.scale,
      y: obj.transform.y + bbox.y * obj.transform.scale,
      w: bbox.w * obj.transform.scale,
      h: bbox.h * obj.transform.scale,
    };
  }

  function objectCenter(obj) {
    const rect = objectRect(obj);
    return { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2 };
  }

  function rotationRadians(obj) {
    return ((obj.transform.rotation || 0) * Math.PI) / 180;
  }

  function rotatePoint(point, center, radians) {
    const dx = point.x - center.x;
    const dy = point.y - center.y;
    const cos = Math.cos(radians);
    const sin = Math.sin(radians);
    return {
      x: center.x + dx * cos - dy * sin,
      y: center.y + dx * sin + dy * cos,
    };
  }

  function unrotatePoint(point, center, radians) {
    return rotatePoint(point, center, -radians);
  }

  function setObjectCenter(obj, x, y) {
    const bbox = obj.bbox || { x: 0, y: 0, w: obj.width || 1, h: obj.height || 1 };
    obj.transform.x = x - (bbox.x + bbox.w / 2) * obj.transform.scale;
    obj.transform.y = y - (bbox.y + bbox.h / 2) * obj.transform.scale;
  }

  function setObjectScale(obj, scale, center = objectCenter(obj)) {
    const bbox = obj.bbox || { x: 0, y: 0, w: obj.width || 1, h: obj.height || 1 };
    obj.transform.scale = clamp(scale, 0.01, 20);
    obj.transform.x = center.x - (bbox.x + bbox.w / 2) * obj.transform.scale;
    obj.transform.y = center.y - (bbox.y + bbox.h / 2) * obj.transform.scale;
  }

  function updateCanvasSize() {
    if (!project) return;
    els.stage.width = project.canvas.width;
    els.stage.height = project.canvas.height;
  }

  function requestRender() {
    if (renderPending) return;
    renderPending = true;
    requestAnimationFrame(() => {
      renderPending = false;
      renderStage();
    });
  }

  function drawObject(ctx, obj, alpha = 1) {
    const runtime = objectRuntime(obj);
    if (!runtime || !obj.transform) return;
    const center = objectCenter(obj);
    const radians = rotationRadians(obj);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(center.x, center.y);
    ctx.rotate(radians);
    ctx.drawImage(
      runtime.keyedCanvas,
      obj.transform.x - center.x,
      obj.transform.y - center.y,
      obj.width * obj.transform.scale,
      obj.height * obj.transform.scale,
    );
    ctx.restore();
  }

  function drawGuides(ctx) {
    const w = project.canvas.width;
    const h = project.canvas.height;
    const anchorX = w * 0.44;
    const baselineY = h * 0.86;
    ctx.save();
    ctx.setLineDash([10, 8]);
    ctx.lineWidth = Math.max(1, w / 900);
    ctx.strokeStyle = "rgba(0, 0, 0, 0.38)";
    ctx.beginPath();
    ctx.moveTo(anchorX, 0);
    ctx.lineTo(anchorX, h);
    ctx.moveTo(0, baselineY);
    ctx.lineTo(w, baselineY);
    ctx.stroke();
    ctx.strokeStyle = "rgba(255, 255, 255, 0.45)";
    ctx.beginPath();
    ctx.moveTo(w / 2, 0);
    ctx.lineTo(w / 2, h);
    ctx.stroke();
    ctx.restore();
  }

  function drawSelection(ctx, obj) {
    if (!obj || !obj.transform) return;
    const rect = objectRect(obj);
    const center = objectCenter(obj);
    const radians = rotationRadians(obj);
    const scale = canvasToCssScale();
    const handle = 10 / scale;
    ctx.save();
    ctx.translate(center.x, center.y);
    ctx.rotate(radians);
    ctx.lineWidth = Math.max(2 / scale, 1);
    ctx.strokeStyle = obj.kind === "reference" ? "#c0442e" : "#2563a7";
    ctx.setLineDash([8 / scale, 5 / scale]);
    ctx.strokeRect(rect.x - center.x, rect.y - center.y, rect.w, rect.h);
    ctx.setLineDash([]);
    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = obj.kind === "reference" ? "#c0442e" : "#2563a7";
    for (const point of rectHandles(rect, handle)) {
      const x = point.x - center.x;
      const y = point.y - center.y;
      ctx.fillRect(x - handle / 2, y - handle / 2, handle, handle);
      ctx.strokeRect(x - handle / 2, y - handle / 2, handle, handle);
    }
    ctx.restore();
  }

  function renderStage() {
    if (!project) return;
    updateCanvasSize();
    const ctx = els.stage.getContext("2d");
    ctx.clearRect(0, 0, els.stage.width, els.stage.height);
    ctx.fillStyle = project.bgColor;
    ctx.fillRect(0, 0, els.stage.width, els.stage.height);

    if (project.guidesEnabled) drawGuides(ctx);

    const frame = currentFrame();
    const reference = referenceObject();
    if (project.onionEnabled && reference && reference.id !== frame?.id) {
      drawObject(ctx, reference, project.onionOpacity);
    }

    if (frame) drawObject(ctx, frame, 1);

    drawSelection(ctx, activeObject());
    els.emptyHint.style.display = project.frames.length ? "none" : "block";
  }

  function renderProjectControls() {
    if (!project) return;
    els.projectNameInput.value = project.name;
    els.presetSelect.value = project.presetId;
    els.bgColorInput.value = project.bgColor;
    els.thresholdInput.value = String(project.keyThreshold);
    els.thresholdValue.value = String(project.keyThreshold);
    els.guidesToggle.checked = project.guidesEnabled;
    els.onionToggle.checked = project.onionEnabled;
    els.onionOpacityInput.value = String(Math.round(project.onionOpacity * 100));
    els.onionOpacityValue.value = `${Math.round(project.onionOpacity * 100)}%`;
    renderTransformControls();
  }

  function renderTransformControls() {
    const obj = activeObject();
    const enabled = Boolean(obj && obj.transform);
    for (const input of [els.centerXInput, els.centerYInput, els.scaleInput, els.rotationInput]) {
      input.disabled = !enabled;
    }
    for (const button of [els.fitBtn, els.centerLeftBtn, els.bottomAlignBtn, els.rotateLeftBtn, els.rotateRightBtn]) {
      button.disabled = !enabled;
    }
    els.removeFrameBtn.disabled = !currentFrame();
    els.clearReferenceBtn.disabled = !project || !referenceObject();

    if (!enabled) {
      els.centerXInput.value = "";
      els.centerYInput.value = "";
      els.scaleInput.value = "";
      els.rotationInput.value = "";
      return;
    }
    const center = objectCenter(obj);
    els.centerXInput.value = String(Math.round(center.x));
    els.centerYInput.value = String(Math.round(center.y));
    els.scaleInput.value = String(Math.round(obj.transform.scale * 100));
    els.rotationInput.value = String(Math.round(obj.transform.rotation || 0));
  }

  function renderFrameList() {
    els.frameList.innerHTML = "";
    if (!project) return;
    for (const frame of project.frames) {
      const item = document.createElement("div");
      item.className = `frame-item${frame.id === project.selectedFrameId ? " selected" : ""}`;
      item.dataset.id = frame.id;
      item.tabIndex = 0;
      item.role = "button";

      const refLabel = document.createElement("label");
      refLabel.className = "ref-check";
      refLabel.title = "设为洋葱皮参考";
      const refInput = document.createElement("input");
      refInput.type = "checkbox";
      refInput.checked = project.referenceFrameId === frame.id;
      refInput.addEventListener("click", (event) => event.stopPropagation());
      refInput.addEventListener("change", () => toggleReferenceFrame(frame.id, refInput.checked));
      const refText = document.createElement("span");
      refText.textContent = "参考";
      refLabel.append(refInput, refText);

      const img = document.createElement("img");
      img.className = "thumb";
      const runtime = frameRuntime.get(frame.id);
      img.src = runtime ? runtime.url : "";
      img.alt = "";

      const meta = document.createElement("div");
      meta.className = "frame-meta";
      const name = document.createElement("div");
      name.className = "frame-name";
      name.textContent = frame.name;
      const size = document.createElement("div");
      size.className = "frame-size";
      size.textContent = `${frame.width || 0} x ${frame.height || 0}`;
      meta.append(name, size);
      item.append(refLabel, img, meta);
      item.addEventListener("click", () => selectFrame(frame.id));
      item.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectFrame(frame.id);
        }
      });
      els.frameList.appendChild(item);
    }
  }

  function selectFrame(id) {
    if (!project) return;
    project.selectedFrameId = id;
    renderFrameList();
    renderProjectControls();
    requestRender();
    scheduleSave();
  }

  function toggleReferenceFrame(id, checked) {
    if (!project) return;
    project.referenceFrameId = checked ? id : null;
    project.reference = null;
    if (referenceRuntime) URL.revokeObjectURL(referenceRuntime.url);
    referenceRuntime = null;
    project.onionEnabled = Boolean(project.referenceFrameId) || project.onionEnabled;
    renderFrameList();
    renderProjectControls();
    requestRender();
    setStatus(checked ? "已设置洋葱皮参考帧" : "已清除参考帧");
    saveProjectNow(true).catch((error) => setStatus(`保存失败：${error.message}`));
  }

  async function loadProject(id) {
    const stored = await getProject(id);
    if (!stored) return false;
    project = stored;
    project.guidesEnabled = project.guidesEnabled !== false;
    project.onionEnabled = project.onionEnabled !== false;
    project.onionOpacity = typeof project.onionOpacity === "number" ? project.onionOpacity : 0.35;
    project.frames = project.frames || [];
    if (project.referenceFrameId && !project.frames.some((frame) => frame.id === project.referenceFrameId)) {
      project.referenceFrameId = null;
    }
    if (!project.selectedFrameId && project.frames[0]) project.selectedFrameId = project.frames[0].id;
    await hydrateProject();
    await putSetting("lastProjectId", project.id);
    await refreshProjectList();
    renderProjectControls();
    renderFrameList();
    requestRender();
    setStatus(`已打开：${project.name}`);
    return true;
  }

  async function createNewProject() {
    clearRuntime();
    project = makeProject();
    await saveProjectNow(true);
    await refreshProjectList();
    renderProjectControls();
    renderFrameList();
    requestRender();
    setStatus(`新项目：${project.name}`);
  }

  function supportedImage(file) {
    if (!file) return false;
    if (file.type && file.type.startsWith("image/")) return true;
    return /\.(png|jpe?g|webp|bmp|gif|tiff?)$/i.test(file.name || "");
  }

  async function addFrameFiles(files) {
    const imageFiles = Array.from(files).filter(supportedImage);
    if (!imageFiles.length) return;
    if (!project) await createNewProject();
    setStatus(`正在导入 ${imageFiles.length} 张图片...`);
    const firstNewId = project.frames.length ? null : undefined;
    let selectedId = firstNewId;

    for (const file of imageFiles) {
      const frame = {
        id: uid("frame"),
        kind: "frame",
        name: file.name,
        blob: file,
        width: 0,
        height: 0,
        bbox: null,
        transform: null,
        createdAt: Date.now(),
      };
      await hydrateFrame(frame);
      project.frames.push(frame);
      if (selectedId === undefined || selectedId === null) selectedId = frame.id;
    }

    if (selectedId) project.selectedFrameId = selectedId;
    renderFrameList();
    renderProjectControls();
    requestRender();
    await saveProjectNow(true);
    setStatus(`已导入 ${imageFiles.length} 张图片`);
  }

  function clearReference() {
    if (!project || !referenceObject()) return;
    project.referenceFrameId = null;
    project.reference = null;
    if (referenceRuntime) URL.revokeObjectURL(referenceRuntime.url);
    referenceRuntime = null;
    renderFrameList();
    renderProjectControls();
    requestRender();
    saveProjectNow(true).catch((error) => setStatus(`保存失败：${error.message}`));
  }

  function removeCurrentFrame() {
    const frame = currentFrame();
    if (!frame) return;
    const index = project.frames.findIndex((item) => item.id === frame.id);
    const runtime = frameRuntime.get(frame.id);
    if (runtime) URL.revokeObjectURL(runtime.url);
    frameRuntime.delete(frame.id);
    project.frames.splice(index, 1);
    if (project.referenceFrameId === frame.id) {
      project.referenceFrameId = null;
    }
    const next = project.frames[Math.min(index, project.frames.length - 1)];
    project.selectedFrameId = next ? next.id : null;
    renderFrameList();
    renderProjectControls();
    requestRender();
    scheduleSave();
  }

  async function rekeyAllFrames() {
    if (!project) return;
    setStatus("正在重新抠绿...");
    for (const frame of project.frames) {
      await hydrateFrame(frame, true);
    }
    await hydrateReference(true);
    renderFrameList();
    renderProjectControls();
    requestRender();
    scheduleSave();
    setStatus("抠绿已更新");
  }

  function setPreset(id) {
    const preset = presetById(id);
    if (!project || !preset) return;
    const oldW = project.canvas.width;
    const oldH = project.canvas.height;
    const ratioX = preset.width / oldW;
    const ratioY = preset.height / oldH;
    const ratioScale = Math.min(ratioX, ratioY);
    const objects = [...project.frames, project.reference && !project.referenceFrameId ? project.reference : null].filter(Boolean);
    for (const obj of objects) {
      if (!obj.transform) continue;
      obj.transform.x *= ratioX;
      obj.transform.y *= ratioY;
      obj.transform.scale *= ratioScale;
    }
    project.presetId = preset.id;
    project.canvas = { width: preset.width, height: preset.height };
    updateCanvasSize();
    renderProjectControls();
    requestRender();
    scheduleSave();
  }

  function resetFitSelected() {
    const obj = activeObject();
    if (!obj) return;
    obj.transform = defaultTransform(obj);
    renderTransformControls();
    requestRender();
    scheduleSave();
  }

  function centerLeftSelected() {
    const obj = activeObject();
    if (!obj) return;
    const center = objectCenter(obj);
    setObjectCenter(obj, project.canvas.width * 0.44, center.y);
    renderTransformControls();
    requestRender();
    scheduleSave();
  }

  function bottomAlignSelected() {
    const obj = activeObject();
    if (!obj) return;
    const bbox = obj.bbox || { x: 0, y: 0, w: obj.width || 1, h: obj.height || 1 };
    obj.transform.y = project.canvas.height * 0.86 - (bbox.y + bbox.h) * obj.transform.scale;
    renderTransformControls();
    requestRender();
    scheduleSave();
  }

  function canvasPoint(event) {
    const rect = els.stage.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * (els.stage.width / rect.width),
      y: (event.clientY - rect.top) * (els.stage.height / rect.height),
    };
  }

  function canvasToCssScale() {
    const rect = els.stage.getBoundingClientRect();
    return rect.width ? rect.width / els.stage.width : 1;
  }

  function rectHandles(rect, size) {
    return [
      { name: "nw", x: rect.x, y: rect.y },
      { name: "ne", x: rect.x + rect.w, y: rect.y },
      { name: "sw", x: rect.x, y: rect.y + rect.h },
      { name: "se", x: rect.x + rect.w, y: rect.y + rect.h },
    ].map((point) => ({ ...point, size }));
  }

  function hitTest(obj, point) {
    if (!obj) return null;
    const rect = objectRect(obj);
    const center = objectCenter(obj);
    const radians = rotationRadians(obj);
    const handleSize = 12 / canvasToCssScale();
    for (const handle of rectHandles(rect, handleSize)) {
      const rotatedHandle = rotatePoint(handle, center, radians);
      if (Math.abs(point.x - rotatedHandle.x) <= handleSize && Math.abs(point.y - rotatedHandle.y) <= handleSize) {
        return { mode: "scale", handle: handle.name };
      }
    }
    const localPoint = unrotatePoint(point, center, radians);
    if (localPoint.x >= rect.x && localPoint.x <= rect.x + rect.w && localPoint.y >= rect.y && localPoint.y <= rect.y + rect.h) {
      return { mode: "move" };
    }
    return null;
  }

  function onPointerDown(event) {
    const obj = activeObject();
    if (!obj || event.button !== 0) return;
    const point = canvasPoint(event);
    if (document.querySelector("#editMode").value === "erase") {
      obj.eraseStrokes ||= [];
      const stroke = { radius: Number(document.querySelector("#brushSize").value) / (2 * obj.transform.scale), points: [sourcePoint(obj, point)] };
      obj.eraseStrokes.push(stroke);
      dragState = { obj, stroke, pointerId: event.pointerId, hit: { mode: "erase" } };
      els.stage.setPointerCapture(event.pointerId);
      rebuildErased(obj); requestRender(); return;
    }
    const hit = hitTest(obj, point);
    if (!hit) return;
    const center = objectCenter(obj);
    dragState = {
      obj,
      hit,
      pointerId: event.pointerId,
      startPoint: point,
      startTransform: { ...obj.transform },
      startCenter: center,
      startDistance: Math.max(1, Math.hypot(point.x - center.x, point.y - center.y)),
    };
    els.stage.setPointerCapture(event.pointerId);
    els.stage.classList.add("dragging");
  }

  function onPointerMove(event) {
    if (!dragState) return;
    const point = canvasPoint(event);
    const obj = dragState.obj;
    if (dragState.hit.mode === "erase") {
      dragState.stroke.points.push(sourcePoint(obj, point));
      rebuildErased(obj); requestRender(); return;
    }
    if (dragState.hit.mode === "move") {
      obj.transform.x = dragState.startTransform.x + point.x - dragState.startPoint.x;
      obj.transform.y = dragState.startTransform.y + point.y - dragState.startPoint.y;
    } else {
      const distance = Math.max(1, Math.hypot(point.x - dragState.startCenter.x, point.y - dragState.startCenter.y));
      const factor = distance / dragState.startDistance;
      obj.transform = { ...dragState.startTransform };
      setObjectScale(obj, dragState.startTransform.scale * factor, dragState.startCenter);
    }
    renderTransformControls();
    requestRender();
  }

  function onPointerUp(event) {
    if (!dragState || dragState.pointerId !== event.pointerId) return;
    els.stage.releasePointerCapture(event.pointerId);
    els.stage.classList.remove("dragging");
    dragState = null;
    scheduleSave();
  }

  function onWheel(event) {
    const obj = activeObject();
    if (!obj) return;
    event.preventDefault();
    const point = canvasPoint(event);
    const factor = Math.exp(-event.deltaY * 0.001);
    const oldScale = obj.transform.scale;
    const nextScale = clamp(oldScale * factor, 0.01, 20);
    obj.transform.x = point.x - (point.x - obj.transform.x) * (nextScale / oldScale);
    obj.transform.y = point.y - (point.y - obj.transform.y) * (nextScale / oldScale);
    obj.transform.scale = nextScale;
    renderTransformControls();
    requestRender();
    scheduleSave();
  }

  function updateTransformFromInputs() {
    const obj = activeObject();
    if (!obj) return;
    const centerX = Number(els.centerXInput.value);
    const centerY = Number(els.centerYInput.value);
    const scalePct = Number(els.scaleInput.value);
    const rotation = Number(els.rotationInput.value);
    if (Number.isFinite(scalePct) && scalePct > 0) {
      setObjectScale(obj, scalePct / 100);
    }
    if (Number.isFinite(rotation)) {
      obj.transform.rotation = rotation;
    }
    if (Number.isFinite(centerX) && Number.isFinite(centerY)) {
      setObjectCenter(obj, centerX, centerY);
    }
    requestRender();
    scheduleSave();
  }

  function rotateCurrentFrame(deltaDegrees) {
    const frame = currentFrame();
    if (!frame || !frame.transform) return;
    frame.transform.rotation = Math.round((frame.transform.rotation || 0) + deltaDegrees);
    renderTransformControls();
    requestRender();
    scheduleSave();
  }

  function drawExportFrame(frame) {
    const canvas = document.createElement("canvas");
    canvas.width = project.canvas.width;
    canvas.height = project.canvas.height;
    const ctx = canvas.getContext("2d");
    if (!document.querySelector("#transparentExport").checked) {
      ctx.fillStyle = project.bgColor;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    const runtime = frameRuntime.get(frame.id);
    if (runtime && frame.transform) {
      const center = objectCenter(frame);
      const radians = rotationRadians(frame);
      ctx.save();
      ctx.translate(center.x, center.y);
      ctx.rotate(radians);
      ctx.drawImage(
        runtime.keyedCanvas,
        frame.transform.x - center.x,
        frame.transform.y - center.y,
        frame.width * frame.transform.scale,
        frame.height * frame.transform.scale,
      );
      ctx.restore();
    }
    return canvas;
  }

  function canvasToBlob(canvas) {
    return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
  }

  function safeFileName(name) {
    return name.replace(/[\\/:*?"<>|]+/g, "_").replace(/\s+/g, " ").trim() || "frame";
  }

  function uniqueNames(frames) {
    const seen = new Map();
    return frames.map((frame) => {
      const base = safeFileName(frame.name.replace(/\.[^.]+$/, ""));
      const count = seen.get(base) || 0;
      seen.set(base, count + 1);
      return count ? `${base}_${count + 1}.png` : `${base}.png`;
    });
  }

  function downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function exportCurrent() {
    const frame = currentFrame();
    if (!frame) return;
    await saveProjectNow(true);
    const blob = await canvasToBlob(drawExportFrame(frame));
    downloadBlob(blob, `${safeFileName(frame.name.replace(/\.[^.]+$/, ""))}.png`);
    setStatus("当前帧已导出");
  }

  async function exportAll() {
    if (!project || !project.frames.length) return;
    await saveProjectNow(true);
    const names = uniqueNames(project.frames);

    if (!window.showDirectoryPicker) {
      setStatus("当前浏览器不支持选择文件夹，改为逐张下载...");
      for (let i = 0; i < project.frames.length; i += 1) {
        setStatus(`正在下载 ${i + 1}/${project.frames.length}: ${names[i]}`);
        const blob = await canvasToBlob(drawExportFrame(project.frames[i]));
        downloadBlob(blob, names[i]);
        await yieldToBrowser();
      }
      setStatus(`已触发 ${project.frames.length} 张 PNG 下载`);
      return;
    }

    let directory;
    try {
      directory = await window.showDirectoryPicker({ mode: "readwrite" });
    } catch (error) {
      if (error && error.name === "AbortError") {
        setStatus("已取消导出");
        return;
      }
      throw error;
    }

    for (let i = 0; i < project.frames.length; i += 1) {
      const name = names[i];
      setStatus(`正在写入 ${i + 1}/${project.frames.length}: ${name}`);
      const blob = await canvasToBlob(drawExportFrame(project.frames[i]));
      await writeBlobToDirectory(directory, name, blob);
      await yieldToBrowser();
    }
    setStatus(`已导出 ${project.frames.length} 张 PNG 到目标文件夹`);
  }

  async function writeBlobToDirectory(directory, name, blob) {
    const fileHandle = await directory.getFileHandle(name, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(blob);
    await writable.close();
  }

  function yieldToBrowser() {
    return new Promise((resolve) => setTimeout(resolve, 0));
  }


  function sourcePoint(obj, point) {
    const p = unrotatePoint(point, objectCenter(obj), rotationRadians(obj));
    return { x: (p.x - obj.transform.x) / obj.transform.scale, y: (p.y - obj.transform.y) / obj.transform.scale };
  }

  function rebuildErased(frame) {
    const runtime = frameRuntime.get(frame.id);
    if (!runtime?.baseCanvas) return;
    const ctx = runtime.keyedCanvas.getContext("2d");
    ctx.clearRect(0, 0, frame.width, frame.height);
    ctx.drawImage(runtime.baseCanvas, 0, 0);
    ctx.save(); ctx.globalCompositeOperation = "destination-out";
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    for (const stroke of frame.eraseStrokes || []) {
      if (!stroke.points.length) continue;
      ctx.lineWidth = stroke.radius * 2;
      ctx.beginPath(); ctx.arc(stroke.points[0].x, stroke.points[0].y, stroke.radius, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      for (const point of stroke.points.slice(1)) ctx.lineTo(point.x, point.y);
      ctx.stroke();
    }
    ctx.restore();
  }

  async function exportProjectFile() {
    try {
      await saveProjectNow(true);
      const data = serializeProject();
      for (const frame of [...data.frames, ...(data.reference ? [data.reference] : [])]) {
        frame.imageData = await new Promise((resolve, reject) => {
          const reader = new FileReader(); reader.onload = () => resolve(reader.result);
          reader.onerror = () => reject(reader.error); reader.readAsDataURL(frame.blob);
        });
        delete frame.blob;
      }
      downloadBlob(new Blob([JSON.stringify({ format: "green-frame-project", version: 1, project: data })], { type: "application/json" }), safeFileName(project.name) + ".green-project.json");
      setStatus("项目已导出，包含原图、橡皮擦和位置参数；请随便携包带到新电脑。");
    } catch (error) { setStatus("导出项目失败：" + error.message); }
  }

  async function importProjectFile(file) {
    if (!file) return;
    try {
      const packet = JSON.parse(await file.text());
      if (packet.format !== "green-frame-project" || packet.version !== 1 || !Array.isArray(packet.project?.frames)) throw new Error("不是支持的项目文件");
      const data = packet.project;
      for (const frame of [...data.frames, ...(data.reference ? [data.reference] : [])]) {
        if (typeof frame.imageData !== "string" || !frame.imageData.startsWith("data:image/")) throw new Error("项目缺少原图");
        frame.blob = await (await fetch(frame.imageData)).blob(); delete frame.imageData;
        if (!Array.isArray(frame.eraseStrokes || [])) throw new Error("橡皮擦数据损坏");
      }
      await saveProjectNow(true);
      data.id = uid("project"); data.name += "（导入）";
      await putProject(data); await refreshProjectList(); await loadProject(data.id);
      setStatus("项目已导入，可继续抠像和调整位置。");
    } catch (error) { setStatus("导入失败：" + error.message); }
  }
  function bindEvents() {
    document.querySelector("#backupProjectBtn").addEventListener("click", exportProjectFile);
    document.querySelector("#importProjectInput").addEventListener("change", async event => { await importProjectFile(event.target.files[0]); event.target.value = ""; });
    document.querySelector("#editMode").addEventListener("change", event => { els.stage.style.cursor = event.target.value === "erase" ? "crosshair" : "grab"; });
    document.querySelector("#undoEraseBtn").addEventListener("click", () => { const frame = currentFrame(); if (!frame) return; frame.eraseStrokes?.pop(); rebuildErased(frame); requestRender(); scheduleSave(); });
    document.querySelector("#resetEraseBtn").addEventListener("click", () => { const frame = currentFrame(); if (!frame || !confirm("恢复当前帧被橡皮擦擦掉的部分？")) return; frame.eraseStrokes = []; rebuildErased(frame); requestRender(); scheduleSave(); });

    els.newProjectBtn.addEventListener("click", createNewProject);
    els.saveBtn.addEventListener("click", () => saveProjectNow(false));
    els.exportCurrentBtn.addEventListener("click", exportCurrent);
    els.exportAllBtn.addEventListener("click", exportAll);
    els.deleteProjectBtn.addEventListener("click", async () => {
      if (!project) return;
      if (!window.confirm(`删除项目“${project.name}”？`)) return;
      const id = project.id;
      await deleteProject(id);
      clearRuntime();
      await refreshProjectList();
      if (projectSummaries[0]) {
        await loadProject(projectSummaries[0].id);
      } else {
        await createNewProject();
      }
      setStatus("项目已删除");
    });

    els.projectSelect.addEventListener("change", async () => {
      await loadProject(els.projectSelect.value);
    });

    els.frameInput.addEventListener("change", async () => {
      await addFrameFiles(els.frameInput.files);
      els.frameInput.value = "";
    });

    for (const node of [els.dropTarget, els.stageWrap]) {
      node.addEventListener("dragover", (event) => {
        event.preventDefault();
        node.classList.add("active");
      });
      node.addEventListener("dragleave", () => node.classList.remove("active"));
      node.addEventListener("drop", async (event) => {
        event.preventDefault();
        node.classList.remove("active");
        await addFrameFiles(event.dataTransfer.files);
      });
    }

    els.projectNameInput.addEventListener("input", () => {
      if (!project) return;
      project.name = els.projectNameInput.value.trim() || "未命名项目";
      scheduleSave();
    });

    els.presetSelect.addEventListener("change", () => setPreset(els.presetSelect.value));
    els.bgColorInput.addEventListener("input", () => {
      project.bgColor = els.bgColorInput.value;
      requestRender();
      scheduleSave();
    });

    let thresholdTimer = null;
    els.thresholdInput.addEventListener("input", () => {
      project.keyThreshold = Number(els.thresholdInput.value);
      els.thresholdValue.value = String(project.keyThreshold);
      clearTimeout(thresholdTimer);
      thresholdTimer = setTimeout(() => rekeyAllFrames(), 260);
    });

    els.guidesToggle.addEventListener("change", () => {
      project.guidesEnabled = els.guidesToggle.checked;
      requestRender();
      scheduleSave();
    });

    els.onionToggle.addEventListener("change", () => {
      project.onionEnabled = els.onionToggle.checked;
      renderProjectControls();
      requestRender();
      scheduleSave();
    });

    els.onionOpacityInput.addEventListener("input", () => {
      project.onionOpacity = Number(els.onionOpacityInput.value) / 100;
      els.onionOpacityValue.value = `${els.onionOpacityInput.value}%`;
      requestRender();
      scheduleSave();
    });

    els.fitBtn.addEventListener("click", resetFitSelected);
    els.centerLeftBtn.addEventListener("click", centerLeftSelected);
    els.bottomAlignBtn.addEventListener("click", bottomAlignSelected);
    els.rotateLeftBtn.addEventListener("click", () => rotateCurrentFrame(-15));
    els.rotateRightBtn.addEventListener("click", () => rotateCurrentFrame(15));
    els.removeFrameBtn.addEventListener("click", removeCurrentFrame);
    els.clearReferenceBtn.addEventListener("click", clearReference);

    for (const input of [els.centerXInput, els.centerYInput, els.scaleInput, els.rotationInput]) {
      input.addEventListener("input", updateTransformFromInputs);
      input.addEventListener("change", updateTransformFromInputs);
    }

    els.stage.addEventListener("pointerdown", onPointerDown);
    els.stage.addEventListener("pointermove", onPointerMove);
    els.stage.addEventListener("pointerup", onPointerUp);
    els.stage.addEventListener("pointercancel", onPointerUp);
    els.stage.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("resize", requestRender);
  }

  function initPresetSelect() {
    for (const preset of PRESETS) {
      const option = document.createElement("option");
      option.value = preset.id;
      option.textContent = preset.label;
      els.presetSelect.appendChild(option);
    }
  }

  async function init() {
    initPresetSelect();
    bindEvents();
    db = await openDb();
    await refreshProjectList();
    const lastProjectId = await getSetting("lastProjectId");
    const openId = lastProjectId && projectSummaries.some((item) => item.id === lastProjectId)
      ? lastProjectId
      : projectSummaries[0]?.id;
    if (openId) {
      await loadProject(openId);
    } else {
      await createNewProject();
    }
  }

  init().catch((error) => {
    console.error(error);
    setStatus(`启动失败：${error.message}`);
  });
})();
