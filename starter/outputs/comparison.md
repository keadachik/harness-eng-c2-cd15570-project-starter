# Compare the Four Runs

Shared EDA question (all four prompt-file runs):

> What patterns and trade-offs in performance, price, vehicle condition, and ownership costs appear in the dealership's inventory and vehicle-history data?

Evidence below is from the saved prompt-run artifacts under `outputs/<loop>/prompt/` (plus related plots). This describes what those runs produced, not what the harness is intended to do.

---

## Loop 01 — Non-production (baseline)

**Added control:** Plan approval before planned data analysis (user framing: plan-approval baseline).

**Evidence:**
- `outputs/non-production/prompt/tool_trace.json`
- `outputs/non-production/prompt/answer.md`
- (interactive companion, separate rubric item) `outputs/non-production/interactive/{answer.md,tool_trace.json}`

Concrete trace sequence: `load_skill` → `write_plan` → `request_approval` → `plan_approval` with `decision: "approved"` / `status: "approved"` → first EDA tool `dataset_info`. No `antidote`, no `permission_check` / `permission_grant`, and no `retrospective_evaluation.json` in this loop’s prompt outputs.

**Observed effect on the shared EDA question:** After approval, the run called registered EDA tools (`dataset_info`, `sample_rows`, `describe_numeric`, `value_counts`, `hypothesis_test`, three `plot_data` calls) and returned an answer on inventory vs history patterns (e.g. New vs Used price test, horsepower–price scatter, segment repair-cost bars). Charts were saved under `outputs/plots/` (e.g. `vehicle_plot_20261103_064534_770863.png`) but the answer notes charts were not visually inspected—numeric tool summaries only. This is the baseline: analysis gated by plan approval, without retrospective JSON, hooks, or scoped grants.

---

## Loop 02 — Self-evaluation

**Added control:** Retrospective structured review after the primary task (user framing: retrospective JSON).

**Evidence:**
- `outputs/self-evaluation/prompt/answer.md`
- `outputs/self-evaluation/prompt/tool_trace.json`
- `outputs/self-evaluation/prompt/retrospective_evaluation.json` (Loop 02–only artifact)

Primary-task trace still shows plan approval then EDA tools (`dataset_info` … `plot_data`); it does not embed the retrospective. The separate evaluation file was produced with outer keys `task_status`, `efficiency_score`, `critique`, `systemic_failure_root_cause`, `workflow_adjustments`. Observed values: `task_status: "SUCCESS"`, `efficiency_score: 1.0`, `critique` notes efficient plan-following and numeric evidence in the summary, `systemic_failure_root_cause: "none"`, `workflow_adjustments: "none"`.

**Observed effect on the shared EDA question:** The primary answer still addresses the same inventory/history trade-offs (price/mileage/HP summaries, New vs Used test, horsepower–price association, repair cost by powertrain). The new control did not rewrite the EDA findings in this run; it added a post-task judgment of execution quality and efficiency. Relative to Loop 01: same style of analysis path plus a review artifact that Loop 01 lacks.

---

## Loop 03 — Hooks

**Added control:** Pre-tool hooks plus post-chart plot-evidence antidote (user framing: hooks + plot-evidence antidote).

**Evidence:**
- `outputs/hooks/prompt/answer.md`
- `outputs/hooks/prompt/tool_trace.json`
- Related plots cited by the trace: `outputs/plots/vehicle_plot_20261102_220308_930161.png` (inventory horsepower vs price scatter), `outputs/plots/vehicle_plot_20261102_220310_626212.png` (history repair cost by powertrain bar)

Pre-tool: multiple entries with `status: "continued"` before the matching completed call (e.g. `load_skill`, `write_plan`, `dataset_info`, `plot_data`). Post-chart: two entries with `antidote: "plot-evidence"` after successful `plot_data`:
1. Scatter antidote: `pearson_correlation: 0.7076`, `x_range: [178.0, 390.0]`, `y_range: [14128.0, 60661.0]`, `point_count: 240`, population `"full dataset"`.
2. Bar antidote: `grouped_means` for powertrain repair cost — Plug-in Hybrid `673.67`, Gasoline `607.17`, Electric `529.75`, Hybrid `456.5`.

