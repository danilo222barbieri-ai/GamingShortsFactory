import test from "node:test";
import assert from "node:assert/strict";

import {
  GAMING_QUICK_ACTIONS,
  combinedQuickActionPatch,
  focusViewport,
  gamingQuickActionPatch,
  normalizeEditorState,
  normalizeFocusMap,
  planGamingCommand,
  sampleFocusMap,
} from "../../web/game_editor_mobile_component/editor_state.mjs";

const persistedKeys = new Set(Object.keys(normalizeEditorState({}, 15)));

test("natural commands map onto existing quick actions only", () => {
  assert.deepEqual(planGamingCommand("segui il giocatore e fai zoom sulle kill").actions, ["follow_action", "zoom_moments"]);
  assert.deepEqual(planGamingCommand("mantieni HUD e minimappa sempre visibili").actions, ["protect_hud"]);
  assert.deepEqual(planGamingCommand("Migliora tutto per favore").actions, ["improve_all"]);
  assert.deepEqual(planGamingCommand("metti i sottotitoli").actions, ["auto_caption"]);
  const unknown = planGamingCommand("ciao come va");
  assert.equal(unknown.understood, false);
  assert.deepEqual(unknown.actions, []);
  for (const action of planGamingCommand("segui, zoom, hud, caption, 9:16").actions) {
    assert.ok(action in GAMING_QUICK_ACTIONS, action);
  }
});

test("combined AI plan is one bounded persisted patch and keeps trim", () => {
  const base = normalizeEditorState({ sourceDuration: 20, inPoint: 2, outPoint: 12, hudMode: "Off" }, 20);
  const patch = combinedQuickActionPatch(["follow_action", "zoom_moments", "protect_hud"], base);
  for (const key of Object.keys(patch)) assert.ok(persistedKeys.has(key), key);
  assert.equal("inPoint" in patch || "outPoint" in patch, false);
  const next = normalizeEditorState({ ...base, ...patch }, 20);
  assert.equal(next.hudMode, "Smart Safe");
  assert.equal(next.visionEnabled, true);
  assert.ok(next.zoom >= 1.1);
  assert.deepEqual(combinedQuickActionPatch(["auto_caption"], base), gamingQuickActionPatch("auto_caption", base));
  assert.deepEqual(combinedQuickActionPatch(["bogus"], base), {});
});

test("focus map is normalised, sorted and rejects invalid points", () => {
  const map = normalizeFocusMap([
    { time: 6, x: 0.8, y: 0.4, confidence: 0.9, subject: "player", action: "kill" },
    { time: 2, x: -1, y: 2, confidence: 0.7 },
    { time: 99, x: 0.5, y: 0.5, confidence: 1 },
    { time: "x", x: 0.5, y: 0.5 },
    null,
  ], 10);
  assert.equal(map.length, 2);
  assert.deepEqual(map.map((point) => point.time), [2, 6]);
  assert.deepEqual([map[0].x, map[0].y], [0, 1]);
  assert.deepEqual(normalizeFocusMap("nope", 10), []);
});

test("focus sampling interpolates confident points and never invents data", () => {
  const map = normalizeFocusMap([
    { time: 1, x: 0.2, y: 0.5, confidence: 0.9, subject: "player" },
    { time: 2, x: 0.6, y: 0.5, confidence: 0.8, subject: "enemy", action: "kill" },
    { time: 3, x: 0.9, y: 0.1, confidence: 0.1 },
  ], 10);
  const mid = sampleFocusMap(map, 1.5);
  assert.equal(mid.x, 0.4);
  assert.equal(mid.confidence, 0.8);
  assert.equal(sampleFocusMap(map, 8), null);
  assert.equal(sampleFocusMap([], 1), null);
  assert.equal(sampleFocusMap(map, 3).x, 0.6);
});

test("focus viewport centres the subject within manual reframe bounds", () => {
  const left = focusViewport({ x: 0.1, y: 0.5 }, { zoom: 1 });
  assert.ok(left.zoom >= 1.15);
  assert.ok(left.panX > 0);
  const limit = (1 - (1 / left.zoom)) * 50;
  assert.ok(Math.abs(left.panX) <= limit + 1e-3);
  assert.deepEqual(focusViewport(null, { zoom: 1.3, panX: 2, panY: 1 }), { zoom: 1.3, panX: 2, panY: 1 });
});
