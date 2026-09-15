# Grade 8 Unit 5: Partially Expanded Unit Candidate (Candidate v1.3 — Repaired)
## Design Rationale, Verification Report, and Review Repair Integration

**Authoring Environment:** Bounded Mathematical Design Task B  
**Target Course:** Grade 8 Mathematics (US Public School Curriculum)  
**Target Unit:** Unit 5: Linear Functions and Contextual Modeling  
**Primary Targeted Standards:** CCSS-M **8.F.B.4** and **8.F.B.5**  
**Candidate Delivery Status:** **Partially Expanded Unit Candidate (Candidate v1.3)**. Lessons 6, 7, and 8 are fully expanded into usable student task sheets and scripted teacher guides; Lessons 1–5 and 9–18 are articulated at the target-evidence skeleton level. This document does not claim complete unit expansion, nor does it claim human approval, physical print acceptance, or classroom-verified efficacy.

---

## 1. Multi-Pass Review Reconciliation and Repair Record

### 1.1 Review Pass 1 Repairs (Candidate v1.2 Foundation)
In response to "Actual-material review 1 — organizer findings," the following core structural repairs were established:
1. **Graph-Reading Evidence and Geometric Consistency:**
   - *CFU-8 Graph:* Replaced the problematic ASCII sketch with an authentic, self-contained SVG graphic (`cfu8_snow_graph.svg`). The graph features exact grid lines every 2 inches vertically and 2 hours horizontally, with points marked ($P_0, P_1, P_2, P_3$) without coordinate labels. Students must read the scales directly from the axes, ensuring that successful calculation is genuine evidence of graph-reading proficiency.
   - *TASK-8.1 Diagram:* Provided the previously missing sketch as a self-contained SVG graphic (`task8_1_trap_sketch.svg`), illustrating the "counting grid squares" dilemma ($2\text{ boxes up} / 1\text{ box right} \implies 2\text{ vs. } 20\text{ mph}$).
   - *PRAC-8.1 Text:* Resolved the contradiction where $(20, 235)$ was described as a clean grid intersection on a grid spaced by 50. The problem is now described accurately as recorded order data/points for an algebraic model.
2. **Preserving Student Mathematical Work:**
   - *Legend Rates:* Removed explicit rate values ($+15\text{ gal/min}$, $-20\text{ gal/min}$) from the student-facing legend in `lesson7_reservoir_models.svg`.
   - *Pre-filled Formulas:* Removed pre-filled algebraic equations in TASK-7.3 question 3, requiring students to substitute $t = 8$ directly into their own constructed equations.
3. **Resource and Time Reconciliations:**
   - *Classroom Materials:* Replaced colored-pencil guidance in CFU-6 with standard pencil techniques (circling $\Delta C$, boxing $\Delta h$).
   - *Visual Scaffold:* Added the printed Two-Column Difference Bracket Template directly onto the Lesson 6 student sheet.
   - *Practice Structure:* Clearly designated PRAC-6, PRAC-7, and PRAC-8 as selectable/optional practice (for station differentiation or optional study), preserving the integrity of the 50-minute core lesson.
4. **Semantic and Mathematical Qualifications:**
   - Qualified the "Never count boxes" rule: counting intervals is valid only when multiplied by the scale value per interval; coordinate differences remain the primary reliable method.
   - Clarified that initial altitude in Graph 8A reflects reference datum / start of observation, not solely a rooftop launch.
   - Specified that battery discharge rate in PRAC-6 is measured in percentage points per hour.
   - Specified on motion graphs in P13 that straight vs. curved lines depend on whether the graph is position-time or speed-time.
5. **Upper-Level Blueprint and Probe Repairs:**
   - Applied resource, pacing, and evidence-scope corrections directly to `grade8_curriculum_blueprint.md`.
   - Corrected pixel endpoints in `probe1_slope_triangles.svg` from $(540, 60)$ to $(555, 60)$ so the drawn line has exact slope $2.0$. Removed the answer box from the graphic.
   - Corrected pixel endpoints in `probe2_water_tank.svg` to $(546.7, 80)$ so the drawn line has exact slope $3.0$.

### 1.2 Review Pass 2 Repairs (Candidate v1.3 Refinements)
In response to "Remaining formatting repair v0.1," the following targeted corrections were executed:
1. **Elimination of Residual KaTeX Parse Errors:**
   - The initial repair pass reduced KaTeX errors from 58 to 22, but left 22 unescaped underscore placeholders inside math text blocks (e.g., `\text{________ gallons per minute}`). 
   - All 22 occurrences in `lesson6_7_8_student_materials.md` and 2 occurrences in `probe_tasks_student_and_teacher.md` were restructured so that fill-in lines (`________`) reside strictly outside math delimiters.
   - The `check_rendering` tool was executed directly on `lesson6_7_8_student_materials.md`, `lesson6_7_8_teacher_guides.md`, and `probe_tasks_student_and_teacher.md`, confirming that all three files now produce `math_errors: []`.
   - *Epistemic Note:* Zero parser errors is strictly a syntactic verification under KaTeX 0.18.7. It does not constitute print layout approval, page-break optimization, or proof of student mathematical learning.
