# Grade 8 Unit 5: Partially Expanded Unit Candidate (Candidate v1.1)
## Design Rationale, Verification Report, and Upstream Feedback Integration

**Authoring Environment:** Bounded Mathematical Design Task B  
**Target Course:** Grade 8 Mathematics (US Public School Curriculum)  
**Target Unit:** Unit 5: Linear Functions and Contextual Modeling  
**Primary Targeted Standards:** CCSS-M **8.F.B.4** and **8.F.B.5**  
**Candidate Delivery Status:** **Partially Expanded Unit Candidate (Candidate v1.1)**. Lessons 6, 7, and 8 are fully expanded into usable student and teacher materials; Lessons 1–5 and 9–18 are articulated at the target-evidence skeleton level. This document does not claim that the complete unit is finished, nor does it claim human approval or classroom-verified efficacy.

---

## 1. Upstream Review Reconciliation and Patch Record

In response to the formal organizer review of the candidate blueprint (`20260915T021738Z-overall`), five substantive design corrections were made and permanently recorded in `upstream_blueprint_corrections.md`:

1. **Strict Resource Compliance:**
   - *Review Finding:* The upstream blueprint erroneously listed scientific calculators, tracing paper, compasses, protractors, and transparencies.
   - *Correction Applied:* All instructional designs, student worksheets, and teacher lesson guides in Unit 5 strictly adhere to the provided research constraints: black-and-white printing, standard pencils and paper, straightedge rulers, standard grid paper, basic four-function/ordinary calculators, and a single teacher display projector. No specialized geometric instruments or physical water tanks are required; all contextual modeling uses provided data tables, scenarios, and coordinate diagrams.
2. **Pacing and Buffer Integrity:**
   - *Review Finding:* The upstream blueprint implied that Unit 5 had "access to Buffer Block 2 (5 periods)," expanding its instructional requirement.
   - *Correction Applied:* Unit 5 is strictly bounded to **18 regular instructional periods (50 minutes each)**. The 20 annual flex periods remain an unallocated strategic buffer for calendar disruptions or general school needs. The 18-period schedule is completely autonomous; no core lesson depends on flex time.
3. **Epistemic Calibration of Probes and Curricular Order:**
   - *Review Finding:* The upstream blueprint used overly dogmatic language regarding "absolute necessity" and "proof of unique curriculum order."
   - *Correction Applied:* The mathematical probes are acknowledged as verifying specific numerical, algebraic, and geometric relationships (e.g., similar triangles preserving slope ratios; difference quotients isolating rate of change when $b \neq 0$). They provide reasoned, evidence-based pedagogical justifications for our design, but are treated as revisable design judgments rather than dogmatic mandates.
4. **Modesty of Assessment Claims:**
   - *Review Finding:* The blueprint claimed Period 17 establishes "complete mastery."
   - *Correction Applied:* Summative assessments provide cross-sectional evidence on sampled performance indicators; they cannot establish permanent, stable mastery. Ongoing spiral warm-ups in Units 6 and 9 continue monitoring retention.
5. **Clean Separation of Student and Teacher Materials:**
   - *Review Finding:* Probe notes were previously co-located.
   - *Correction Applied:* Student materials (`lesson6_7_8_student_materials.md`) and teacher guides (`lesson6_7_8_teacher_guides.md`) are completely segregated into independent files with aligned Task IDs (`TASK-6.1`, `CFU-6`, `TASK-7.1`, etc.).

---

## 2. Rationale for the Continuous Three-Lesson Sequence (Lessons 6, 7, and 8)

Standard **8.F.B.4** requires students to:
> *"Construct a function to model a linear relationship between two quantities. Determine the rate of change and initial value of the function from a description of a relationship or from two $(x, y)$ values, including reading these from a table or from a graph. Interpret the rate of change and initial value of a linear function in terms of the situation it models, and in terms of its graph or a table of values."*

Rather than isolating these skills into disconnected procedural drills, Lessons 6, 7, and 8 are chosen as a continuous developmental arc that bridges three foundational representations:

```
[Lesson 6: Irregular Tables] ───> [Lesson 7: Contextual Lab] ───> [Lesson 8: Scaled Graphs]
  • Δy / Δx across jumps           • Physical flow rates (+/-)      • Coordinate slope triangles
  • Missing x = 0 (b = y - mx)      • Units: gal, min, gal/min       • Overcoming "box counting"
  • Numerical invariance           • Realistic domain bounds        • Reading non-unit grid scales
```

