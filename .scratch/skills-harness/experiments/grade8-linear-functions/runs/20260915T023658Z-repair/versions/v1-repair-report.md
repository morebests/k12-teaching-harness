# Candidate Repair Report: Unit 5 and Grade 8 Blueprint (Candidate v1.3)

**Document Reference:** Formal repair record addressing `Actual-material review 1 — organizer findings` and `Remaining formatting repair v0.1`.  
**Run Identity:** Repair Run 20260915 (Pass 2)  
**Candidate Target:** Grade 8 Public Mathematics Curriculum — Unit 5 (`8.F.B.4`, `8.F.B.5`) and Year-Long Blueprint.  
**Deliverable Status:** Research Candidate v1.3 for external rechecking. (Does not claim human approval, print acceptance, or classroom-verified efficacy).

---

## 1. Item-by-Item Review Investigation and Dispositions (Pass 1 — Candidate v1.2 Foundation)

### Issue 1: Graph-Reading Evidence Compromised
- **Review Finding:** In `lesson6_7_8_student_materials.md`, CFU-8 displayed an ASCII graph with misaligned visual point positions (e.g., $(4, 16)$ drawn on the line for 12), allowing students to calculate from printed labels without reading the graph. `TASK-8.1` referred to a "small sketch below" without providing it. `PRAC-8.1` claimed $(20, 235)$ was a "clean grid intersection" despite a vertical grid spacing of 50.
- **Investigation Finding:** Confirmed. The ASCII sketch in CFU-8 could not faithfully represent coordinate lattice points and violated the project constraint requiring self-contained SVG files. `TASK-8.1` lacked a diagram, and `PRAC-8.1` contained an internal contradiction between its stated grid spacing ($\Delta C = 50$) and the point $C = 235$.
- **Actual Changed Files and Task IDs:**
  - `cfu8_snow_graph.svg` *(New Artifact)*: Created a dedicated high-contrast SVG graphic featuring an exact coordinate grid (horizontal: $t \in [0, 16]$ hours, vertical: $S \in [0, 40]$ inches, with grid lines every 2 inches). Marked points $P_0(0, 6)$, $P_1(4, 16)$, $P_2(8, 26)$, and $P_3(12, 36)$ as distinct dots without printing coordinate numbers, requiring students to read scales and coordinates directly from the axes.
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

### Issue 3: Formatting Failures in Pass 1
- **Review Finding:** KaTeX 0.18.7 reported 58 rendering failures on the student sheet due to unescaped underscores in constructs like `\text{______}`. The three teacher diagnostic tables contained literal `\n` strings on single lines, corrupting Markdown table rendering. Multi-step tasks lacked adequate writing and calculation spaces.
- **Investigation Finding:** Confirmed. In KaTeX, an unescaped `_` inside math mode or `\text{}` triggers a parse error. The teacher diagnostic tables had escaped newline strings (`\n`) rather than physical newlines. Response areas lacked structured containers.
- **Actual Changed Files and Task IDs (Pass 1):**
  - `lesson6_7_8_student_materials.md`: Converted majority of math-mode blanks to outside math delimiters; added boxed workspace frames; added layout note.
  - `lesson6_7_8_teacher_guides.md`: Converted literal `\n` tokens in diagnostic tables into actual newlines.
