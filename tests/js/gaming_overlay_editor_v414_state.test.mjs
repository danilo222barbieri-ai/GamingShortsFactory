import test from "node:test";
import assert from "node:assert/strict";

import {
  cameraPresetPatch,
  gamingQuickActionPatch,
  inferCameraPreset,
  normalizeEditorState,
} from "../../web/game_editor_mobile_component/editor_state.mjs";

const persistedKeys = new Set([
  "zoom", "panX", "panY", "framePreset", "coverMode", "coverTime", "coverLocked",
  "look", "intensity", "brightness", "contrast", "hudMode", "captionOn", "captionMode",
  "captionText", "captionSize", "captionY", "textColor", "activeColor", "outlineColor",
  "muted", "volume", "speed", "audioMode", "inPoint", "outPoint", "aiMode",
  "visionEnabled", "editorVersion", "sourceDuration", "qualityMode",
]);

function assertPersistedPatch(patch) {
  for (const key of Object.keys(patch)) {
    assert.equal(persistedKeys.has(key), true, `unexpected non-persisted camera field: ${key}`);
  }
  assert.equal("cameraMode" in patch, false);
  assert.equal("cameraKeyframes" in patch, false);
}

test("camera presets are renderer-compatible and recoverable after normalization", () => {
  const base = normalizeEditorState({ sourceDuration: 20, zoom: 1, look: "Clean" }, 20);
  const expected = ["static", "follow", "dynamic", "cinematic"];
  for (const mode of expected) {
    const patch = cameraPresetPatch(mode, base);
    assertPersistedPatch(patch);
    const roundTrip = normalizeEditorState({ ...base, ...patch }, 20);
    assert.equal(inferCameraPreset(roundTrip), mode, mode);
  }
});

test("Follow Action enables existing smart vision instead of inventing preview-only tracking", () => {
  const base = normalizeEditorState({ sourceDuration: 15 }, 15);
  const patch = cameraPresetPatch("follow", base);
  assert.deepEqual(patch, {
    visionEnabled: true,
    aiMode: "Auto Gaming",
    framePreset: "gameplay",
    zoom: 1,
    look: "Clean",
  });
});

test("dynamic and cinematic camera presets remain bounded", () => {
  const base = normalizeEditorState({ sourceDuration: 15, zoom: 1.95 }, 15);
  const dynamic = normalizeEditorState({ ...base, ...cameraPresetPatch("dynamic", base) }, 15);
  const cinematic = normalizeEditorState({ ...base, ...cameraPresetPatch("cinematic", base) }, 15);
  assert.ok(dynamic.zoom <= 2 && dynamic.zoom >= 1.1);
  assert.ok(cinematic.zoom <= 2 && cinematic.zoom >= 1.16);
  assert.equal(dynamic.visionEnabled, true);
  assert.equal(cinematic.visionEnabled, true);
  assert.equal(cinematic.look, "Boss Cinematic");
});

test("gaming quick actions only emit persisted bounded editor fields", () => {
  const base = normalizeEditorState({ sourceDuration: 15, captionMode: "Off", hudMode: "Off" }, 15);
  for (const action of ["follow_action", "auto_vertical", "zoom_moments", "protect_hud", "auto_caption", "improve_all"]) {
    const patch = gamingQuickActionPatch(action, base);
    assertPersistedPatch(patch);
    const normalized = normalizeEditorState({ ...base, ...patch }, 15);
    assert.ok(normalized.zoom >= 0.8 && normalized.zoom <= 2);
    assert.ok(["Off", "Smart Safe"].includes(normalized.hudMode));
    assert.ok(["Auto", "Fixed", "Off"].includes(normalized.captionMode));
  }
});

test("improve all enables safe gaming intelligence without mutating trim", () => {
  const base = normalizeEditorState({ sourceDuration: 18, inPoint: 2, outPoint: 13, captionMode: "Off" }, 18);
  const patch = gamingQuickActionPatch("improve_all", base);
  assert.equal(patch.visionEnabled, true);
  assert.equal(patch.hudMode, "Smart Safe");
  assert.equal(patch.captionMode, "Auto");
  assert.equal("inPoint" in patch, false);
  assert.equal("outPoint" in patch, false);
});
