import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the finished research site", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Climate Twin Frankfurt/);
  assert.match(html, /actually.* warmer/i);
  assert.match(html, /urban heat island/i);
  assert.match(html, /Skip to main content/);
  assert.match(html, /Read the complete daily data table/);
  assert.match(html, /Scientific method/);
  assert.match(html, /block bootstrap/i);
  assert.match(html, /not.* significant|not detected/i);
  assert.match(html, /Provenance/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Starter Project/);
});

test("ships accessible controls and research boundaries", async () => {
  const [page, layout, styles, packageJson] = await Promise.all([
    readFile(new URL("app/page.tsx", root), "utf8"),
    readFile(new URL("app/layout.tsx", root), "utf8"),
    readFile(new URL("app/globals.css", root), "utf8"),
    readFile(new URL("package.json", root), "utf8"),
  ]);
  assert.match(page, /className="skip-link"/);
  assert.match(page, /limitations-first/);
  assert.match(page, /Read this before any/);
  assert.match(styles, /prefers-contrast: more/);
  assert.match(styles, /forced-colors: active/);
  assert.match(styles, /\.nav__links a \{ display: inline-flex; min-height: 44px/);
  assert.match(layout, /Climate Twin Frankfurt/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|drizzle/);
});

test("ships the complete frozen registry into the interactive release", async () => {
  const shipped = JSON.parse(await readFile(new URL("app/data/registry.json", root), "utf8"));
  const frozen = JSON.parse(
    await readFile(
      new URL("../reports/v0.1-climate-twin-frankfurt-registry.json", root),
      "utf8",
    ),
  );
  assert.deepEqual(shipped, frozen);
  assert.equal(shipped.schema_version, 1);
  assert.ok(shipped.period.n_valid_paired_days > 10000);
  assert.equal(typeof shipped.gap.full_period.mean_gap_c, "number");
  assert.equal(typeof shipped.trend.p_value, "number");
});
