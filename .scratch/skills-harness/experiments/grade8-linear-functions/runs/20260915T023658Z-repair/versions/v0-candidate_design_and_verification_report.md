# Grade 8 Unit 5: Partially Expanded Unit Candidate (Candidate v1.2 — Repaired)
## Design Rationale, Verification Report, and Review Repair Integration

**Authoring Environment:** Bounded Mathematical Design Task B  
**Target Course:** Grade 8 Mathematics (US Public School Curriculum)  
**Target Unit:** Unit 5: Linear Functions and Contextual Modeling  
**Primary Targeted Standards:** CCSS-M **8.F.B.4** and **8.F.B.5**  
**Candidate Delivery Status:** **Partially Expanded Unit Candidate (Candidate v1.2)**. Lessons 6, 7, and 8 are fully expanded into usable student task sheets and scripted teacher guides; Lessons 1–5 and 9–18 are articulated at the target-evidence skeleton level. This document does not claim complete unit expansion, nor does it claim human approval or classroom-verified efficacy.

---

## 1. Upstream Review Reconciliation and Repair Record

In response to "Actual-material review 1 — organizer findings," seven comprehensive repairs were executed across all candidate artifacts:

1. **Graph-Reading Evidence and Geometric Consistency (Finding 1):**
   - *CFU-8 Graph:* Replaced the problematic ASCII sketch with an authentic, self-contained SVG graphic (`cfu8_snow_graph.svg`). The graph features exact grid lines every 2 inches vertically and 2 hours horizontally, with points marked ($P_0, P_1, P_2, P_3$) without coordinate labels. Students must read the scales directly from the axes, ensuring that successful calculation is genuine evidence of graph-reading proficiency.
   - *TASK-8.1 Diagram:* Provided the previously missing sketch as a self-contained SVG graphic (`task8_1_trap_sketch.svg`), illustrating the "counting grid squares" dilemma ($2\text{ boxes up} / 1\text{ box right} \implies 2\text{ vs. } 20\text{ mph}$).
   - *PRAC-8.1 Text:* Resolved the contradiction where $(20, 235)$ was described as a clean grid intersection on a grid spaced by 50. The problem is now described accurately as recorded order data/points for an algebraic model.
2. **Preserving Student Mathematical Work (Finding 2):**
   - *Legend Rates:* Removed explicit rate values ($+15\text{ gal/min}$, $-20\text{ gal/min}$) from the student-facing legend in `lesson7_reservoir_models.svg`.
   - *Pre-filled Formulas:* Removed pre-filled algebraic equations in TASK-7.3 question 3, requiring students to substitute $t = 8$ directly into their own constructed equations.
3. **KaTeX Formatting and Document Usability (Finding 3):**
   - *KaTeX Math Errors:* Replaced all 58 unescaped underscores in math mode (`\text{______}`) with clean Markdown blank lines outside math delimiters (`$b =$ ________`).
   - *Markdown Table Formatting:* Converted literal `\n` tokens in teacher diagnostic tables into actual newlines, restoring proper table rendering.
   - *Response Spaces:* Added boxed workspace containers and clear blank lines for multi-step calculations and written explanations.
4. **Resource and Time Reconciliations (Finding 4):**
   - *Classroom Materials:* Replaced colored-pencil guidance in CFU-6 with standard pencil techniques (circling $\Delta C$, boxing $\Delta h$).
   - *Visual Scaffold:* Added the printed Two-Column Difference Bracket Template directly onto the Lesson 6 student sheet.
   - *Practice Structure:* Clearly designated PRAC-6, PRAC-7, and PRAC-8 as selectable/optional practice (for station differentiation or optional study), preserving the integrity of the 50-minute core lesson.
5. **Claims and Diagnostic Calibration (Finding 5):**
   - Replaced overreaching claims of "complete mastery" with calibrated statements of "demonstrated proficiency on sampled targets."
   - Reframed error diagnostics to offer multi-cause interpretations and targeted pedagogical questions.
   - Clarified verification records to distinguish symbolic engine checks from graphical layout and student perceptual reading.
6. **Semantic and Mathematical Qualifications (Finding 6):**
   - Qualified the "Never count boxes" rule: counting intervals is valid only when multiplied by the scale value per interval; coordinate differences remain the primary reliable method.
   - Clarified that initial altitude in Graph 8A reflects reference datum / start of observation, not solely a rooftop launch.
   - Specified that battery discharge rate in PRAC-6 is measured in percentage points per hour.
   - Specified on motion graphs in P13 that straight vs. curved lines depend on whether the graph is position-time or speed-time.