- **Correction of Pass 1 Assertion:** The previous repair report claimed: *"Full workspace search confirmed zero unescaped underscores in math mode."* That statement was inaccurate. In fact, 22 unescaped underscore instances in math blocks persisted into Candidate v1.2 because they were wrapped inside math display/inline tags (e.g., `$$\text{Rate } = \text{________ gallons per minute}$$`), and the `check_rendering` tool had not yet been executed in that run. This is comprehensively resolved in Pass 2 below.

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
    - Expanded error diagnoses to offer tentative, multi-cause interpretations with targeted follow-up questions.
  - `unit5_linear_functions_skeleton.md`:
    - Softened Section 4 claim: replaced "unbreakable representational triad... ensuring that students master" with *"a coherent representational progression... providing structured opportunities to explore rate of change and initial value."*
    - Re-calibrated Period 17 description to emphasize sampling specific performance targets.
  - `grade8_curriculum_blueprint.md`:
    - Updated Period 17 summative assessment row from "complete mastery" to an indicator of current proficiency on sampled targets.
    - Calibrated Sections 5.2 and 5.3 to emphasize that mathematical probes verify internal numerical/geometric consistency rather than proving unique lesson orders or guaranteed classroom success.
  - `candidate_design_and_verification_report.md`:
    - Explicitly qualified the epistemic boundary of SymPy checks: verified algebraic relations and pixel-coordinate geometries, but acknowledged that SymPy does not verify student visual perception or instructional efficacy.

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

---

### Issue 7: Upper-Level Blueprint and Probe File Corrections
- **Review Finding:** Patch notes in `upstream_blueprint_corrections.md` were not fully integrated into `grade8_curriculum_blueprint.md`. Probe diagrams contained measurable geometric errors: Probe 1 drawn line endpoints had slope $2.0652$ instead of $2.0$ and printed answers in a summary box; Probe 2 drawn line endpoints had slope $3.0435$ instead of $3.0$.
- **Investigation Finding:** Confirmed. `grade8_curriculum_blueprint.md` still contained outdated resource assumptions and overreaching claims. The drawn line in `probe1_slope_triangles.svg` had endpoints $(80, 459)$ and $(540, 60)$ (slope $\approx 2.0652$); `probe2_water_tank.svg` had endpoints $(80, 360)$ and $(540, 80)$ (slope $\approx 3.0435$).
- **Actual Changed Files and Task IDs:**
  - `grade8_curriculum_blueprint.md`: Directly amended with all candidate patches.
  - `probe1_slope_triangles.svg`: Repaired drawn line endpoints to $(80, 459)$ and $(555, 60)$ ($m = 2.000$ exact); removed answer summary box.
  - `probe2_water_tank.svg`: Repaired drawn line endpoints to $(80, 360)$ and $(546.7, 80)$ ($m = 3.000$ exact).
  - `probe_tasks_student_and_teacher.md`: Added explicit clarification of document role; adjusted math blanks.

---

## 2. Second Repair Pass (Pass 2 — Candidate v1.3 Refinements)