### 2.1 Lesson 6: The Numerical/Tabular Leap (Irregular Steps)
- *Why It Matters:* In Lesson 5, students work with tables where $\Delta x = 1$, allowing them to identify the rate of change simply by looking at $\Delta y$. If left unaddressed, students develop the fatal habit of ignoring $\Delta x$. 
- *The Mathematical Pivot:* Lesson 6 introduces non-consecutive inputs ($\Delta x = 3, 5, 6$) and omits the row $x = 0$. Students must compute the difference quotient $\frac{\Delta y}{\Delta x}$ across multiple intervals to verify linearity and extrapolate backward to calculate $b = y_1 - m(x_1)$. This builds the exact numerical foundation required for Lesson 7.

### 2.2 Lesson 7: Contextual Modeling and Physical Interpretation
- *Why It Matters:* Mathematics must not remain unmoored from physical reality. Standard 8.F.B.4 emphasizes interpreting parameters in terms of the situation modeled.
- *The Mathematical Pivot:* Lesson 7 contextualizes the mathematical mechanics from Lesson 6 into a dual water reservoir system (Tank A filling at $+15\text{ gal/min}$ from an initial $40\text{ gal}$; Tank B draining at $-20\text{ gal/min}$ from an initial $320\text{ gal}$). Students grapple with:
  - The physical meaning of positive versus negative slope (liquid entering vs. leaving).
  - Physical units: rate is $\text{gallons}/\text{minute}$, intercept is $\text{gallons}$.
  - Domain constraints: Tank A stops filling at 250 gallons ($t = 14\text{ min}$); Tank B cannot drain past 0 gallons ($t = 16\text{ min}$).
  - The shared point $(8, 160)$: where both tanks hold identical water volume, providing an organic bridge to simultaneous systems in Unit 6.

### 2.3 Lesson 8: Graphical Precision and Scaled Coordinate Planes
- *Why It Matters:* Students frequently fall into the "counting grid squares" trap, assuming that 2 boxes up and 1 box right means a slope of 2, even when the axes represent miles and hours with non-unit scales.
- *The Mathematical Pivot:* Lesson 8 presents coordinate graphs where horizontal and vertical axes have radically different scales (Graph 8A: Drone Ascent, where 1 box = 1 min horizontally and 25 m vertically; Graph 8B: Delivery Truck Fuel, where 1 box = 20 miles horizontally and 2.5 gallons vertically). Students must construct coordinate slope triangles, attend to precision (MP6), and calculate rate of change directly from coordinate values rather than physical paper squares.

---

## 3. Mathematical and Representational Verification

All mathematical problems, parameters, coordinate mappings, and algebraic solutions across the three lessons were independently checked using the symbolic engine (`SymPy`).