**Observed effect on the shared EDA question:** The answer grounds chart claims in those antidote numbers (e.g. “strong positive correlation (r=0.708)”, repair averages ≈ $674 / $607 / $530 / $457 by powertrain). Compared with Loops 01/02, chart interpretation is tied to deterministic post-plot evidence rather than tool path strings alone. Pre-tool `continued` markers show the hook path ran for allowed calls on this prompt’s valid chart requests.

**Antidote → answer pairing (observed):**

| Antidote value | Answer text |
|---|---|
| `pearson_correlation: 0.7076` | “strong positive correlation (r=0.708)” |
| Plug-in Hybrid mean `673.67` | “Plug-in Hybrid: $674” |
| Gasoline `607.17` | “Gasoline: $607” |
| Electric `529.75` | “Electric: $530” |
| Hybrid `456.5` | “Hybrid: $457” |

---

## Loop 04 — Permissions

**Added control:** Policy checks with approval + one-exact-call grants for non-readonly tools (user framing: `require_approval`×3 + `grant`×3 for non-readonly).

**Evidence:**
- `outputs/permissions/prompt/answer.md`
- `outputs/permissions/prompt/tool_trace.json`
- Related plots after grants: `outputs/plots/vehicle_plot_20261103_062655_498878.png`, `outputs/plots/vehicle_plot_20261103_062704_149161.png`

Read-only path: `permission_check` entries with `decision: "allow"` for tools such as `load_skill`, `write_plan`, `dataset_info`, `describe_numeric`, `value_counts`, `hypothesis_test`.

Protected path (exactly three `require_approval` and three matching `event: "grant"` / `scope: "one_exact_call"`; no `decision: "deny"` on this happy-path run):

1. `plot_data` scatter (inventory horsepower vs price) — `permission_check` `require_approval` → status `blocked` → `permission_grant` `grant` with the same `input` → later `allow` (`reason: "one-time grant consumed"`) → completed.
2. `plot_data` bar (history repair cost by segment) — same require → blocked → grant → allow → completed pattern with matching `input`.
3. `rank_inventory` (equal weights on horsepower, price, mileage, reliability, repair cost; `limit: 20`) — same require → blocked → grant → allow → completed pattern with matching `input`.

**Observed effect on the shared EDA question:** EDA still covers structure, numeric summaries, New vs Used price test, charts, and ranking, but non-readonly chart/rank steps only completed after per-call grants. Ranking appears as a weighted sensitivity over inventory rows (“balanced sensitivity to performance and economics”), and the answer states the analysis does not recommend specific purchases. Versus Loop 03: hooks/`continued`/`plot-evidence` are not the distinguishing control here; human-scoped grants gate `plot_data` and `rank_inventory`.

---

## Cross-loop summary

| Loop | Added control | Decisive evidence | Observed effect on shared EDA question |
|---|---|---|---|
| 01 | Plan approval only | `plan_approval` approved before first `dataset_info` in `non-production/prompt/tool_trace.json` | Baseline answer from approved plan + EDA tools; no retrospective / hooks / grants |
| 02 | Retrospective JSON after primary task | `self-evaluation/prompt/retrospective_evaluation.json` (`SUCCESS`, `efficiency_score: 1.0`, five required keys) | Same-style EDA answer plus post-hoc execution review; review did not replace the findings |
| 03 | Hooks + plot-evidence antidote | `status: "continued"` pre-tool; `antidote: "plot-evidence"` with correlation / grouped means; answer cites r≈0.708 and powertrain means | Chart claims grounded in antidote numerics for the shared trade-off question |
| 04 | Non-readonly require_approval + grant (×3 each) | Three `require_approval` / three `event: "grant"` pairs for two `plot_data` + one `rank_inventory`; readonly `allow` | Protected chart/rank steps run only after exact-call grants; ranking framed as analysis, not a purchase recommendation |