7. **Upper-Level Blueprint and Probe Repairs (Finding 7):**
   - Applied resource, pacing, and evidence-scope corrections directly to `grade8_curriculum_blueprint.md`.
   - Corrected pixel endpoints in `probe1_slope_triangles.svg` from $(540, 60)$ to $(555, 60)$ so the drawn line has exact slope $2.0$. Removed the answer box from the graphic.
   - Corrected pixel endpoints in `probe2_water_tank.svg` to $(546.7, 80)$ so the drawn line has exact slope $3.0$.
   - Reconciled `probe_tasks_student_and_teacher.md` formatting and document context.

---

## 2. Rationale for the Continuous Three-Lesson Sequence (Lessons 6, 7, and 8)

Standard **8.F.B.4** requires students to construct linear models, determine rate of change and initial value across representations, and interpret their physical meaning. Lessons 6, 7, and 8 provide a coherent developmental triad:

```
[Lesson 6: Irregular Tables] ───> [Lesson 7: Contextual Lab] ───> [Lesson 8: Scaled Graphs]
  • Δy / Δx across jumps           • Physical flow rates (+/-)      • Coordinate slope triangles
  • Missing x = 0 (b = y - mx)      • Units: gal, min, gal/min       • Overcoming "box counting"
  • Numerical invariance           • Realistic domain bounds        • Reading non-unit grid scales
```

- **Lesson 6:** Tackles tables with $\Delta x > 1$ and missing $x=0$, establishing that linearity depends on constant difference ratios $\frac{\Delta y}{\Delta x}$ rather than raw successive differences $\Delta y$.
- **Lesson 7:** Grounds the rate and intercept in physical dynamics (filling vs. draining), introduces negative slopes, and investigates domain limits ($V \ge 0$).
- **Lesson 8:** Bridges to the coordinate plane, directly confronting the common pitfall where students count visual boxes rather than computing true coordinate differences on scaled axes.

---

## 3. Mathematical and Representational Verification

The following mathematical relationships, formulas, and pixel-scale geometries were independently checked using the symbolic evaluation engine (`SymPy`).

*Important Epistemic Qualification:* The symbolic engine verifies algebraic consistency, arithmetic evaluation, and geometric coordinates. It does **not** simulate classroom student behavior, nor does it verify student visual perception of diagrams.

