import test from "node:test";
import assert from "node:assert/strict";

import {
  applySuggestion,
  clampViewport,
  createEditorHistory,
  createSaveSequencer,
  normalizeEditorState,
  previewSuggestion,
  projectGestureViewport,
} from "../../web/game_editor_mobile_component/editor_state.mjs";


const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));


test("normalizes renderer-compatible mobile state without mutating input", () => {
  const raw = {
    sourceDuration: 12,
    inPoint: -8,
    outPoint: 99,
    zoom: 9,
    panX: 80,
    panY: -80,
    captionText: "x".repeat(400),
    captionSize: 200,
    captionY: -2,
    textColor: "not-a-color",
    volume: 500,
    speed: 9,
    qualityMode: "Impossible",
    unknown: "drop",
  };

  const normalized = normalizeEditorState(raw, 12);

  assert.equal(raw.zoom, 9);
  assert.equal(normalized.sourceDuration, 12);
  assert.equal(normalized.inPoint, 0);
  assert.equal(normalized.outPoint, 12);
  assert.equal(normalized.zoom, 2);
  assert.equal(normalized.panX, 25);
  assert.equal(normalized.panY, -25);
  assert.equal(normalized.captionText.length, 240);
  assert.equal(normalized.captionSize, 72);
  assert.equal(normalized.captionY, 5);
  assert.equal(normalized.textColor, "#ffffff");
  assert.equal(normalized.volume, 100);
  assert.equal(normalized.speed, 2);
  assert.equal(normalized.qualityMode, "Adaptive AI");
  assert.equal("unknown" in normalized, false);
});


test("clamps viewport to crop-safe pan bounds", () => {
  assert.deepEqual(clampViewport({ zoom: 1, panX: 20, panY: -20 }), {
    zoom: 1,
    panX: 0,
    panY: 0,
  });
  assert.deepEqual(clampViewport({ zoom: 2, panX: 90, panY: -90 }), {
    zoom: 2,
    panX: 25,
    panY: -25,
  });
});


test("history is immutable, bounded to fifty commits, and undoable", () => {
  const initial = normalizeEditorState({ sourceDuration: 90 }, 90);
  const history = createEditorHistory(initial, 50);
  for (let index = 1; index <= 60; index += 1) {
    history.commit({ ...history.value, zoom: 1 + index / 100 });
  }

  assert.equal(initial.zoom, 1);
  assert.equal(history.snapshot().pastLength, 50);
  assert.equal(history.value.zoom, 1.6);
  for (let index = 0; index < 50; index += 1) history.undo();
  assert.equal(history.canUndo, false);
  assert.equal(history.value.zoom, 1.1);
  assert.equal(history.canRedo, true);
  history.redo();
  assert.equal(history.value.zoom, 1.11);
});


test("AI preview is transient and Apply creates one reversible history entry", () => {
  const base = normalizeEditorState({ sourceDuration: 20, zoom: 1, captionY: 88 }, 20);
  const suggestion = { id: "reframe", patch: { zoom: 1.4, captionY: 76 } };
  const history = createEditorHistory(base);

  const preview = previewSuggestion(history.value, suggestion);
  assert.equal(preview.zoom, 1.4);
  assert.equal(history.value.zoom, 1);
  assert.equal(history.snapshot().pastLength, 0);

  history.commit(applySuggestion(history.value, suggestion, 20));
  assert.equal(history.value.zoom, 1.4);
  assert.equal(history.snapshot().pastLength, 1);
  history.undo();
  assert.deepEqual(history.value, base);
});


test("save sequencer debounces, flushes latest state, and ignores stale ACKs", async () => {
  const sent = [];
  const sequencer = createSaveSequencer((message) => sent.push(message), 12);

  sequencer.schedule({ zoom: 1.1 });
  sequencer.schedule({ zoom: 1.2 });
  await delay(25);
  assert.equal(sent.length, 1);
  assert.equal(sent[0].state.zoom, 1.2);
  assert.equal(sent[0].sequence, 1);
  assert.equal(sent[0].action, "autosave");

  sequencer.schedule({ zoom: 1.3 });
  const flushed = sequencer.flush(undefined, "continue_to_short");
  assert.equal(sent.length, 2);
  assert.equal(flushed.state.zoom, 1.3);
  assert.equal(flushed.sequence, 2);
  assert.equal(flushed.action, "continue_to_short");
  assert.equal(sequencer.snapshot().status, "saving");

  assert.equal(sequencer.acknowledge(2, true), true);
  assert.equal(sequencer.snapshot().status, "saved");
  assert.equal(sequencer.acknowledge(1, false, "old failure"), false);
  assert.equal(sequencer.snapshot().status, "saved");
  sequencer.dispose();
});


test("gesture projection keeps pinch and pan crop-safe", () => {
  assert.deepEqual(projectGestureViewport(
    { zoom: 1.25, panX: 0, panY: 0 },
    { startDistance: 100, currentDistance: 160, deltaX: 400, deltaY: -400, width: 320, height: 568 },
  ), { zoom: 2, panX: 25, panY: -25 });

  assert.deepEqual(projectGestureViewport(
    { zoom: 1, panX: 0, panY: 0 },
    { startDistance: 100, currentDistance: 100, deltaX: 30, deltaY: 30, width: 300, height: 500 },
  ), { zoom: 1, panX: 0, panY: 0 });
});

test("a replacement initialization cancels the previous clip's pending autosave", async () => {
  const { readFileSync } = await import('node:fs');
  const { runInNewContext } = await import('node:vm');
  const source = readFileSync(new URL('../../web/game_editor_mobile_component/editor.mjs', import.meta.url), 'utf8');
  const init = source.slice(source.indexOf('function receiveInit(message)'), source.indexOf('function receiveSaveStatus(message)'));
  const sent = [];
  const sequencer = createSaveSequencer(message => sent.push(message), 12);
  const noop = () => {};
  const scope = {saveSequencer:sequencer, normalizeEditorState, history:{reset:noop},
    projectTitle:{}, renderMarkers:noop, renderAiContext:noop, overlay:{setFocusMap:noop},
    renderState:noop, loadMedia:noop, app:{setAttribute:noop}, setStatus:noop};
  runInNewContext(init, scope);
  sequencer.schedule({zoom:1.7});
  scope.receiveInit({initial_state:{sourceDuration:15},binding:{source_key:'replacement'}});
  await delay(30);
  assert.equal(sent.length, 0, 'old clip autosave must not dispatch after replacement initialization');
  sequencer.schedule({zoom:1.2});
  await delay(30);
  assert.equal(sent.length, 1, 'new clip remains editable');
  sequencer.dispose();
});
