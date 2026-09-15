# Candidate Repair Report: Unit 5 and Grade 8 Blueprint (Candidate v1.2)

**Document Reference:** Formal repair record addressing `Actual-material review 1 — organizer findings`.  
**Run Identity:** Repair Run 20260915  
**Candidate Target:** Grade 8 Public Mathematics Curriculum — Unit 5 (`8.F.B.4`, `8.F.B.5`) and Year-Long Blueprint.  
**Deliverable Status:** Research Candidate v1.2 for external rechecking. (Does not claim human approval, print acceptance, or classroom-verified efficacy).

---

## 1. Item-by-Item Review Investigation and Actual Dispositions

### Issue 1: Graph-Reading Evidence Compromised
- **Review Finding:** In `lesson6_7_8_student_materials.md`, CFU-8 displayed an ASCII graph with misaligned visual point positions (e.g., $(4, 16)$ drawn on the line for 12), allowing students to calculate from printed labels without reading the graph. `TASK-8.1` referred to a "small sketch below" without providing it. `PRAC-8.1` claimed $(20, 235)$ was a "clean grid intersection" despite a vertical grid spacing of 50.
- **Investigation Finding:** Confirmed. The ASCII sketch in CFU-8 could not faithfully represent coordinate lattice points and violated the project constraint requiring self-contained SVG files. `TASK-8.1` lacked a diagram, and `PRAC-8.1` contained an internal contradiction between its stated grid spacing ($\Delta C = 50$) and the point $C = 235$.
- **Actual Changed Files and Task IDs:**
  - `cfu8_snow_graph.svg` *(New Artifact)*: Created a dedicated high-contrast SVG graphic featuring an exact coordinate grid (horizontal: $t \in [0, 16]$ hours, vertical: $S \in [0, 40]$ inches, with grid lines every 2 inches). Marked points $P_0(0, 6)$, $P_1(4, 16)$, $P_2(8, 26)$, and $P_3(12, 36)$ as distinct dots **without printing coordinate numbers**, forcing students to read scales and coordinates directly from the axes.
  - `task8_1_trap_sketch.svg` *(New Artifact)*: Created an SVG graphic illustrating the "counting grid squares" dilemma (2 grid boxes up, 1 grid box right on axes scaled by 50 miles and 5 hours).
  - `lesson6_7_8_student_materials.md`:
    - `TASK-8.1`: Inserted image reference to `task8_1_trap_sketch.svg`.
    - `CFU-8`: Replaced ASCII graph with image reference to `cfu8_snow_graph.svg`; restructured prompts to require reading coordinates of $P_0, P_1, P_2$ from the grid.
    - `PRAC-8` (Item 1): Reconciled text to accurately describe the model as given order data/points ($(0, 75)$ setup fee, $(20, 235)$ order total) rather than an impossible grid intersection.
  - `lesson6_7_8_teacher_guides.md`:
    - `CFU-8`: Updated key and observation guide to reference reading coordinates from `cfu8_snow_graph.svg`.
    - `PRAC-8`: Updated solution text to reflect recorded data formulation.
- **Checks Performed:** Evaluated grid coordinates and slope $m = \frac{16 - 6}{4 - 0} = 2.5\text{ in/hr}$; checked that line endpoints $(80, 366)$ and $(515.2, 60)$ strictly obey $S = 2.5t + 6$.

---

### Issue 2: Given Answers Substituting for Intended Student Work
- **Review Finding:** In `lesson7_reservoir_models.svg`, the legend printed the rates `+15 gal/min` and `-20 gal/min` before `TASK-7.2` asked students to calculate them. Later in `TASK-7.3`, the pre-filled verification questions printed both equations ($V_A = 15(8) + 40$ and $V_B = 320 - 20(8)$), revealing the models prematurely.
- **Investigation Finding:** Confirmed. The legend text and Task 7.3 prompts provided answers that should have been constructed independently by students.
- **Actual Changed Files and Task IDs:**
  - `lesson7_reservoir_models.svg`: Revised legend text from `Tank A (Filling: +15 gal/min)` and `Tank B (Draining: -20 gal/min)` to `Tank A (Filling)` and `Tank B (Draining)`.
  - `lesson6_7_8_student_materials.md`:
    - `TASK-7.3` (Question 3): Replaced pre-filled formulas with: *"Substitute $t = 8$ into your equation for $V_A$: ________"* and *"Substitute $t = 8$ into your equation for $V_B$: ________"*.
  - `lesson6_7_8_teacher_guides.md`:
    - `TASK-7.3`: Aligned teacher key with student prompts.
