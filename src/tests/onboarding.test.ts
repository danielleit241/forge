import assert from "node:assert/strict";
import test from "node:test";
import { inferMigrationSource } from "../core/onboarding.js";

test("migration source prefers the lockfile over detected folders", () => {
  assert.equal(inferMigrationSource("claude", ["codex"]), "claude");
  assert.equal(inferMigrationSource("codex", ["claude"]), "codex");
});

test("migration source uses a single detected agent without a lockfile", () => {
  assert.equal(inferMigrationSource(undefined, ["claude"]), "claude");
  assert.equal(inferMigrationSource(undefined, ["codex"]), "codex");
});

test("migration source remains selectable when detection is ambiguous", () => {
  assert.equal(inferMigrationSource(undefined, []), undefined);
  assert.equal(inferMigrationSource(undefined, ["claude", "codex"]), undefined);
});
