// Git pre-commit hook (deterministic inner loop) — Python/Docker stack (ADR-0001).
// Fast, staged-scope checks only; the full pytest battery runs in the container
// at the gate and in CI (`docker compose run --rm app pytest`).
//
//   1. block committing real env files / obvious secrets
//   2. ruff on staged Python files IF ruff is on PATH (best-effort, dev convenience)
//   3. traceability validator (fast, pure file parsing)
//   4. trajectory process audit (warns only by default)
import { execSync } from "node:child_process";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });
const capture = (cmd) => execSync(cmd, { encoding: "utf8" }).trim();
const has = (bin) => {
  try { execSync(`command -v ${bin}`, { stdio: "ignore" }); return true; } catch { return false; }
};

const staged = capture("git diff --cached --name-only --diff-filter=ACM")
  .split("\n")
  .filter(Boolean);

// 1 — secret hygiene
const envViolations = staged.filter((f) => /(^|\/)\.env(\.|$)/.test(f) && !f.endsWith(".example"));
if (envViolations.length) {
  console.error(`pre-commit: refusing to commit env file(s): ${envViolations.join(", ")}`);
  process.exit(1);
}
const SECRET_PATTERNS = [
  /-----BEGIN (RSA |EC )?PRIVATE KEY-----/,
  /\b(sk|rk|re|ghp|gho|xox[bap])_[A-Za-z0-9]{16,}\b/,
  /\bAKIA[0-9A-Z]{16}\b/,
  /postgres(ql)?:\/\/[^\s'"]+:[^\s'"]+@/,
];
for (const file of staged) {
  if (/\.(png|webm|jpg|jpeg|gif|pdf|ico|woff2?)$/.test(file)) continue;
  let content = "";
  try {
    content = capture(`git show :"${file}"`);
  } catch {
    continue;
  }
  for (const pattern of SECRET_PATTERNS) {
    if (pattern.test(content)) {
      console.error(`pre-commit: possible secret in ${file} (pattern ${pattern}). Use env vars; bypass only with an explicit allowlist edit to this hook.`);
      process.exit(1);
    }
  }
}

// 2 — lint staged Python (best-effort: only if ruff is installed on the host).
// The canonical lint runs in the container; this is a fast local guard.
const pyStaged = staged.filter((f) => f.endsWith(".py"));
if (pyStaged.length && has("ruff")) {
  run(`ruff check ${pyStaged.map((f) => `"${f}"`).join(" ")}`);
}

// 3 — traceability (fails on broken FR chain / archived-but-unchecked tasks).
// Regenerates the report + trace graph; stage them so the commit carries the
// fresh versions (otherwise CI --check-fresh fails on staleness).
run("node scripts/check-traceability.mjs");
run('git add docs/qa/traceability-report.md trace/trace.json');

// 4 — trajectory (process audit). Warns only by default; regenerates + stages
// its report so CI --check-fresh stays green.
run("node scripts/check-trajectory.mjs");
run('git add docs/qa/trajectory-report.md trace/trajectory.json');

console.log("pre-commit: all deterministic checks passed");