### Issue 8: KaTeX Parser Failures in Student Sheet and Probes
- **Review Finding:** The student sheet in Candidate v1.2 had 22 KaTeX parse errors due to unescaped underscores inside math text environments (`\text{________ ...}`). Teacher guides had zero parser errors.
- **Investigation Finding:** Confirmed via real execution of `check_rendering` on `lesson6_7_8_student_materials.md`. KaTeX 0.18.7 reported 22 errors, all stemming from `\text{________}` or `\$\text{________}` inside display math blocks `$$ ... $$` or inline `$ ... $`. Additionally, `probe_tasks_student_and_teacher.md` contained 2 similar unescaped underscore expressions in PROBE-2.
- **Actual Changed Files and Expressions:**
  - `lesson6_7_8_student_materials.md`: Corrected all 22 failing expressions by moving the response blank lines (`________`) completely outside math delimiters:
    1. TASK-6.3 Q1: `$$\text{Rate } = \text{________ gallons per minute}$$` $\implies$ `Rate = ________________________ gallons per minute`
    2. TASK-6.3 Q2: `$$\text{Rate } = \text{________ gallons per minute}$$` $\implies$ `Rate = ________________________ gallons per minute`
    3. TASK-6.3 Q4: `$$\text{Initial Volume } b = \text{________ gallons}$$` $\implies$ `Initial Volume $b =$ ________________________ gallons`
    4. CFU-6 Q1: `$$m = \text{________ dollars per hour}$$` $\implies$ `$m =$ ________________________ dollars per hour`
    5. CFU-6 Q2: `$$b = \$\text{________}$$` $\implies$ `$b =$ ________________________ dollars`
    6. CFU-6 Q3: `$$C = \text{________________________}$$` $\implies$ `$C =$ ________________________`
    7. CFU-6 Q4: `$$\text{Total Charge} = \$\text{________}$$` $\implies$ `Total Charge = ________________________ dollars`
    8. TASK-7.2 Part 1 Q2: `$$m_A = \frac{\Delta V}{\Delta t} = \text{________ gallons per minute}$$` $\implies$ `$m_A = \frac{\Delta V}{\Delta t} =$ ________________________ gallons per minute`
    9. TASK-7.2 Part 1 Q3: `$$V_A = \text{________________________}$$` $\implies$ `$V_A =$ ________________________`
    10. TASK-7.2 Part 2 Q5: `$$m_B = \frac{\Delta V}{\Delta t} = \text{________ gallons per minute}$$` $\implies$ `$m_B = \frac{\Delta V}{\Delta t} =$ ________________________ gallons per minute`
    11. TASK-7.2 Part 2 Q6: `$$V_B = \text{________________________}$$` $\implies$ `$V_B =$ ________________________`
    12. CFU-7 Q1: `$$\text{Rate of change } m = \text{________________________}$$` $\implies$ `Rate of change $m =$ ________________________`
    13. CFU-7 Q2: `$$b = \text{________ gallons}$$` $\implies$ `$b =$ ________________________ gallons`
    14. CFU-7 Q3: `$$V = \text{________________________}$$` $\implies$ `$V =$ ________________________`
    15. TASK-8.2 Part 1 Q3: `$$m = \frac{\Delta A}{\Delta t} = \text{________ meters per minute}$$` $\implies$ `$m = \frac{\Delta A}{\Delta t} =$ ________________________ meters per minute`
    16. TASK-8.2 Part 1 Q4: `$$A = \text{________________________}$$` $\implies$ `$A =$ ________________________`
    17. TASK-8.2 Part 1 Q4: `$$A(11) = \text{________ meters}$$` $\implies$ `$A(11) =$ ________________________ meters`
    18. TASK-8.2 Part 2 Q3: `$$m = \frac{\Delta F}{\Delta d} = \text{________ gallons per mile}$$` $\implies$ `$m = \frac{\Delta F}{\Delta d} =$ ________________________ gallons per mile`
    19. TASK-8.2 Part 2 Q4: `$$F = \text{________________________}$$` $\implies$ `$F =$ ________________________`
    20. CFU-8 Q3: `$$S = \text{________________________}$$` $\implies$ `$S =$ ________________________`
    21. CFU-8 Q4: `$$\text{Depth after 15 hours} = \text{________ inches}$$` $\implies$ `Depth after 15 hours = ________________________ inches`
    22. PRAC-8 Item 1: `Total Cost = $\$\text{________}$` $\implies$ `Total Cost = ________________________ dollars`
  - `probe_tasks_student_and_teacher.md`: Corrected the 2 expressions in PROBE-2:
    - PROBE-2 Q2: `$$\text{Rate of Change } m = \frac{\Delta D}{\Delta t} = \text{________ inches per hour}$$` $\implies$ `Rate of Change $m = \frac{\Delta D}{\Delta t} =$ ________________________ inches per hour`
    - PROBE-2 Q4: `$$D = \text{________________________}$$` $\implies$ `$D =$ ________________________`
- **Checks Performed:** Executed `check_rendering` on both modified files. Result: Both returned `math_errors: []` with KaTeX 0.18.7.
- **Epistemic Qualification:** Zero parser errors demonstrates that the KaTeX engine can parse all mathematical expressions without syntax failure. It does **not** signify that physical printed sheets have been accepted or tested on physical printing hardware.

---