| Target Task / Item | Evaluated Expressions / Mathematical Relations | Symbolic Result / Verification |
| :--- | :--- | :--- |
| **Lesson 6:** Table 2 (`TASK-6.1`/`6.2`) | $m_1 = \frac{23-11}{5-2} = 4$, $m_2 = \frac{35-23}{8-5} = 4$, $m_3 = \frac{59-35}{14-8} = 4$<br>$b = 11 - 4(2) = 3$<br>Check: $4(14) + 3 = 59$ | Verified: $m = 4$, $b = 3$, $y = 4x + 3$. |
| **Lesson 6:** Cooling Tank (`TASK-6.3`) | $m = \frac{126-156}{9-4} = -6$, $m = \frac{48-90}{22-15} = -6$<br>$b = 156 - (-6)(4) = 180$<br>Empty: $-6t + 180 = 0 \implies t = 30$ | Verified: $m = -6\text{ gal/min}$, $b = 180\text{ gal}$, $W = -6t + 180$, $t = 30\text{ min}$. |
| **Lesson 6:** Exit Ticket (`CFU-6`) | $m = \frac{102-57}{9-4} = 9$, $m = \frac{156-102}{15-9} = 9$<br>$b = 57 - 9(4) = 21$<br>At $h = 8$: $9(8) + 21 = 93$ | Verified: $m = \$9/\text{hr}$, $b = \$21$, $C = 9h + 21$, Cost = $\$93$. |
| **Lesson 7:** Tank A (`TASK-7.2`) | $b_A = 40$, $m_A = \frac{220-100}{12-4} = 15$<br>Full at $V_A = 250$: $15t + 40 = 250 \implies t = 14$ | Verified: $V_A = 15t + 40$, $t = 14\text{ min}$. |
| **Lesson 7:** Tank B (`TASK-7.2`) | $b_B = 320$, $m_B = \frac{80-240}{12-4} = -20$<br>Empty at $V_B = 0$: $320 - 20t = 0 \implies t = 16$ | Verified: $V_B = -20t + 320$, $t = 16\text{ min}$. |
| **Lesson 7:** Intersection Point | $15t + 40 = 320 - 20t \implies 35t = 280 \implies t = 8$<br>$V_A(8) = 160$, $V_B(8) = 160$ | Verified: Unique intersection at $(8, 160)$. |
| **Lesson 7:** Exit Ticket (`CFU-7`) | $m = \frac{162-330}{12-5} = -24$, $b = 450$<br>Empty: $450 - 24t = 0 \implies t = 18.75$ | Verified: $V = -24t + 450$, $t = 18.75\text{ min}$ ($18\text{ min } 45\text{ sec}$). |
| **Lesson 8:** Graph 8A (`TASK-8.2`) | Points $(0, 50)$, $(2, 100)$, $(6, 200)$, $(10, 300)$<br>$m = \frac{200-100}{6-2} = 25$, $b = 50$<br>At $t = 11$: $25(11) + 50 = 325$ | Verified: $A = 25t + 50$, $A(11) = 325\text{ m}$. |
| **Lesson 8:** Graph 8B (`TASK-8.2`) | Points $(0, 24)$, $(40, 20)$, $(120, 12)$, $(240, 0)$<br>$m = \frac{12-20}{120-40} = -0.1$, $b = 24$<br>Empty: $24 - 0.1d = 0 \implies d = 240$ | Verified: $F = -0.1d + 24$, $d = 240\text{ miles}$. |
| **Lesson 8:** Exit Ticket (`CFU-8`) | Points $P_0(0, 6)$, $P_1(4, 16)$, $P_2(8, 26)$, $P_3(12, 36)$<br>$m = \frac{16-6}{4-0} = 2.5$, $b = 6$<br>At $t = 15$: $2.5(15) + 6 = 43.5$ | Verified: $S = 2.5t + 6$, $S(15) = 43.5\text{ inches}$. |
| **Probe 1:** Geometry (`probe1_slope_triangles.svg`) | Origin $(80, 480)$, scale $50\text{ px}/x, 21\text{ px}/y$.<br>Endpoints $(80, 459)$ to $(555, 60)$:<br>$\Delta x = (555-80)/50 = 9.5$, $\Delta y = (480-60)/21 = 20 - 1 = 19$.<br>Slope $= 19 / 9.5 = 2.0$. | Verified: Exact line slope $m = 2.0$ matches equation $y = 2x + 1$. |
| **Probe 2:** Geometry (`probe2_water_tank.svg`) | Origin $(80, 440)$, scale $50\text{ px}/\text{hr}, 10\text{ px}/\text{in}$.<br>Endpoints $(80, 360)$ to $(546.67, 80)$:<br>$\Delta t = (546.67-80)/50 = 28/3$, $\Delta D = (440-80)/10 - 8 = 36 - 8 = 28$.<br>Slope $= 28 / (28/3) = 3.0$. | Verified: Exact line slope $m = 3.0$ matches equation $D = 3t + 8$. |

---

## 4. Truthful Boundaries, Limitations, and Next Handoff Steps

### 4.1 Explicit Limitations of Current Delivery
1. **Unrendered Content Status:** All student worksheets and teacher guides are formatted in pure Markdown with vector SVG graphics. While engineered specifically for black-and-white 8.5" $\times$ 11" paper layout, they have not undergone physical print-rendering tests. True multi-page pagination must be visually verified before bulk printing.
2. **Skeleton Lessons:** Lessons 1–5 and 9–18 exist as a rigorous target-evidence curriculum skeleton. They are not yet expanded into full student worksheets and scripted teacher guides.
3. **No Empirical Classroom Evidence:** The pedagogical strategies, timing allocations (50 minutes), and anticipated student misconceptions are grounded in mathematical design analysis and standard cognitive research, but have not been tested in live 28-student classrooms.

### 4.2 Immediate Next Steps for Downstream Development
- Author full student task sheets and teacher guides for Cluster 4 (Lessons 12–15: Qualitative Graphing, 8.F.B.5), including card-sort materials for Lesson 15 (`TASK-15.1`).
- Author the 50-minute target-sampled summative assessment for Lesson 17 with an accompanying multi-trait scoring rubric.
- Conduct layout rendering tests on all SVG diagrams (`lesson7_reservoir_models.svg`, `lesson8_scaled_graphs.svg`, `cfu8_snow_graph.svg`, `task8_1_trap_sketch.svg`) to ensure optimal contrast on standard 300-dpi office photocopiers.