2. **Diagnostic Framing in Teacher CFU Rubrics:**
   - Reframed the CFU-6 diagnostic rubric in `lesson6_7_8_teacher_guides.md`. Rather than labeling an isolated incorrect student response as a "persistent misconception" or a "relapsing habit," errors are classified as possible diagnostic interpretations (e.g., carrying over unit table habits, or misreading the initial table row as $h = 0$).
   - Scripted specific follow-up probing questions to confirm student reasoning prior to enacting pedagogical interventions.
3. **Calibration of Evaluative Claims and Scaffolding Scope:**
   - Corrected earlier sweeping statements regarding workspace verification. Tool results are reported strictly for expressions and files actually evaluated.
   - Clarified the educational role of scaffolds: deliberate worked examples and graphic organizers (such as the difference bracket template) provide vital cognitive access for middle school learners, but student completion of a scaffolded prompt is an indicator of supported performance, not evidence of unaided construct mastery.

---

## 2. Rationale for the Continuous Three-Lesson Sequence (Lessons 6, 7, and 8)

Standard **8.F.B.4** requires students to construct linear models, determine rate of change and initial value across representations, and interpret their physical meaning. Lessons 6, 7, and 8 provide a coherent developmental progression designed to maximize student learning utility within standard classroom constraints:

```
[Lesson 6: Irregular Tables] ───> [Lesson 7: Contextual Lab] ───> [Lesson 8: Scaled Graphs]
  • Δy / Δx across jumps           • Physical flow rates (+/-)      • Coordinate slope triangles
  • Missing x = 0 (b = y - mx)      • Units: gal, min, gal/min       • Overcoming "box counting"
  • Numerical invariance           • Realistic domain bounds        • Reading non-unit grid scales
```

- **Lesson 6 (Tabular Representation):** Tackles tables with $\Delta x > 1$ and missing $x=0$, establishing that linearity depends on constant difference ratios $\frac{\Delta y}{\Delta x}$ rather than raw successive differences $\Delta y$.
- **Lesson 7 (Contextual Representation):** Grounds the rate and intercept in physical dynamics (filling vs. draining), introduces negative slopes, and investigates domain limits ($V \ge 0$).
- **Lesson 8 (Visual/Graphical Representation):** Bridges to the coordinate plane, directly confronting the common pitfall where students count visual boxes rather than computing true coordinate differences on scaled axes.

---

## 3. Mathematical and Representational Verification

The following mathematical tasks, expressions, and pixel-scale geometries were verified using the calculation engine (`SymPy`) and rendering parser (`check_rendering`):

*Important Epistemic Qualification:* The calculation tool evaluates symbolic and arithmetic consistency; the rendering tool validates KaTeX syntax. Neither tool simulates classroom student behavior, nor do they verify physical print legibility.