### Issue 9: Calibrating CFU-6 Diagnostic Rubric
- **Review Finding:** In `lesson6_7_8_teacher_guides.md`, CFU-6's diagnostic table still labeled single incorrect answers as a "persistent misconception" or a "relapsing habit."
- **Investigation Finding:** Confirmed. Attributing a single incorrect calculation on an exit ticket to an entrenched student trait is an over-interpretation. Formative assessment requires treating an error as a possible interpretation to be confirmed through follow-up probing.
- **Actual Changed Files and Content:**
  - `lesson6_7_8_teacher_guides.md` (Section 7, Lesson 6 Rubric):
    - Row 2 (writes $C = 9h + 57$): Changed state description to: *"Possible Interpretation: Student has procedural grasp of rate, but may have assumed the first listed row is the vertical intercept, or copied the first value without checking whether $h = 0$. (A single response does not prove a permanent conceptual deficit)."* Added explicit confirming prompt: *"What is the value of $h$ in the first row? Does $h = 0$? How much did cost grow during those first 4 hours before the recorded point?"*
    - Row 3 (computes $m = 45$): Changed state description to: *"Possible Interpretation: Student may be attending only to the change in cost ($\Delta C$), possibly carrying over habits from consecutive tables ($\Delta x = 1$), or may have overlooked the time column during subtraction."* Added explicit confirming prompt: *"How many hours did it take for the fee to increase by $\$45$? What is the rate per 1 single hour?"*
    - Row 4 (inverts rate): Framed as a possible interpretation between ratio orientation confusion versus accidental keying order slip in division, with teacher follow-up prompt.
    - All numerical keys ($m = 9$, $b = 21$, $C = 9h + 21$, $\$93$) and pencil circling/boxing interventions were strictly preserved.
- **Checks Performed:** Verified that `lesson6_7_8_teacher_guides.md` renders with zero math errors and maintains valid Markdown table syntax.

---

### Issue 10: Correction of Sweeping Workspace Assertions and Verification Claims
- **Review Finding:** The previous report asserted “Full workspace search confirmed zero unescaped underscores” and made sweeping statements like “zero pre-filled formulas” and “all checked” without documenting the actual execution results. Deliberate worked examples were conflated with unaided construction.
- **Investigation Finding:** Confirmed. The claim of a full workspace search was unjustified because tool checks had not been run on student materials, and sweeping assertions overstated the evidential scope.
- **Actual Changed Files and Corrections:**
  - `repair-report.md` (Section 1.3 & Section 3): Retracted the previous assertion of zero unescaped underscores. Documented that 22 instances persisted in Candidate v1.2, identified their exact lines, and confirmed their resolution in Candidate v1.3 using `check_rendering`.
  - `candidate_design_and_verification_report.md`:
    - Replaced sweeping "all checked" claims with an itemized table listing every mathematical task and geometric SVG coordinate evaluated with SymPy, alongside the specific verification output.
    - Clarified the pedagogical role of scaffolding: instructional organizers (e.g., difference bracket template, guided prompts) reduce cognitive friction to facilitate initial learning, but student work on scaffolded tasks represents supported learning rather than evidence of unaided construct mastery.
- **Checks Performed:** Confirmed that all recorded verification claims in Section 3 of both reports correspond strictly to expressions actually computed or parsed.

---

## 3. Workspace Artifact Inventory (Candidate v1.3)