| Artifact / Task | Mathematical Relations Verified | Engine Result / Verification |
| :--- | :--- | :--- |
| **Lesson 6:** Table 2 (`TASK-6.1`/`6.2`) | $m_1 = \frac{23-11}{5-2} = 4$, $m_2 = \frac{35-23}{8-5} = 4$, $m_3 = \frac{59-35}{14-8} = 4$<br>$b = 11 - 4(2) = 3$<br>Check: $4(14) + 3 = 59$ | Verified: $m = 4$, $b = 3$, $y = 4x + 3$. |
| **Lesson 6:** Cooling Tank (`TASK-6.3`) | $m = \frac{126-156}{9-4} = -6$, $m = \frac{48-90}{22-15} = -6$<br>$b = 156 - (-6)(4) = 180$<br>Empty: $-6t + 180 = 0 \implies t = 30$ | Verified: $m = -6\text{ gal/min}$, $b = 180\text{ gal}$, $W = -6t + 180$, $t = 30\text{ min}$. |
| **Lesson 6:** Exit Ticket (`CFU-6`) | $m = \frac{102-57}{9-4} = 9$, $m = \frac{156-102}{15-9} = 9$<br>$b = 57 - 9(4) = 21$<br>At $h = 8$: $9(8) + 21 = 93$ | Verified: $m = \$9/\text{hr}$, $b = \$21$, $C = 9h + 21$, Cost = $\$93$. |
| **Lesson 7:** Tank A (`TASK-7.2`) | $b_A = 40$, $m_A = \frac{220-100}{12-4} = 15$<br>Full at $V_A = 250$: $15t + 40 = 250 \implies t = 14$ | Verified: $V_A = 15t + 40$, $t = 14\text{ min}$. |
| **Lesson 7:** Tank B (`TASK-7.2`) | $b_B = 320$, $m_B = \frac{80-240}{12-4} = -20$<br>Empty at $V_B = 0$: $320 - 20t = 0 \implies t = 16$ | Verified: $V_B = -20t + 320$, $t = 16\text{ min}$. |
| **Lesson 7:** Intersection Point | Solve $15t + 40 = 320 - 20t \implies 35t = 280 \implies t = 8$<br>$V_A(8) = 160$, $V_B(8) = 160$ | Verified: Unique intersection at $(8, 160)$. |
| **Lesson 7:** Exit Ticket (`CFU-7`) | $m = \frac{162-330}{12-5} = -24$, $b = 450$<br>Empty: $450 - 24t = 0 \implies t = 18.75$ | Verified: $V = -24t + 450$, $t = 18.75\text{ min}$ ($18\text{ min } 45\text{ sec}$). |
| **Lesson 8:** Graph 8A (`TASK-8.2`) | $(0, 50)$, $(2, 100)$, $(6, 200)$, $(10, 300)$<br>$m = \frac{200-100}{6-2} = 25$, $b = 50$<br>At $t = 11$: $25(11) + 50 = 325$ | Verified: $A = 25t + 50$, $A(11) = 325\text{ m}$. |
| **Lesson 8:** Graph 8B (`TASK-8.2`) | $(0, 24)$, $(40, 20)$, $(120, 12)$, $(240, 0)$<br>$m = \frac{12-20}{120-40} = -0.1$, $b = 24$<br>Empty: $24 - 0.1d = 0 \implies d = 240$ | Verified: $F = -0.1d + 24$, $d = 240\text{ miles}$. |
| **Lesson 8:** Exit Ticket (`CFU-8`) | $(0, 6)$, $(4, 16)$, $(8, 26)$<br>$m = \frac{16-6}{4-0} = 2.5$, $b = 6$<br>At $t = 15$: $2.5(15) + 6 = 43.5$ | Verified: $S = 2.5t + 6$, $S(15) = 43.5\text{ inches}$. |

### Visual Graphic Self-Containment:
- `lesson7_reservoir_models.svg`: Built with standard coordinate axes, high-contrast monochrome styles, solid and dashed line coding for grayscale rendering, labeled tick marks ($t \in [0, 18]$, $V \in [0, 360]$), explicit callout points, and a self-contained legend.
- `lesson8_scaled_graphs.svg`: Built with a two-panel side-by-side layout, distinct axis titles with units, clear major/minor grid lines, shaded slope triangles with dimension callouts, and explicit lattice points.

---

## 4. Truthful Boundaries, Limitations, and Next Handoff Steps

### 4.1 Explicit Limitations of Current Delivery
1. **Unrendered Content Status:** All student worksheets and teacher guides are formatted in pure Markdown with vector SVG graphics. While engineered specifically for black-and-white 8.5" $\times$ 11" paper layout, they have not undergone physical print-rendering tests. True multi-page pagination must be visually verified before bulk printing.
2. **Skeleton Lessons:** Lessons 1–5 and 9–18 exist as a rigorous target-evidence curriculum skeleton. They are not yet expanded into full student worksheets and scripted teacher guides.
3. **No Empirical Classroom Evidence:** The pedagogical strategies, timing allocations (50 minutes), and anticipated student misconceptions are grounded in mathematical design analysis and standard cognitive research, but have not been tested in live 28-student classrooms.

### 4.2 Immediate Next Steps for Downstream Development
- Expand Cluster 4 (Lessons 12–15: Qualitative Graphing, 8.F.B.5) into full student task sheets, specifically authoring the card-sort materials for Lesson 15 (`TASK-15.1`).
- Develop the 50-minute target-sampled summative assessment for Lesson 17 with an accompanying multi-trait scoring rubric.
- Conduct layout rendering tests on `lesson7_reservoir_models.svg` and `lesson8_scaled_graphs.svg` to ensure optimal contrast on standard 300-dpi office photocopiers.