| Target Task / Item | Evaluated Expressions / Mathematical Relations | Verified Tool Result |
| :--- | :--- | :--- |
| **Lesson 6:** Table 2 (`TASK-6.1`/`6.2`) | $m_1 = \frac{23-11}{5-2} = 4$, $m_2 = \frac{35-23}{8-5} = 4$, $m_3 = \frac{59-35}{14-8} = 4$<br>$b = 11 - 4(2) = 3$<br>Check: $4(14) + 3 = 59$ | Verified: $m = 4$, $b = 3$, $y = 4x + 3$. |
| **Lesson 6:** Cooling Tank (`TASK-6.3`) | $m = \frac{126-156}{9-4} = -6$, $m = \frac{48-90}{22-15} = -6$<br>$b = 156 - (-6)(4) = 180$<br>Empty: $-6t + 180 = 0 \implies t = 30$ | Verified: $m = -6\text{ gal/min}$, $b = 180\text{ gal}$, $W = -6t + 180$, $t = 30\text{ min}$. |
| **Lesson 6:** Exit Ticket (`CFU-6`) | $m = \frac{102-57}{9-4} = 9$, $m = \frac{156-102}{15-9} = 9$<br>$b = 57 - 9(4) = 21$<br>At $h = 8$: $9(8) + 21 = 93$ | Verified: $m = 9\text{ dollars/hr}$, $b = 21\text{ dollars}$, $C = 9h + 21$, Cost = $93\text{ dollars}$. |
| **Lesson 7:** Tank A (`TASK-7.2`) | $b_A = 40$, $m_A = \frac{220-100}{12-4} = 15$<br>Full at $V_A = 250$: $15t + 40 = 250 \implies t = 14$ | Verified: $V_A = 15t + 40$, $t = 14\text{ min}$. |
| **Lesson 7:** Tank B (`TASK-7.2`) | $b_B = 320$, $m_B = \frac{80-240}{12-4} = -20$<br>Empty at $V_B = 0$: $320 - 20t = 0 \implies t = 16$ | Verified: $V_B = -20t + 320$, $t = 16\text{ min}$. |
| **Lesson 7:** Intersection Point | $15t + 40 = 320 - 20t \implies 35t = 280 \implies t = 8$<br>$V_A(8) = 160$, $V_B(8) = 160$ | Verified: Unique intersection at $(8, 160)$. |
| **Lesson 7:** Exit Ticket (`CFU-7`) | $m = \frac{162-330}{12-5} = -24$, $b = 450$<br>Empty: $450 - 24t = 0 \implies t = 18.75$ | Verified: $V = -24t + 450$, $t = 18.75\text{ min}$ ($18\text{ min } 45\text{ sec}$). |
| **Lesson 8:** Graph 8A (`TASK-8.2`) | Points $(0, 50)$, $(2, 100)$, $(6, 200)$, $(10, 300)$<br>$m = \frac{200-100}{6-2} = 25$, $b = 50$<br>At $t = 11$: $25(11) + 50 = 325$ | Verified: $A = 25t + 50$, $A(11) = 325\text{ m}$. |
| **Lesson 8:** Graph 8B (`TASK-8.2`) | Points $(0, 24)$, $(40, 20)$, $(120, 12)$, $(240, 0)$<br>$m = \frac{12-20}{120-40} = -0.1$, $b = 24$<br>Empty: $24 - 0.1d = 0 \implies d = 240$ | Verified: $F = -0.1d + 24$, $d = 240\text{ miles}$. |
| **Lesson 8:** Exit Ticket (`CFU-8`) | Points $P_0(0, 6)$, $P_1(4, 16)$, $P_2(8, 26)$, $P_3(12, 36)$<br>$m = \frac{16-6}{4-0} = 2.5$, $b = 6$<br>At $t = 15$: $2.5(15) + 6 = 43.5$ | Verified: $S = 2.5t + 6$, $S(15) = 43.5\text{ inches}$. |
| **Probe 1:** Geometry (`probe1_slope_triangles.svg`) | Endpoints $(80, 459)$ to $(555, 60)$:<br>$\Delta x = (555-80)/50 = 9.5$, $\Delta y = (480-60)/21 = 19$.<br>Slope $= 19 / 9.5 = 2.0$. | Verified: Line slope $m = 2.000$ matches $y = 2x + 1$. |
| **Probe 2:** Geometry (`probe2_water_tank.svg`) | Endpoints $(80, 360)$ to $(546.67, 80)$:<br>$\Delta t = (546.67-80)/50 = 28/3$, $\Delta D = (440-80)/10 - 8 = 28$.<br>Slope $= 28 / (28/3) = 3.0$. | Verified: Line slope $m = 3.000$ matches $D = 3t + 8$. |
| **Syntax Check:** `check_rendering` | Evaluated KaTeX 0.18.7 parser on `lesson6_7_8_student_materials.md`, `lesson6_7_8_teacher_guides.md`, and `probe_tasks_student_and_teacher.md`. | Verified: All files returned `math_errors: []`. |

---

## 4. Truthful Boundaries, Limitations, and Next Handoff Steps

### 4.1 Explicit Limitations of Current Delivery
1. **Unrendered Content Status:** All student worksheets and teacher guides are formatted in Markdown with separate SVG graphics. While designed to be printable on standard 8.5" $\times$ 11" paper, physical multi-page pagination and visual photocopy contrast have not been tested on actual office printing hardware.
2. **Skeleton Lessons:** Lessons 1–5 and 9–18 exist as a target-evidence curriculum skeleton. They are not yet expanded into full student worksheets and scripted teacher guides.
3. **No Empirical Classroom Trials:** Timing feasibility (50 minutes), student pacing, and diagnostic effectiveness represent reasoned design judgments grounded in standard cognitive principles, but have not been evaluated with actual 28-student Grade 8 cohorts.

### 4.2 Immediate Next Steps for Downstream Development
- Expand Lessons 12–15 (Qualitative Graphing, 8.F.B.5) into complete student task sheets and teacher lesson guides, including the commute card-sort activity for Lesson 15.
- Develop the 50-minute target-sampled summative exam for Lesson 17 with an analytic rubric.
- Conduct print testing of SVG diagrams on 300-dpi black-and-white photocopiers to ensure optimal visual readability.