- **Checks Performed:** Visual inspection of SVG text elements confirms no numerical rates appear in the diagram; student task sheet requires independent equation construction before substitution.

---

### Issue 3: Formatting Failures (KaTeX Errors, Markdown Table Syntax, Response Spaces)
- **Review Finding:** KaTeX 0.18.7 reported 58 rendering failures on the student sheet due to unescaped underscores in constructs like `\text{______}`. The three teacher diagnostic tables contained literal `\n` strings on single lines, corrupting Markdown table rendering. Multi-step tasks lacked adequate writing and calculation spaces.
- **Investigation Finding:** Confirmed. In KaTeX, an unescaped `_` inside math mode or `\text{}` triggers a parse error. The teacher diagnostic tables had escaped newline strings (`\n`) rather than physical newlines. Response areas lacked structured containers.
- **Actual Changed Files and Task IDs:**
  - `lesson6_7_8_student_materials.md`:
    - Replaced all unescaped underscores across all tasks (`TASK-6.1` through `PRAC-8`) with valid Markdown blank lines (`________`) placed outside math delimiters.
    - Added boxed workspace frames (`[ Space for Work / Calculation: ... ]`) and multi-line blank prompts for all explanations and calculations.
    - Included explicit formatting note explaining renderer assumptions (standard Markdown with KaTeX math).
  - `lesson6_7_8_teacher_guides.md`:
    - Converted all literal `\n` occurrences in Section 7 of Lessons 6, 7, and 8 into actual line breaks, creating valid Markdown tables.
  - `probe_tasks_student_and_teacher.md`:
    - Replaced all unescaped underscores in math mode (`\text{______}`) in PROBE-2 and PROBE-3 with clean Markdown blanks.
- **Checks Performed:** Textual regex search confirms zero instances of `\text{___` or unescaped underscores in math mode across all candidate Markdown files. Markdown table syntax parsed and verified.

---

### Issue 4: Resource and Time Commitments Reconciliation
- **Review Finding:** Teacher guide CFU-6 recommended green/orange colored pencils, conflicting with the black-and-white print/pencil classroom condition. A promised two-column difference bracket scaffold was absent. `PRAC-6/7/8` were labeled independent practice without a scheduled place in the 50-minute lesson, and homework cannot be a mandatory gate.
- **Investigation Finding:** Confirmed. Colored pencil recommendations violated the resource constraints. The difference bracket was referenced in teacher text but omitted from student sheets. Practice items lacked explicit curricular status.
- **Actual Changed Files and Task IDs:**
  - `lesson6_7_8_student_materials.md`:
    - Added the printed `Visual Reference Scaffold: Two-Column Difference Bracket Template` directly at the top of Lesson 6.
    - Explicitly labeled PRAC-6, PRAC-7, and PRAC-8 as **"Selectable / Optional Practice Problems"**, clarifying they are optional reinforcement for station rotations, review days, or home study, and not mandatory homework gates.
  - `lesson6_7_8_teacher_guides.md`:
    - Section 2 (Lesson 6): Documented the student-facing difference bracket scaffold.
    - Section 3 (Lessons 6, 7, 8): Added an explicit **"Practice Architecture"** statement explaining how core work is fully contained within the 50-minute period and how PRAC items fit flexibly.
    - Section 7 (Lesson 6 CFU rubric): Replaced colored pencil guidance with pencil circling (for $\Delta C$) and boxing (for $\Delta h$).
