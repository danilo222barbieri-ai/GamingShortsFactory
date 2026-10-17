// Pure-core contract of the GSF Alive 2 runtime (web/gsf_alive_v418.js).
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../../web/gsf_alive_v418.js", import.meta.url), "utf8");
const sandbox = { window: {} };
vm.runInNewContext(source, sandbox);
const core = sandbox.window.GSFAlive._core;
const T0 = 1_000_000;
const run = (events, start) => events.reduce((s, [type, data], i) => core.reduce(s, type, data, T0 + i * 1000), start || core.BASE);

test("a fresh visitor is guided to upload", () => {
  assert.equal(core.nextAction(core.BASE), "upload");
  assert.equal(core.reduce(core.BASE, "noop", {}, T0).mode, "idle");
});

test("the full journey hears, guides and carries the user", () => {
  let s = run([["upload.started"], ["upload.progress", { progress: 42 }]]);
  assert.equal(s.mode, "working");
  assert.equal(s.active_job, "upload");
  assert.equal(s.progress, 0.42);
  assert.equal(core.nextAction(s), null, "no nagging while working");
  s = run([["upload.completed"]], s);
  assert.equal(s.mode, "active");
  assert.equal(core.nextAction(s), "create_with_ai");
  s = run([["ai.started"], ["ai.found", { count: 3 }]], s);
  assert.equal(s.message, "Ho trovato 3 momenti forti.");
  assert.equal(core.nextAction(s), "choose_moment");
  s = run([["moment.selected", { index: 1 }]], s);
  assert.equal(core.nextAction(s), "create_short");
  s = run([["render.started"]], s);
  assert.equal(s.active_job, "render");
  s = core.reduce(s, "render.completed", {}, T0 + 60_000);
  assert.equal(s.short_ready, true);
  assert.equal(s.mode, "celebrate");
  assert.equal(core.calmMode(s, T0 + 70_000), "active", "celebration is short");
  assert.equal(core.nextAction(s), "publish");
  s = core.reduce(s, "social.status", { connected: 0 }, T0 + 61_000);
  assert.equal(core.nextAction(s), "connect_social");
  s = core.reduce(s, "publish.started", {}, T0 + 62_000);
  s = core.reduce(s, "publish.completed", { ok: 2, ko: 0 }, T0 + 63_000);
  assert.equal(s.published, true);
  assert.equal(core.nextAction(s), "new_video");
});

test("errors are calm, keep the job and offer retry", () => {
  let s = run([["upload.completed"], ["render.started"], ["failure", { message: "Il montaggio si è fermato." }]]);
  assert.equal(s.mode, "error");
  assert.equal(s.error_job, "render");
  assert.equal(s.active_job, null);
  assert.equal(core.nextAction(s), "retry");
  assert.ok(core.motion(s).dur > 2, "error breathes slowly, never flashes");
  assert.equal(core.calmMode(s, s.updated + 4 * 60_000), "active", "an old error stops colouring the app");
  s = run([["recovered"]], s);
  assert.equal(s.error, null);
});

test("a failed publish is an error, a partial one still celebrates", () => {
  let s = run([["publish.started"], ["publish.completed", { ok: 0, ko: 2 }]]);
  assert.equal(s.error_job, "publish");
  s = run([["publish.started"], ["publish.completed", { ok: 1, ko: 1 }]]);
  assert.equal(s.published, true);
  assert.match(s.message, /1 pubblicati, 1 da riprovare/);
});

test("working breath follows real progress, never invented", () => {
  const s = run([["upload.started"]]);
  const slow = core.motion(core.reduce(s, "upload.progress", { progress: 0.05 }, T0 + 5000)).dur;
  const fast = core.motion(core.reduce(s, "upload.progress", { progress: 0.95 }, T0 + 5000)).dur;
  assert.ok(fast < slow);
  assert.ok(core.motion(core.BASE).dur > core.motion(s).dur);
});

test("stale jobs expire instead of spinning forever", () => {
  const s = run([["render.started"]]);
  assert.equal(core.expire(s, T0 + 60_000).active_job, "render");
  const gone = core.expire(s, T0 + 30 * 60_000);
  assert.equal(gone.active_job, null);
  assert.notEqual(gone.mode, "working");
});

test("a new upload forgets the previous short", () => {
  let s = run([["upload.completed"], ["render.started"], ["render.completed"], ["upload.started"]]);
  assert.equal(s.short_ready, false);
  assert.equal(s.moments_count, 0);
});

test("every guided action has a whisper and copy stays short", () => {
  for (const action of ["upload", "create_with_ai", "choose_moment", "create_short", "publish", "connect_social", "retry", "new_video"]) {
    assert.ok(core.NUDGE[action], action);
    assert.ok(core.NUDGE[action].length <= 48, action);
  }
  assert.match(core.welcome({ ...core.BASE, short_ready: true }), /pronto/);
});
