import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
  badgeProgress,
  escapeHtml,
  formatNumber,
  heroStats,
  iconEmoji,
  moreStats,
  nextTierLabel,
  progressFooter,
} from "../../custom_components/mapmesh/www/mapmesh-card-logic.js";

describe("formatNumber", () => {
  it("returns em dash for empty values", () => {
    assert.equal(formatNumber(null), "—");
    assert.equal(formatNumber(undefined), "—");
    assert.equal(formatNumber(""), "—");
  });

  it("formats numbers with locale grouping", () => {
    const formatted = formatNumber(42254);
    assert.notEqual(formatted, "—");
    assert.match(formatted, /42/);
    assert.match(formatted, /254/);
  });
});

describe("badgeProgress", () => {
  it("returns null when value or next is missing", () => {
    assert.equal(badgeProgress(null), null);
    assert.equal(badgeProgress({}), null);
    assert.equal(badgeProgress({ value: 10 }), null);
    assert.equal(badgeProgress({ next: 10 }), null);
  });

  it("allows zero value and clamps to 100", () => {
    assert.equal(badgeProgress({ value: 0, next: 100 }), 0);
    assert.equal(badgeProgress({ value: 150, next: 100 }), 100);
    assert.equal(badgeProgress({ value: 50, next: 100 }), 50);
  });
});

describe("heroStats", () => {
  it("returns Hexes / Samples / Days in order", () => {
    const result = heroStats({
      unique_hexes: 42,
      total_samples: 91,
      active_days: 47,
      pioneer_hexes: 1,
    });
    assert.deepEqual(
      result.map((r) => r.label),
      ["Hexes", "Samples", "Days"]
    );
    assert.deepEqual(
      result.map((r) => r.value),
      [42, 91, 47]
    );
  });

  it("handles missing attrs", () => {
    const result = heroStats(undefined);
    assert.equal(result.length, 3);
    assert.equal(result[0].value, undefined);
  });
});

describe("moreStats", () => {
  it("excludes hero keys and omits missing values", () => {
    const result = moreStats({
      unique_hexes: 1,
      total_samples: 2,
      active_days: 3,
      pioneer_hexes: 10,
      unique_repeaters: 5,
      rx_hexes: null,
      days_since_first: 118,
    });
    const keys = result.map((r) => r.key);
    assert.deepEqual(keys, ["pioneer_hexes", "unique_repeaters", "days_since_first"]);
    assert.ok(!keys.includes("unique_hexes"));
  });
});

describe("iconEmoji", () => {
  it("maps known icons and falls back", () => {
    assert.equal(iconEmoji("map"), "🗺️");
    assert.equal(iconEmoji("fire"), "🔥");
    assert.equal(iconEmoji("chart"), "📊");
    assert.equal(iconEmoji("unknown"), "🏅");
    assert.equal(iconEmoji(""), "🏅");
    assert.equal(iconEmoji(undefined), "🏅");
  });
});

describe("nextTierLabel / progressFooter", () => {
  it("infers next tier label", () => {
    assert.equal(nextTierLabel("gold"), "Platinum");
    assert.equal(nextTierLabel("bronze"), "Silver");
    assert.equal(nextTierLabel("diamond"), null);
    assert.equal(nextTierLabel(undefined), null);
  });

  it("builds footer with and without next", () => {
    const withNext = progressFooter({
      value: 42254,
      next: 75000,
      tier: "gold",
    });
    assert.ok(withNext);
    assert.match(withNext.current, /42/);
    assert.match(withNext.goal, /75/);
    assert.match(withNext.goal, /Platinum/);

    const valueOnly = progressFooter({ value: 10 });
    assert.deepEqual(valueOnly, { current: formatNumber(10), goal: null });

    assert.equal(progressFooter({}), null);
    assert.equal(progressFooter({ tier: "special" }), null);
  });
});

describe("escapeHtml", () => {
  it("escapes markup characters", () => {
    assert.equal(escapeHtml(`<b>"x"&'y'</b>`), "&lt;b&gt;&quot;x&quot;&amp;&#39;y&#39;&lt;/b&gt;");
  });
});