| Filename | Status in this Run | Primary Changes / Additions |
| :--- | :---: | :--- |
| `lesson6_7_8_student_materials.md` | Revised (v2) | Fixed all 22 KaTeX unescaped underscore parse errors; confirmed zero errors via `check_rendering`. |
| `lesson6_7_8_teacher_guides.md` | Revised (v2) | Re-calibrated CFU-6 diagnostic table (tentative interpretations + confirming questions); confirmed zero errors. |
| `probe_tasks_student_and_teacher.md` | Revised (v2) | Fixed 2 KaTeX unescaped underscore parse errors in PROBE-2; confirmed zero errors via `check_rendering`. |
| `candidate_design_and_verification_report.md` | Revised (v2) | Updated to Candidate v1.3; documented tool checks and calibrated scaffolding/syntax boundaries. |
| `repair-report.md` | Revised (v2) | Complete multi-pass repair record; appended Pass 2 findings; retracted inaccurate v1.2 assertion. |
| `lesson7_reservoir_models.svg` | Retained (v1) | Legend rates removed; preserved student construction. |
| `lesson8_scaled_graphs.svg` | Retained (v0) | Verified accurate scaled coordinate diagrams. |
| `cfu8_snow_graph.svg` | Retained (v1) | High-contrast vector coordinate grid with unlabelled points for authentic graph reading. |
| `task8_1_trap_sketch.svg` | Retained (v1) | Vector sketch illustrating the "counting grid squares" dilemma. |
| `probe1_slope_triangles.svg` | Retained (v1) | Corrected endpoints ($m = 2.000$ exact); answer box removed. |
| `probe2_water_tank.svg` | Retained (v1) | Corrected endpoints ($m = 3.000$ exact). |
| `grade8_curriculum_blueprint.md` | Retained (v1) | Candidate v1.1 patch fully integrated. |
| `unit5_linear_functions_skeleton.md` | Retained (v1) | Candidate v1.2 skeleton fully aligned. |
| `upstream_blueprint_corrections.md` | Retained (v0) | Historical record of initial patch specifications. |

---

## 4. Checks Performed

1. **KaTeX Syntax Rendering (`check_rendering`):**
   - `lesson6_7_8_student_materials.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `lesson6_7_8_teacher_guides.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `probe_tasks_student_and_teacher.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `candidate_design_and_verification_report.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `unit5_linear_functions_skeleton.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `grade8_curriculum_blueprint.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
   - `repair-report.md`: Evaluated with KaTeX 0.18.7 $\implies$ `math_errors: []` (0 errors).
2. **Symbolic and Arithmetic Checks (`SymPy`):**
   - Re-verified calculations for Table 2 ($m = 4, b = 3$), cooling tank ($m = -6, b = 180, t = 30$), technician charges ($m = 9, b = 21$), Tank A ($m = 15, b = 40$), Tank B ($m = -20, b = 320$), shared intersection $(8, 160)$, filtration pool ($m = -24, b = 450, t = 18.75$), drone ascent ($m = 25, b = 50$), truck fuel ($m = -0.1, b = 24$), snow depth ($m = 2.5, b = 6$), Probe 1 ($m = 2.000$), and Probe 2 ($m = 3.000$).
3. **Curricular Consistency and Alignment:**
   - Verified that Task IDs correspond across student sheets, teacher guides, and reports (`TASK-6.1` to `PRAC-8`).
   - Verified that all student task sheets contain designated response blanks and boxed calculation containers without pre-filled answers.
   - Verified that all tasks respect research constraints (28 students, ordinary calculators, black-and-white printing, no 1:1 connected devices).

---

## 5. Unaffected Material Retained

- **Year-Long Blueprint Architecture:** The 9-unit annual sequence, the 160-period instructional budget, and the 20-period strategic reserve buffer in `grade8_curriculum_blueprint.md` remain intact.
- **Skeleton Structure:** The 18-period trajectory and developmental cluster sequence in `unit5_linear_functions_skeleton.md` remain unchanged.
- **Instructional Progression:** Lessons 6, 7, and 8 maintain their planned representational progression (Table $\to$ Context $\to$ Scaled Graph).

---

## 6. Truthful Unresolved Limitations

1. **Syntax vs. Print Layout:** Achieving zero KaTeX math errors confirms mathematical text parseability in web/HTML environments. It does not verify physical page-break placement, visual contrast on office photocopiers, or margin boundaries for double-sided 8.5" $\times$ 11" printing.
2. **Partially Expanded Envelope:** Lessons 6, 7, and 8 are fully expanded into student and teacher deliverables. Lessons 1–5 and 9–18 remain articulated at the skeleton/target-evidence level.
3. **Absence of Classroom Trials:** Pacing feasibility within 50 minutes, student engagement, and diagnostic efficacy represent reasoned design judgments that have not undergone empirical classroom validation with live 28-student cohorts.
