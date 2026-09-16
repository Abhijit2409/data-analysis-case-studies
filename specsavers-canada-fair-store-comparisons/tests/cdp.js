/*
 * Minimal Chrome DevTools Protocol client for headless Microsoft Edge (no npm dependencies; Node 22+ WebSocket).
 * Used by tests/ui_regression.js (rendered-page checks, real key events) and build/capture_screenshots.js.
 */
const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const EDGE = process.env.EDGE_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function killTree(proc) {
  if (!proc || proc.exitCode !== null) return;
  try {
    if (process.platform === "win32") spawnSync("taskkill", ["/PID", String(proc.pid), "/T", "/F"], { stdio: "ignore" });
    else proc.kill();
  } catch (e) { /* ignore */ }
}

function removeDir(dir) {
  // Temporary browser profiles are 10-120 MB each; always delete them.
  for (let i = 0; i < 20; i++) {
    try { fs.rmSync(dir, { recursive: true, force: true }); return; } catch (e) { spawnSync(process.execPath, ["-e", "setTimeout(()=>{},250)"]); }
  }
}

async function launchOnce(timeoutMs) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cdp-casestudy-"));
  const proc = spawn(EDGE, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
    "--disable-extensions", "--disable-background-networking", "--disk-cache-size=1048576", `--user-data-dir=${dir}`, "--remote-debugging-port=0", "about:blank"], { stdio: "ignore" });
  const portFile = path.join(dir, "DevToolsActivePort");
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (fs.existsSync(portFile) && fs.readFileSync(portFile, "utf8").trim()) break;
    await sleep(100);
  }
  if (!fs.existsSync(portFile)) { killTree(proc); removeDir(dir); return null; }
  const port = fs.readFileSync(portFile, "utf8").split(/\r?\n/)[0].trim();
  return {
    port, proc,
    async newPage() {
      const res = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
      const t = await res.json();
      return connect(t.webSocketDebuggerUrl);
    },
    async close() {
      // Graceful shutdown first (headless Edge re-parents helper processes, so killing the launcher alone can leave them running).
      try {
        const v = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
        const b = await connect(v.webSocketDebuggerUrl);
        b.send("Browser.close").catch(() => {});
        await sleep(1500);
        b.close();
      } catch (e) { /* already closed */ }
      killTree(proc);
      for (let i = 0; i < 20 && fs.existsSync(dir); i++) {
        try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) { await sleep(500); }
      }
    },
  };
}

async function launch() {
  if (!fs.existsSync(EDGE)) throw new Error(`Edge not found at ${EDGE}; set EDGE_PATH`);
  // Remove profiles left behind by earlier runs whose browser had not released files in time.
  for (const name of fs.readdirSync(os.tmpdir()).filter((n) => n.startsWith("cdp-casestudy-"))) {
    const p = path.join(os.tmpdir(), name);
    try { if (Date.now() - fs.statSync(p).mtimeMs > 60000) fs.rmSync(p, { recursive: true, force: true }); } catch (e) { /* in use */ }
  }
  for (let attempt = 1; attempt <= 3; attempt++) {
    const b = await launchOnce(30000);
    if (b) return b;
    await sleep(1000);
  }
  throw new Error("Headless Edge did not start (DevToolsActivePort not written after 3 attempts)");
}

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    const listeners = [];
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
      } else if (msg.method) listeners.filter((l) => l.method === msg.method).forEach((l) => l.fn(msg.params));
    };
    ws.onerror = (e) => reject(e);
    ws.onopen = () => {
      const page = {
        send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
        once: (method) => new Promise((res) => { const l = { method, fn: (p) => { listeners.splice(listeners.indexOf(l), 1); res(p); } }; listeners.push(l); }),
        async viewport(width, height, scale = 1) { await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: scale, mobile: false }); },
        async goto(url) {
          await page.send("Page.enable");
          const loaded = page.once("Page.loadEventFired");
          await page.send("Page.navigate", { url });
          await loaded;
          await sleep(150);
        },
        async eval(expression) {
          const r = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
          if (r.exceptionDetails) throw new Error("Page error: " + (r.exceptionDetails.exception ? r.exceptionDetails.exception.description : r.exceptionDetails.text));
          return r.result.value;
        },
        async key(key, code, keyCode, modifiers = 0) {
          const base = { key, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode, modifiers };
          await page.send("Input.dispatchKeyEvent", Object.assign({ type: "rawKeyDown" }, base));
          if (key === "Enter") await page.send("Input.dispatchKeyEvent", Object.assign({ type: "char", text: "\r" }, base));
          await page.send("Input.dispatchKeyEvent", Object.assign({ type: "keyUp" }, base));
          await sleep(40);
        },
        async screenshot(file, { fullPage = false, clipSelector = null, width = null, scale = 1 } = {}) {
          let clip;
          if (clipSelector) {
            const r = await page.eval(`(() => { const e = document.querySelector(${JSON.stringify(clipSelector)}); if (!e) return null; e.scrollIntoView(); const b = e.getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, width: b.width, height: b.height }; })()`);
            if (!r) throw new Error("clip selector not found: " + clipSelector);
            clip = Object.assign(r, { scale });
          }
          if (fullPage || clip) {
            const m = await page.send("Page.getLayoutMetrics");
            const h = Math.ceil(m.cssContentSize ? m.cssContentSize.height : m.contentSize.height);
            const w = width || Math.ceil(m.cssLayoutViewport ? m.cssLayoutViewport.clientWidth : m.layoutViewport.clientWidth);
            await page.viewport(w, Math.min(h, 16000), scale);
            await sleep(250);
          }
          const shot = await page.send("Page.captureScreenshot", Object.assign({ format: "png", captureBeyondViewport: true }, clip ? { clip } : {}));
          fs.mkdirSync(path.dirname(file), { recursive: true });
          fs.writeFileSync(file, Buffer.from(shot.data, "base64"));
          return file;
        },
        close() { try { ws.close(); } catch (e) { /* ignore */ } },
      };
      resolve(page);
    };
  });
}

function fileUrl(p, hash = "") { return "file:///" + path.resolve(p).replace(/\\/g, "/") + (hash ? "#" + hash : ""); }

module.exports = { launch, fileUrl, sleep };