- **Checks Performed:** Verified that all materials and teacher facilitation strategies require only black-and-white printing, ordinary pencils, straightedge rulers, grid paper, basic four-function calculators, and a teacher display projector.

---

### Issue 5: Claims and Diagnostics Overreach
- **Review Finding:** Teacher CFU tables claimed "full/complete mastery" from single exit tickets, and the skeleton claimed an "unbreakable representational triad ensures mastery." The verification report claimed all coordinate mappings were independently checked with SymPy, but recorded calls only checked selected expressions.
- **Investigation Finding:** Confirmed. Evaluative claims were overly dogmatic for single 5-minute exit tickets. The verification report overstated the reach of symbolic computation by conflating algebraic checks with diagrammatic reading.
- **Actual Changed Files and Task IDs:**
  - `lesson6_7_8_teacher_guides.md`:
    - Replaced "full/complete mastery" in all diagnostic rubrics (Lessons 6, 7, 8) with calibrated descriptors: *"Demonstrates strong current procedural and conceptual proficiency on the sampled target."*
    - Expanded error diagnoses to offer tentative, multi-cause interpretations (e.g., distinguishing an arithmetic division slip from conceptual variable reversal) with targeted follow-up questions.
  - `unit5_linear_functions_skeleton.md`:
    - Softened Section 4 claim: replaced "unbreakable representational triad... ensuring that students master" with *"a coherent representational progression... providing structured opportunities to explore rate of change and initial value."*
    - Re-calibrated Period 17 description to emphasize sampling specific performance targets.
  - `grade8_curriculum_blueprint.md`:
    - Updated Period 17 summative assessment row from "complete mastery" to an indicator of current proficiency on sampled targets.
    - Calibrated Sections 5.2 and 5.3 to emphasize that mathematical probes verify internal numerical/geometric consistency rather than proving unique lesson orders or guaranteed classroom success.
  - `candidate_design_and_verification_report.md`:
    - Explicitly qualified the epistemic boundary of SymPy checks: verified algebraic relations and pixel-coordinate geometries, but acknowledged that SymPy does not verify student visual perception or instructional efficacy.
- **Checks Performed:** Audited all assessment and narrative text across the workspace to eliminate absolutist claims ("proves," "ensures," "complete mastery").

---

### Issue 6: Mathematical and Semantic Qualifications
- **Review Finding:** The teacher rule "Never count boxes" was too dogmatic (counting intervals multiplied by unit scale is mathematically valid). Graph 8A's initial altitude of 50 m was narrowly assumed to be a rooftop launch without considering timing or reference datum. PRAC-6 battery discharge conflated percentage points with percent change. The skeleton's P13 omitted which quantity was graphed when discussing straight vs. curved motion graphs.
- **Investigation Finding:** Confirmed. All four points represented mathematical or semantic imprecisions.
- **Actual Changed Files and Task IDs:**
  - `lesson6_7_8_student_materials.md`:
    - `TASK-8.2` (Graph 8A Q2): Expanded prompt to consider reference datum and tracking start time.
    - `PRAC-6` (Item 2): Specified that battery discharge rate is measured in **"percentage points per hour"**.
  - `lesson6_7_8_teacher_guides.md`:
    - Lesson 8, Section 4 & Section 6 (`TASK-8.1`): Replaced "Never count boxes" with a qualified rule: *"Counting grid boxes as 1 unit each is an error when axes have non-unit scales. If students count grid intervals, they must multiply the number of intervals by the scale value per interval... Calculating coordinate differences directly ($\Delta y / \Delta x$) is the most direct and reliable method."*
    - Lesson 8, Section 6 (`TASK-8.2` Graph 8A Q2): Qualified that $(0, 50)$ indicates the drone was 50 meters above ground datum when tracking began (launched from an elevation or already in flight).
    - Lesson 6, Section 6 (`PRAC-6` Item 2): Clarified that $-4\%$ represents an absolute decrease of 4 percentage points of full capacity per hour.
  - `unit5_linear_functions_skeleton.md`:
    - Period 13: Explicitly specified the quantity graphed: on a **position-time graph**, steady speed is a straight line and acceleration/braking is curved; on a **speed-time graph**, steady speed is a horizontal line and constant acceleration is a straight line.
