// Adapt pytest-cov's JSON (coverage/pytest-cov.json) to the istanbul-shaped
// coverage/coverage-summary.json that check-coverage-ratchet.mjs consumes.
// pytest-cov reports statements/lines and (with --cov-branch) branches; it does
// not measure "functions", so we mirror the line percentage for that metric.
import { readFileSync, writeFileSync } from "node:fs";

const src = "coverage/pytest-cov.json";
const totals = JSON.parse(readFileSync(src, "utf8")).totals;
const lines = totals.percent_covered;
const statements = totals.percent_statements_covered ?? lines;
const branches = totals.percent_branches_covered ?? lines;

const summary = {
  total: {
    lines: { pct: lines },
    statements: { pct: statements },
    functions: { pct: lines }, // pytest-cov has no function metric; mirror lines
    branches: { pct: branches },
  },
};
writeFileSync("coverage/coverage-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
console.log(
  `cov-adapt: lines ${lines.toFixed(1)}% statements ${statements.toFixed(1)}% branches ${branches.toFixed(1)}%`,
);
