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

test("unchanged social facts do not retrigger the same idle guidance", () => {
  const first=core.reduce(core.BASE,"social.status",{connected:0},T0);
  const repeated=core.reduce(first,"social.status",{connected:0},T0+10000);
  assert.equal(repeated.seq,first.seq);
  assert.equal(repeated.updated,first.updated);
});

test("expired errors stop forcing retry guidance without forgetting the video", () => {
  const uploaded=core.reduce(core.BASE,"upload.completed",{},T0);
  const failed=core.reduce(uploaded,"failure",{job:"ai",message:"Analisi interrotta"},T0+1000);
  assert.equal(core.nextAction(core.expire(failed,T0+2000)),"retry");
  const calm=core.expire(failed,T0+4*60000);
  assert.equal(calm.mode,"active");
  assert.equal(core.nextAction(calm),"create_with_ai");
  assert.equal(calm.video_ready,true);
});

test("unrelated facts cannot keep a stale analysis spinning", () => {
  let s=core.reduce(core.BASE,"ai.started",{},T0);
  s=core.reduce(s,"social.status",{connected:1},T0+7*60000);
  assert.equal(core.expire(s,T0+7*60000).active_job,null);
});

test("real upload progress still refreshes its inactivity deadline", () => {
  let s=core.reduce(core.BASE,"upload.started",{},T0);
  s=core.reduce(s,"upload.progress",{progress:0.8},T0+9*60000);
  assert.equal(core.expire(s,T0+11*60000).active_job,"upload");
});

test("unrelated facts cannot extend an old error", () => {
  let s=core.reduce(core.BASE,"failure",{job:"ai"},T0);
  s=core.reduce(s,"social.status",{connected:1},T0+4*60000);
  assert.equal(core.nextAction(core.expire(s,T0+4*60000)),"upload");
});

test("restored legacy jobs retain their recent real progress", () => {
  const legacy={...core.BASE,active_job:"upload",job_started:T0,updated:T0+9*60000,progress:0.8};
  delete legacy.job_updated;
  assert.equal(core.expire(legacy,T0+11*60000).active_job,"upload");
  assert.equal(core.expire(legacy,T0+25*60000).active_job,null);
});

test("clearing a video keeps the event sequence monotonic", () => {
  const started = core.reduce(core.BASE, "ai.started", {}, T0);
  const cleared = core.reduce(started, "video.cleared", {}, T0 + 1);
  assert.ok(cleared.seq > started.seq);
  assert.equal(cleared.active_job, null);
});