- **Checks Performed:** Verified semantic accuracy against standard middle school physics and mathematics conventions.

---

### Issue 7: Upper-Level Blueprint and Probe File Corrections
- **Review Finding:** Patch notes in `upstream_blueprint_corrections.md` were not fully integrated into `grade8_curriculum_blueprint.md`. Probe diagrams contained measurable geometric errors: Probe 1 drawn line endpoints had slope $2.0652$ instead of $2.0$ and printed answers in a summary box; Probe 2 drawn line endpoints had slope $3.0435$ instead of $3.0$.
- **Investigation Finding:** Confirmed. `grade8_curriculum_blueprint.md` still contained outdated resource assumptions and overreaching claims. The drawn line in `probe1_slope_triangles.svg` had endpoints $(80, 459)$ and $(540, 60)$ (slope $\approx 2.0652$); `probe2_water_tank.svg` had endpoints $(80, 360)$ and $(540, 80)$ (slope $\approx 3.0435$).
- **Actual Changed Files and Task IDs:**
  - `grade8_curriculum_blueprint.md`: Directly amended with all candidate patches:
    - Updated classroom context assumptions (strictly black-and-white print, pencils, straightedges, grid paper, ordinary calculators, projector).
    - Replaced Unit 1 transformation tools (tracing paper/transparencies $\to$ coordinate rules and grid-paper constructions).
    - Updated MP5 description to reflect basic ordinary calculators and straightedges.
    - Updated Section 4.1 to establish Unit 5's duration as strictly 18 periods without claiming the annual flex buffer.
    - Updated Section 4.4 (Period 17) and Section 5.2/5.3 to calibrate evaluative and epistemic claims.
  - `probe1_slope_triangles.svg`:
    - Repaired drawn line endpoints to $(80, 459)$ and $(555, 60)$. At $y = 20$ ($y_{px} = 60$), $x = (20 - 1)/2 = 9.5 \implies x_{px} = 80 + 9.5 \times 50 = 555$. Calculated slope: $\frac{19}{9.5} = 2.000$ (exact).
    - Removed the ratio summary box that previously disclosed answers $\Delta y / \Delta x = 2$.
  - `probe2_water_tank.svg`:
    - Repaired drawn line endpoints to $(80, 360)$ and $(546.7, 80)$. At $D = 36$ inches ($y_{px} = 80$), $t = (36 - 8)/3 = 28/3\text{ hr} \implies x_{px} = 80 + \frac{28}{3} \times 50 \approx 546.67$. Calculated slope: $\frac{28}{28/3} = 3.000$ (exact).
  - `probe_tasks_student_and_teacher.md`:
    - Added explicit clarification of document role (design feasibility probes, distinct from live lesson handouts).
    - Fixed unescaped underscores in math mode.
- **Checks Performed:** Engine calculation verified endpoint slopes:
  - Probe 1: `(480 - 60)/21 / ((555 - 80)/50) = 19 / 9.5 = 2.0`
  - Probe 2: `(440 - 80)/10 / ((546.67 - 80)/50) = 28 / (28/3) = 3.0`

---

## 2. Workspace Artifact Inventory (Candidate v1.2)

| Filename | Status in this Run | Primary Changes / Additions |
| :--- | :---: | :--- |
| `grade8_curriculum_blueprint.md` | Revised (v1) | Direct patch integration: resources, pacing buffer, calibrated claims, qualified probe role. |
| `unit5_linear_functions_skeleton.md` | Revised (v1) | P13 motion graph qualification; calibrated representational narrative and assessment scope. |
| `lesson6_7_8_student_materials.md` | Revised (v1) | Fixed 58 KaTeX errors; added SVG references, workspace boxes, difference bracket template; removed pre-filled answers. |
| `lesson6_7_8_teacher_guides.md` | Revised (v1) | Fixed table newlines; calibrated rubrics; qualified box counting; added practice architecture. |
| `lesson7_reservoir_models.svg` | Revised (v1) | Removed rate values from legend to preserve student mathematical construction. |
| `lesson8_scaled_graphs.svg` | Retained (v0) | Verified accurate; high-contrast grayscale with clear major/minor scales and slope triangles. |
| `cfu8_snow_graph.svg` | **New (v1)** | Replaces ASCII graph in CFU-8 with exact vector coordinate grid and unlabelled data points. |
| `task8_1_trap_sketch.svg` | **New (v1)** | Provides the missing visual sketch for TASK-8.1 ("counting squares" dilemma). |
| `probe1_slope_triangles.svg` | Revised (v1) | Repaired line endpoints to exact slope 2.0; removed answer disclosure box. |
| `probe2_water_tank.svg` | Revised (v1) | Repaired line endpoints to exact slope 3.0. |
| `probe_tasks_student_and_teacher.md` | Revised (v1) | Fixed math blanks; clarified document status as design feasibility record. |
| `candidate_design_and_verification_report.md` | Revised (v1) | Complete design rationale, repair integration record, and qualified SymPy checks. |
| `repair-report.md` | **New (v1)** | Comprehensive review disposition, actual changes, checks performed, and limitations. |
| `upstream_blueprint_corrections.md` | Retained (v0) | Preserved historical audit trail of earlier blueprint patch notes. |

---

## 3. Checks Performed

1. **Symbolic and Arithmetic Checks (`SymPy`):**
   - Verified difference quotients, initial values, and equation predictions for Tables 1 and 2, cooling tank, technician charges, reservoir tanks, drone ascent, truck fuel, snow depth, t-shirt costs, and canyon hiker.
   - Evaluated SVG pixel coordinate endpoints for Probe 1 and Probe 2, confirming slopes of exactly $2.000$ and $3.000$.
2. **Syntactic and Formatting Checks:**
   - Full workspace search confirmed zero unescaped underscores in math mode (`\text{___}`).
   - Verified that teacher diagnostic tables parse as standard multi-row Markdown tables without embedded `\n` characters.
   - Verified that all SVG image references (`![...](filename.svg)`) match existing files in the current workspace.
3. **Curricular and Pedagogical Consistency Checks:**
   - Confirmed common Task IDs match between student worksheets and teacher guides (`TASK-6.1` to `PRAC-8`).
   - Verified that all student task sheets contain zero leaked answers, pre-filled formulas, or premature rates.
   - Checked that all tasks adhere strictly to the 28-student, ordinary calculator, black-and-white printing research constraints.

---

## 4. Unaffected Material Retained

- **Year-Long Architecture:** The 9-unit annual sequence, the 160-period instructional budget, and the 20-period strategic reserve buffer in `grade8_curriculum_blueprint.md` remain intact.
- **Core Unit Structure:** The 18-period trajectory, developmental cluster sequence, and essential problem contexts in `unit5_linear_functions_skeleton.md` remain unchanged.
- **Instructional Progression:** The core activities of Lessons 6, 7, and 8 (analyzing irregular tables, reservoir dynamics, and scaled coordinate planes) maintain their planned cognitive flow.

---

## 5. Truthful Unresolved Limitations

1. **No Live Classroom Trial:** All instructional timings (e.g., 50 minutes per period), student misconceptions, and teacher moves are based on mathematical design reasoning and standard middle-grades cognitive research. They have not been validated in an empirical classroom setting.
2. **Physical Layout and Pagination:** While designed for standard 8.5" $\times$ 11" pages, materials exist as Markdown files with separate SVG assets. Exact multi-page pagination and photocopying contrast must be verified on physical hardware prior to classroom use.
3. **Partially Expanded Scope:** Lessons 6, 7, and 8 are fully articulated as complete student and teacher materials. Lessons 1–5 and 9–18 remain articulated at the skeleton/target-evidence level.
