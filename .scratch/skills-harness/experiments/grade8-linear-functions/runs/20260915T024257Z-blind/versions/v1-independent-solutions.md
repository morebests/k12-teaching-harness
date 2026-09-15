# Independent Mathematical Solution and Reading Audit: Lessons 6, 7, and 8

**Document Identifier:** `independent-solutions.md`  
**Evaluation Scope:** Grade 8 Mathematics, Unit 5: Linear Functions and Contextual Modeling (Continuous Three-Lesson Sequence: Lessons 6, 7, and 8)  
**Evaluator Status:** Autonomous Model Independent Reading Audit (Strictly based on student-visible materials and accompanying SVG diagrams; no teacher answer keys, generation logs, or prior rubrics provided).  
**Source Materials Audited:**
- Student Task Document: `lesson6_7_8_student_materials.md`
- Visual Artifacts:
  - `lesson7_reservoir_models.svg` (Figure 7.1)
  - `task8_1_trap_sketch.svg` (Figure 8.0)
  - `lesson8_scaled_graphs.svg` (Figure 8.1)
  - `cfu8_snow_graph.svg` (Figure 8.2)

---

## 1. Executive Summary & Audit Scope

This document provides complete, independent mathematical solutions, verifiable derivations, parameter determinations, and visual/textual consistency audits for every student-facing task across Lessons 6, 7, and 8. 

### Coverage Summary
- **Total Student Task IDs Audited:** 17 tasks (including launches, core investigations, partner practice, exit tickets [CFU], extensions, and practice problem sets).
- **Total Distinct Question Prompts Checked:** 46 mathematical sub-questions.
- **Coverage Mode:** Complete 100% census (no random sampling; every item is independently solved and audited).
- **Core Findings:**
  1. **Mathematical Soundness:** The underlying mathematical progressions in Lessons 6 and 7, as well as Lesson 8.1 and 8.2, are mathematically rigorous, fully solvable, and internally consistent in values and units.
  2. **Graphic Alignment in Lesson 7 & Lesson 8.2:** Figures 7.1 and 8.1 accurately display all labeled coordinate points, slopes, and piecewise features (e.g., Tank A shutoff capping at 250 gal).
  3. **Visual Collision in Figure 8.0 (`task8_1_trap_sketch.svg`):** The text annotation `"1 grid box right"` overlaps directly with the horizontal tick label `"5"`.
  4. **Critical Reading Dilemma in CFU-8 (`cfu8_snow_graph.svg`):** Point $P_0(0, 6)$ and point $P_3(12, 36)$ align cleanly on grid intersections, establishing the line $S = 2.5t + 6$. However, points $P_1(4, 16)$ and $P_2(8, 26)$ lie at non-grid positions on an axis whose grid lines increment by $3$ (major ticks by $6$). Because numerical coordinates are omitted from the diagram, students instructed to "read coordinates from the grid axes" cannot do so with exact integer precision without interpolating or deducing the slope from $P_0$ and $P_3$. In addition, the top vertical tick is labeled `40` despite following uniform step increments of 6 ($0, 6, 12, 18, 24, 30, 36$), where $42$ would be expected.

---

## 2. Complete Independent Solutions by Task

---

### LESSON 6: Constructing Linear Functions from Irregular Tables

#### Task ID: TASK-6.1 — Launch: Notice and Wonder with Two Tables
*Source:* `lesson6_7_8_student_materials.md`  
*Tables Provided:*
- Table 1 (Plan A): $(0, 5), (1, 9), (2, 13), (3, 17)$
- Table 2 (Plan B): $(2, 11), (5, 23), (8, 35), (14, 59)$

**Part 1: Calculate the Differences (Table 1)**
1. Consecutive change in $x$:
   $$\Delta x = 1 - 0 = 2 - 1 = 3 - 2 = 1$$
   **Answer:** $\Delta x = 1$
2. Consecutive change in $y$:
   $$\Delta y = 9 - 5 = 13 - 9 = 17 - 13 = 4$$
   **Answer:** $\Delta y = 4$
3. Rate of change:
   $$\text{Rate} = \frac{\Delta y}{\Delta x} = \frac{4}{1} = 4$$
   **Answer:** $\text{Rate} = 4$
4. Initial value ($b$ when $x = 0$):
   Directly from row 1 $(0, 5)$:
   **Answer:** $b = 5$
5. Equation:
   **Answer:** $y = 4x + 5$

**Part 2: Examine Table 2**
1. Step from $(2, 11)$ to $(5, 23)$:
   $$\Delta x = 5 - 2 = 3$$
   $$\Delta y = 23 - 11 = 12$$
   **Answer:** $\Delta x = 3$, $\Delta y = 12$
2. Step from $(8, 35)$ to $(14, 59)$:
   $$\Delta x = 14 - 8 = 6$$
   $$\Delta y = 59 - 35 = 24$$
   **Answer:** $\Delta x = 6$, $\Delta y = 24$
3. Evaluation of Jordan's Claim (*"The outputs jump by 12, and then by 24, so this table cannot be linear."*):
   - **Judgment:** Disagree with Jordan.
   - **Mathematical Justification:** Linearity requires a constant *ratio* of change $\frac{\Delta y}{\Delta x}$ (unit rate of change), not equal absolute changes in $y$ when $\Delta x$ is unequal.
     - First interval: $\frac{\Delta y}{\Delta x} = \frac{12}{3} = 4$
     - Third interval: $\frac{\Delta y}{\Delta x} = \frac{24}{6} = 4$
     Because $\frac{\Delta y}{\Delta x} = 4$ is constant across all intervals, the function is linear. Jordan evaluated only $\Delta y$ without dividing by $\Delta x$.

---

#### Task ID: TASK-6.2 — Core Activity: Determining Rate of Change and Extrapolating Initial Value
*Source:* `lesson6_7_8_student_materials.md`

1. **Unit Rate of Change ($m$) for Table 2:**
   - Interval 1 ($x = 2$ to $x = 5$): $\frac{23 - 11}{5 - 2} = \frac{12}{3} = 4$
   - Interval 2 ($x = 5$ to $x = 8$): $\frac{35 - 23}{8 - 5} = \frac{12}{3} = 4$
   - Interval 3 ($x = 8$ to $x = 14$): $\frac{59 - 35}{14 - 8} = \frac{24}{6} = 4$
   - Is the rate of change constant? **Yes.**
   - Value of $m$: **$m = 4$**
2. **Finding the Initial Value ($b$):**
   - Using point $(2, 11)$ and $m = 4$:
     $$y = mx + b \implies 11 = 4(2) + b \implies 11 = 8 + b \implies b = 3$$
     *(Alternative step-back reasoning: Moving 2 units left from $x = 2$ to $x = 0$ decreases $y$ by $2 \times 4 = 8$; $11 - 8 = 3$.)*
   - Initial value: **$b = 3$**
   - Complete linear equation: **$y = 4x + 3$**
3. **Verification:**
   - Test with point $(14, 59)$:
     $$y = 4(14) + 3 = 56 + 3 = 59$$
   - Matches table output $y = 59$. Verified.

---

#### Task ID: TASK-6.3 — Partner Practice: A Decreasing Relationship
*Source:* `lesson6_7_8_student_materials.md`  
*Table Provided:* $(4, 156), (9, 126), (15, 90), (22, 48)$

1. Rate of change between $(4, 156)$ and $(9, 126)$:
   $$\frac{\Delta W}{\Delta t} = \frac{126 - 156}{9 - 4} = \frac{-30}{5} = -6\text{ gallons per minute}$$
   **Answer:** $-6$ (or decreasing at $6$) gallons per minute.
2. Rate of change between $(15, 90)$ and $(22, 48)$:
   $$\frac{\Delta W}{\Delta t} = \frac{48 - 90}{22 - 15} = \frac{-42}{7} = -6\text{ gallons per minute}$$
   **Answer:** $-6$ gallons per minute.
3. Real-world meaning of the negative rate:
   - The negative sign indicates that the water volume is decreasing over time. The cooling tank is losing/consuming water at a constant rate of $6$ gallons every minute.
4. Initial water volume ($t = 0$):
   $$W = -6t + b \implies 156 = -6(4) + b \implies 156 = -24 + b \implies b = 180$$
   **Answer:** $b = 180$ gallons.
5. Linear equation:
   **Answer:** $W = -6t + 180$ (or $W = 180 - 6t$)
6. Time to completely empty ($W = 0$):
   $$0 = -6t + 180 \implies 6t = 180 \implies t = 30$$
   **Answer:** $t = 30$ minutes.

---

#### Task ID: CFU-6 — Independent Check for Understanding (Exit Ticket 6)
*Source:* `lesson6_7_8_student_materials.md`  
*Table Provided:* $(4, 57), (9, 102), (15, 156)$

1. Technician's hourly labor rate ($m$):
   $$m = \frac{102 - 57}{9 - 4} = \frac{45}{5} = 9\text{ dollars per hour}$$
   *(Verification on second interval: $\frac{156 - 102}{15 - 9} = \frac{54}{6} = 9$.)*  
   **Answer:** $m = 9$ dollars per hour.
2. Fixed home-visit fee ($b$):
   $$C = 9h + b \implies 57 = 9(4) + b \implies 57 = 36 + b \implies b = 21$$
   **Answer:** $b = 21$ dollars.
3. Linear equation:
   **Answer:** $C = 9h + 21$
4. Total charge for $8$ hours:
   $$C(8) = 9(8) + 21 = 72 + 21 = 93$$
   **Answer:** $93$ dollars.

---

#### Task ID: EXT-6 — Extension Task (Optional Challenge)
*Source:* `lesson6_7_8_student_materials.md`  
*Table Provided:* $(3, 19), (7, ?), (12, 64), (?, 89)$

1. Rate of change $m$ and initial value $b$:
   - Known points: $(3, 19)$ and $(12, 64)$
   $$m = \frac{64 - 19}{12 - 3} = \frac{45}{9} = 5$$
   $$b = 19 - 5(3) = 19 - 15 = 4$$
   **Answer:** $m = 5$, $b = 4$
2. Missing smudged values:
   - When $x = 7$:
     $$y = 5(7) + 4 = 35 + 4 = 39$$
     **Answer:** $y = 39$
   - When $y = 89$:
     $$5x + 4 = 89 \implies 5x = 85 \implies x = 17$$
     **Answer:** $x = 17$

---

#### Task ID: PRAC-6 — Selectable / Optional Practice Problems
*Source:* `lesson6_7_8_student_materials.md`

**Problem 1: Points $(5, 65)$ and $(15, 145)$**
- Rate of change:
  $$m = \frac{145 - 65}{15 - 5} = \frac{80}{10} = 8$$
  **Answer:** $m = 8$
- Initial value:
  $$b = 65 - 8(5) = 65 - 40 = 25$$
  **Answer:** $b = 25$
- Function rule:
  **Answer:** $y = 8x + 25$
- Output when $x = 25$:
  $$y = 8(25) + 25 = 200 + 25 = 225$$
  **Answer:** $y = 225$

**Problem 2: Discharging Battery**
- Points given: $(6, 74\%)$ and $(14, 42\%)$
- Hourly discharge rate:
  $$m = \frac{42 - 74}{14 - 6} = \frac{-32}{8} = -4\text{ percentage points per hour}$$
  **Answer:** $-4\%$ per hour (or $-4$ percentage points per hour).
- Initial percentage at $t = 0$:
  $$b = 74 - (-4)(6) = 74 + 24 = 98\%$$
  **Answer:** $b = 98\%$
- Linear equation:
  **Answer:** $P = -4t + 98$ (or $P = 98 - 4t$)
- Complete discharge time ($P = 0\%$):
  $$0 = -4t + 98 \implies 4t = 98 \implies t = 24.5\text{ hours}$$
  **Answer:** $t = 24.5$ hours (or $24\frac{1}{2}$ hours, or 24 hours 30 minutes).

---

### LESSON 7: Contextual Modeling: Filling and Draining Systems

#### Task ID: TASK-7.1 — Launch: Two Tanks, Two Stories
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `lesson7_reservoir_models.svg` (Figure 7.1)
- Context setup introducing Tank A (solid line, filling) and Tank B (dashed line, draining).
- No direct numeric question prompts in TASK-7.1; questions are structured under TASK-7.2.

---

#### Task ID: TASK-7.2 — Core Modeling Lab: Tank A and Tank B
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `lesson7_reservoir_models.svg` (Figure 7.1)

**Part 1: Tank A (The Filling Tank — Solid Line)**
1. Initial Volume:
   - Axis intercept: Point $A_0(0, 40)$ on the vertical axis.
   - **Answer:** $b_A = 40$ gallons.
   - **Meaning:** At the start of observation ($t = 0$), Tank A already contained 40 gallons of water.
2. Filling Rate ($m_A$):
   - Marked points: $(4, 100)$ and $(12, 220)$.
   - $\Delta t = 12 - 4 = 8$ minutes.
   - $\Delta V = 220 - 100 = 120$ gallons.
   - $m_A = \frac{120}{8} = 15$ gallons per minute.
   - **Answer:** $m_A = 15$ gallons per minute.
   - **Interpretation:** Water flows into Tank A at a constant filling speed of 15 gallons each minute.
3. Linear Function for Tank A:
   - **Answer:** $V_A = 15t + 40$

**Part 2: Tank B (The Draining Tank — Dashed Line)**
4. Initial Volume:
   - Axis intercept: Point $B_0(0, 320)$ on the vertical axis.
   - **Answer:** $b_B = 320$ gallons.
   - **Meaning:** Tank B was initially filled to its starting volume of 320 gallons at $t = 0$.
5. Draining Rate ($m_B$):
   - Marked points: $(4, 240)$ and $(12, 80)$.
   - $\Delta t = 12 - 4 = 8$ minutes.
   - $\Delta V = 80 - 240 = -160$ gallons.
   - $m_B = \frac{-160}{8} = -20$ gallons per minute.
   - **Answer:** $m_B = -20$ gallons per minute.
   - **Negative sign interpretation:** The rate is negative because water is being removed from Tank B, decreasing total remaining volume.
6. Linear Function for Tank B:
   - **Answer:** $V_B = -20t + 320$ (or $V_B = 320 - 20t$)

---

#### Task ID: TASK-7.3 — Realistic Constraints and Intersection Analysis
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `lesson7_reservoir_models.svg` (Figure 7.1)

1. **Maximum Capacity of Tank A (250 gallons):**
   - Solving for trigger time:
     $$15t + 40 = 250 \implies 15t = 210 \implies t = 14\text{ minutes}$$
     **Answer:** $t = 14$ minutes.
   - **Observation of Graph between $t = 14$ and $t = 18$:**  
     At point $(14, 250)$ labeled `"Full: (14, 250)"`, the filling stops. Between $t = 14$ and $t = 18$, the graph becomes a horizontal dashed line at constant height $V = 250$, indicating the pump has shut off and the volume remains capped at 250 gallons.
2. **Emptying of Tank B ($V_B = 0$):**
   - Solving for empty time:
     $$-20t + 320 = 0 \implies 20t = 320 \implies t = 16\text{ minutes}$$
     **Answer:** $t = 16$ minutes.
   - Marked on graph: `"Empty: (16, 0)"`.
   - Practical domain: from $t = 0$ to $t = 16$ minutes.
3. **The Shared Point (Point of Intersection):**
   - Coordinates: $(8, 160)$ labeled `"Shared: (8, 160)"`.
   - **Horizontal coordinate ($t = 8$):** At 8 minutes after operations begin...
   - **Vertical coordinate ($V = 160$):** ...both tanks contain the exact same volume of water, 160 gallons.
   - **Algebraic Verification:**
     - Tank A: $V_A(8) = 15(8) + 40 = 120 + 40 = 160$ (Verified).
     - Tank B: $V_B(8) = -20(8) + 320 = -160 + 320 = 160$ (Verified).

---

#### Task ID: CFU-7 — Independent Check for Understanding (Exit Ticket 7)
*Source:* `lesson6_7_8_student_materials.md`  
*Given Information:* Pool contains 450 gallons initially ($b = 450$). At $t = 5$, $V = 330$; at $t = 12$, $V = 162$.

1. Constant draining rate (rate of change):
   $$m = \frac{162 - 330}{12 - 5} = \frac{-168}{7} = -24\text{ gallons per minute}$$
   **Answer:** $m = -24$ gallons per minute (or draining at $24$ gal/min).
2. Initial volume $b$:
   Given as 450 gallons in the narrative stem.  
   *(Consistency check: $V(0) = 330 - (-24)(5) = 330 + 120 = 450$. Consistent.)*  
   **Answer:** $b = 450$ gallons.
3. Linear equation:
   **Answer:** $V = -24t + 450$ (or $V = 450 - 24t$)
4. Exact emptying minute ($V = 0$):
   $$-24t + 450 = 0 \implies 24t = 450 \implies t = \frac{450}{24} = \frac{75}{4} = 18.75\text{ minutes}$$
   **Answer:** $t = 18.75$ minutes (or $18\frac{3}{4}$ minutes, or 18 minutes 45 seconds).

---

#### Task ID: EXT-7 — Extension Task (Optional Challenge)
*Source:* `lesson6_7_8_student_materials.md`  
*Given Information:* Tank A finishes at 14 minutes. Tank B starts at 320 gallons and must empty ($V = 0$) in exactly 14 minutes.

- Required draining rate:
  $$m = \frac{0 - 320}{14 - 0} = -\frac{320}{14} = -\frac{160}{7} = -22\frac{6}{7}\text{ gallons per minute} \approx -22.86\text{ gal/min}$$
- **Answer:** Draining rate of $\frac{160}{7}$ gallons per minute (or $22\frac{6}{7}\text{ gal/min} \approx 22.86\text{ gal/min}$; slope $m = -\frac{160}{7}\text{ gal/min}$).

---

#### Task ID: PRAC-7 — Selectable / Optional Practice Problems
*Source:* `lesson6_7_8_student_materials.md`

**Problem 1: Descending Hot-Air Balloon**
- Points given: $(3, 580)$ and $(8, 380)$
- Rate of descent:
  $$m = \frac{380 - 580}{8 - 3} = \frac{-200}{5} = -40\text{ meters per minute}$$
  **Answer:** $-40$ meters per minute (or descent rate of $40$ m/min).
- Initial altitude ($t = 0$):
  $$b = 580 - (-40)(3) = 580 + 120 = 700\text{ meters}$$
  **Answer:** $b = 700$ meters.
- Altitude equation:
  **Answer:** $A = -40t + 700$ (or $A = 700 - 40t$)
- Total descent time to ground ($A = 0$):
  $$-40t + 700 = 0 \implies 40t = 700 \implies t = 17.5\text{ minutes}$$
  **Answer:** $t = 17.5$ minutes (or 17 minutes 30 seconds).

**Problem 2: Cooling Soup**
- Initial temperature $190^\circ\text{F}$, cooling rate $2.5^\circ\text{F}$/min.
- Equation:
  **Answer:** $T = -2.5m + 190$ (or $T = 190 - 2.5m$)
- Temperature after 24 minutes:
  $$T(24) = 190 - 2.5(24) = 190 - 60 = 130^\circ\text{F}$$
  **Answer:** $T = 130^\circ\text{F}$
- Time to reach target serving temperature $115^\circ\text{F}$:
  $$190 - 2.5m = 115 \implies 2.5m = 75 \implies m = \frac{75}{2.5} = 30\text{ minutes}$$
  **Answer:** $m = 30$ minutes.

---

### LESSON 8: Constructing Linear Functions from Scaled Coordinate Graphs

#### Task ID: TASK-8.1 — Launch: The "Counting Squares" Trap
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `task8_1_trap_sketch.svg` (Figure 8.0)

- **Student Claim:** *"It goes up 2 grid squares and right 1 grid square, so the slope must be $\frac{2}{1} = 2$."*
- **Grid Scale Information:** 1 horizontal square = 5 hours; 1 vertical square = 50 miles.
- **Why is counting grid boxes as 1 unit dangerous?**
  Grid squares represent visual increments on the page, not actual mathematical units of the variables. Because the horizontal scale is 5 hours per grid box and the vertical scale is 50 miles per grid box, the physical change represented by 1 visual unit on the y-axis is 10 times larger than on the x-axis. Counting grid boxes assumes an isotropic $1:1$ unit grid, leading to an answer that is off by an order of magnitude.
- **How should the student determine the true rate of change?**
  Multiply the number of grid boxes by their physical unit scale (or compute the coordinate difference from the axis labels):
  $$\Delta \text{Distance} = 2\text{ vertical boxes} \times 50\text{ miles/box} = 100\text{ miles}$$
  $$\Delta \text{Time} = 1\text{ horizontal box} \times 5\text{ hours/box} = 5\text{ hours}$$
  $$\text{True Rate of Change} = \frac{100\text{ miles}}{5\text{ hours}} = 20\text{ miles per hour}$$

---

#### Task ID: TASK-8.2 — Core Investigation: Reading Scaled Coordinate Graphs
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `lesson8_scaled_graphs.svg` (Figure 8.1)

**Part 1: Graph 8A — Drone Ascent Over Time**
1. **Identify Axes and Grid Scales:**
   - Horizontal axis ($x$): Quantity = **Time** (or Elapsed Time), Unit = **minutes**
   - Each single vertical grid line represents: **$1$ minute**  
     *(Check: Labeled ticks occur at intervals of 2 min: $0, 2, 4, 6, 8, 10, 12$. A dotted grid line is centered between every pair of numbered ticks, giving $\frac{2}{2} = 1\text{ min/line}$.)*
   - Vertical axis ($y$): Quantity = **Altitude**, Unit = **meters**
   - Each single horizontal grid line represents: **$25$ meters**  
     *(Check: Labeled ticks occur every 50 m: $0, 50, 100, 150, 200, 250, 300$. A dotted grid line is centered between each pair, giving $\frac{50}{2} = 25\text{ m/line}$.)*
2. **Identify Initial Value ($b$):**
   - Vertical intercept: Point $(0, 50)$ marked on the vertical axis.
   - Initial altitude at $t = 0$: **$b = 50$ meters**.
   - Physical meaning: When altitude recording began, the drone was already 50 meters above the reference ground level.
3. **Determine Rate of Change using Slope Triangle:**
   - Shaded slope triangle between $(2, 100)$ and $(6, 200)$:
     - $\Delta t = 6 - 2 = 4$ minutes
     - $\Delta A = 200 - 100 = 100$ meters
     - Rate of change: $m = \frac{100}{4} = 25$ meters per minute.
   - **Error Check Explanation:**  
     Visually, the triangle spans 4 vertical grid boxes ($4 \times 25\text{ m} = 100\text{ m}$) and 4 horizontal grid boxes ($4 \times 1\text{ min} = 4\text{ min}$). Counting boxes blindly yields $\frac{4\text{ boxes}}{4\text{ boxes}} = 1$, which ignores that 1 vertical box is 25 meters while 1 horizontal box is 1 minute.
4. **Construct the Equation:**
   - Equation: **$A = 25t + 50$**
   - Altitude at $t = 11$ minutes:
     $$A(11) = 25(11) + 50 = 275 + 50 = 325\text{ meters}$$
     **Answer:** $A(11) = 325$ meters.

**Part 2: Graph 8B — Delivery Truck Fuel Remaining**
1. **Identify Axes and Grid Scales:**
   - Horizontal axis: Quantity = **Distance Traveled**, Unit = **miles**
   - Each vertical grid line represents: **$20$ miles**  
     *(Check: Major numbered ticks are $0, 40, 80, 120, 160, 200, 240$. With one sub-grid line halfway between each tick, each line represents 20 miles.)*
   - Vertical axis: Quantity = **Fuel Remaining**, Unit = **gallons**
   - Each horizontal grid line represents: **$5$ gallons**  
     *(Check: Numbered ticks are $0, 5, 10, 15, 20, 25, 30$ with grid lines directly aligning with these values.)*
2. **Identify Initial Value ($b$):**
   - Vertical intercept: $(0, 24)$
   - Initial fuel in tank: **$b = 24$ gallons**
3. **Determine Rate of Change using Slope Triangle:**
   - Slope triangle between $(40, 20)$ and $(120, 12)$:
     - $\Delta d = 120 - 40 = 80$ miles
     - $\Delta F = 12 - 20 = -8$ gallons
     - Rate of change: $m = \frac{-8}{80} = -\frac{1}{10}$ gallons per mile
     - Decimal representation: **$m = -0.1$ gallons/mile**
   - Driver interpretation: The delivery truck burns 0.1 gallons of fuel for every 1 mile driven (consumption rate of 0.1 gal/mi).
4. **Construct Equation and Interpret Intercept:**
   - Linear function equation: **$F = -0.1d + 24$** (or $F = 24 - 0.1d$)
   - Meaning of point $(240, 0)$: At a distance of 240 miles, the fuel tank has 0 gallons remaining (completely empty). 240 miles is the vehicle's driving range on a full tank.

---

#### Task ID: CFU-8 — Independent Check for Understanding (Exit Ticket 8)
*Source:* `lesson6_7_8_student_materials.md`  
*Visual Reference:* `cfu8_snow_graph.svg` (Figure 8.2)

1. **Read Initial Value ($b$):**
   - Point $P_0$ is marked on the vertical axis at tick 6.
   - Coordinates: **$(0, 6)$**
   - Initial snow depth: **$b = 6$ inches**
2. **Read Coordinates and Determine Snowfall Rate ($m$):**
   - *Mathematical Analysis of the Line:*  
     The line passes through grid intersection $P_0(0, 6)$ and grid intersection $P_3(12, 36)$.
     $$m = \frac{36 - 6}{12 - 0} = \frac{30}{12} = 2.5\text{ inches per hour}$$
     Along this line:
     - At $t = 4$: $S = 6 + 2.5(4) = 16 \implies P_1 = (4, 16)$
     - At $t = 8$: $S = 6 + 2.5(8) = 26 \implies P_2 = (8, 26)$
   - *Independent Reading Ambiguity / Anomaly in Figure 8.2:*  
     The vertical grid lines are drawn at intervals of 3 ($0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36$). Unlike Figure 8.1, where coordinates are printed directly next to points, Figure 8.2 prints only the letter labels $P_1$ and $P_2$. 
     - $P_1$ is located at $(4, 16)$, which sits between grid lines 15 and 18.
     - $P_2$ is located at $(8, 26)$, which sits between grid lines 24 and 27.
     - **Plausible Student Readings:**
       - **Canonical/Exact Mathematical Reading:** $P_1 = (4, 16)$, $P_2 = (8, 26)$.  
         $$m = \frac{26 - 16}{8 - 4} = \frac{10}{4} = 2.5\text{ inches per hour}$$
       - **Approximate Visual Grid Estimate:** A student estimating to the nearest visual grid increment might approximate $P_1 \approx (4, 15)$ or $(4, 16)$, and $P_2 \approx (8, 26)$ or $(8, 27)$, yielding rates between $2.25$ and $3.0$ in/hr if they do not derive $m = 2.5$ from $(0, 6)$ and $(12, 36)$.
     - **Canonical Answer:** $P_1 = (4, 16)$, $P_2 = (8, 26)$, Rate $m = 2.5$ inches per hour.
3. **Construct Function Equation:**
   - **Answer:** $S = 2.5t + 6$ (or $S = \frac{5}{2}t + 6$)
4. **Predict Depth after 15 Hours:**
   $$S(15) = 2.5(15) + 6 = 37.5 + 6 = 43.5\text{ inches}$$
   - **Answer:** $43.5$ inches (or $43\frac{1}{2}$ inches).  
   *(Note: 43.5 inches exceeds the top of the visible vertical axis, testing algebraic extrapolation beyond the grid boundaries).*

---

#### Task ID: EXT-8 — Extension Task (Optional Challenge)
*Source:* `lesson6_7_8_student_materials.md`

1. **Convert Rate of Change to Miles Per Gallon (mpg):**
   - The fuel consumption rate is $-0.1$ gallons per mile.
   - To travel on 1 gallon of fuel:
     $$\text{Fuel Economy} = \frac{1}{|m|} = \frac{1\text{ mile}}{0.1\text{ gallon}} = 10\text{ miles per gallon (mpg)}$$
   - **Answer:** The truck gets $10$ mpg (it travels $10$ miles per $1$ gallon of fuel).
2. **Auxiliary 15-Gallon Tank Analysis (Initial Fuel $24 + 15 = 39$ gallons):**
   - **Vertical Intercept:** Changes. It increases from $(0, 24)$ to $(0, 39)$.
   - **Slope (Rate of Change):** Does not change. The engine fuel consumption rate remains constant at $-0.1$ gallons per mile.
   - **Graph transformation:** The line shifts vertically upward by 15 units (parallel translation). The new horizontal intercept is $d = \frac{39}{0.1} = 390$ miles.

---

#### Task ID: PRAC-8 — Selectable / Optional Practice Problems
*Source:* `lesson6_7_8_student_materials.md`

**Problem 1: Custom T-Shirt Cost Model**
- Given points: $(0, 75)$ and $(20, 235)$
- Constant cost per shirt:
  $$m = \frac{235 - 75}{20 - 0} = \frac{160}{20} = 8\text{ dollars per shirt}$$
  **Answer:** $m = 8$ dollars per shirt.
- Function equation:
  **Answer:** $C = 8n + 75$
- Total cost for 80 shirts:
  $$C(80) = 8(80) + 75 = 640 + 75 = 715\text{ dollars}$$
  **Answer:** $715$ dollars.

**Problem 2: Hiker Canyon Descent**
- Given points: $(15, 720)$ and $(45, 360)$
- Rate of descent:
  $$m = \frac{360 - 720}{45 - 15} = \frac{-360}{30} = -12\text{ feet per minute}$$
  **Answer:** $-12$ feet per minute (or descent rate of $12$ ft/min).
- Elevation at trailhead ($t = 0$):
  $$b = 720 - (-12)(15) = 720 + 180 = 900\text{ feet}$$
  **Answer:** $b = 900$ feet.
- Function equation:
  **Answer:** $E = -12t + 900$ (or $E = 900 - 12t$)
- Arrival time at canyon river ($E = 0$):
  $$-12t + 900 = 0 \implies 12t = 900 \implies t = \frac{900}{12} = 75\text{ minutes}$$
  **Answer:** $t = 75$ minutes (or 1 hour 15 minutes).

---

## 3. Visual Artifact and Textual Consistency Audit

### 3.1 Figure 7.1: `lesson7_reservoir_models.svg`
- **Referenced in:** TASK-7.1, TASK-7.2, TASK-7.3.
- **Textual Condition Check:**
  - Tank A: Passes through $(0, 40)$, $(4, 100)$, $(8, 160)$, $(12, 220)$, $(14, 250)$. Line becomes horizontal dashed from $t = 14$ to $t = 18$ at $V = 250$. All points match student text exactly.
  - Tank B: Passes through $(0, 320)$, $(4, 240)$, $(8, 160)$, $(12, 80)$, $(16, 0)$. Stops at $t = 16$. Matches student text exactly.
  - Intersection: Highlighted at $(8, 160)$ with open-ring marker labeled `"Shared: (8, 160)"`.
- **Finding:** Fully compliant. Graph mathematically and visually satisfies all task questions.

### 3.2 Figure 8.0: `task8_1_trap_sketch.svg`
- **Referenced in:** TASK-8.1.
- **Textual Condition Check:**
  - Triangle base: 1 grid box horizontally (from $t = 0$ to $t = 5$, representing 5 hours).
  - Triangle height: 2 grid boxes vertically (from $d = 0$ to $d = 100$, representing 100 miles).
  - Callout box accurately quotes student misconception: `"It goes up 2 boxes & right 1 box, so the slope must be 2 / 1 = 2 !"`.
- **Graphic Anomaly Identified:**
  - **Visual Text Collision:** At the bottom horizontal axis, the red text annotation `"1 grid box right"` is placed directly over the numerical tick label `"5"`. While legible from context, this is a minor graphic rendering collision.

### 3.3 Figure 8.1: `lesson8_scaled_graphs.svg`
- **Referenced in:** TASK-8.2.
- **Textual Condition Check:**
  - Graph 8A:
    - Points: $(0, 50), (2, 100), (6, 200), (10, 300)$.
    - Slope triangle: Marked between $(2, 100)$ and $(6, 200)$ with labels $\Delta t = 4\text{ min}$ and $\Delta A = 100\text{ m}$.
    - Grid lines: Vertical grid lines at $1$ min intervals; horizontal grid lines at $25$ m intervals.
  - Graph 8B:
    - Points: $(0, 24), (40, 20), (120, 12), (200, 4), (240, 0)$.
    - Slope triangle: Marked between $(40, 20)$ and $(120, 12)$ with labels $\Delta d = 80\text{ mi}$ and $\Delta F = -8\text{ gal}$.
    - Grid lines: Vertical grid lines at $20$ mi intervals; horizontal grid lines at $5$ gal intervals.
- **Finding:** Fully compliant. The labeled points prevent any ambiguity regarding non-integer or off-grid values.

### 3.4 Figure 8.2: `cfu8_snow_graph.svg`
- **Referenced in:** CFU-8.
- **Textual Condition Check:**
  - Line passes through $(0, 6)$ and $(12, 36)$.
- **Critical Graphic and Didactic Anomalies Identified:**
  1. **Non-Grid Coordinates for Points $P_1$ and $P_2$ Without Numerical Callouts:**
     - The vertical axis has ticks at $0, 6, 12, 18, 24, 30, 36$ and dotted sub-grid lines at multiples of $3$ ($3, 9, 15, 21, 27, 33$).
     - The line has slope $m = 2.5$. Thus $P_1$ is at $(4, 16)$ and $P_2$ is at $(8, 26)$.
     - Neither $16$ nor $26$ lies on a grid line ($16$ is $\frac{1}{3}$ between $15$ and $18$; $26$ is $\frac{2}{3}$ between $24$ and $27$).
     - CFU-8 Question 2 commands: *"Read the coordinate values of point $P_1$ and point $P_2$ from the grid axes"*. Because no numerical coordinate labels are provided on the diagram (unlike Figure 8.1), an 8th-grade student attempting to read the grid directly faces visual ambiguity and may misread or approximate the values (e.g., guessing $(4, 15)$ or $(8, 27)$).
  2. **Vertical Axis Top Tick Mislabeled (`40` vs. `42`):**
     - The vertical axis ticks increase by uniform intervals of 6: $0, 6, 12, 18, 24, 30, 36$.
     - The top labeled tick is labeled **`40`**, which is an increment of only 4 units above 36. Following the established grid scale, this tick should be **`42`**.
  3. **Extrapolation Beyond Visible Axis in Question 4:**
     - Question 4 asks for depth after 15 hours: $S(15) = 43.5$ inches.
     - The vertical axis ends at 40 (or 42), meaning students must use their algebraic equation to solve this item rather than reading it off the chart. (This is mathematically valid as an extrapolation check, but worth noting for test administration).

---

## 4. Comprehensive Task Coverage and Verification Matrix

The following table presents the census audit of all 17 tasks across the student materials, verifying solvability, graphic alignment, and clarity.

| Task ID | Component / Lesson | Independent Solvability | Mathematical Consistency | Units & Values Checked | Graphic Status | Audit Notes / Flags |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **TASK-6.1** | Launch / Lesson 6 | Solvable | Consistent | Verified | N/A (Tables) | Compares unit rate vs. absolute delta; unambiguous. |
| **TASK-6.2** | Core Lab / Lesson 6 | Solvable | Consistent | Verified | N/A (Tables) | Irregular table intervals all yield $m = 4$, $b = 3$. |
| **TASK-6.3** | Partner Practice / L6 | Solvable | Consistent | Verified (gal, min) | N/A (Table) | Decreasing linear function; clean integer intercepts $(0, 180)$ and $(30, 0)$. |
| **CFU-6** | Exit Ticket / Lesson 6 | Solvable | Consistent | Verified (\\$, h) | N/A (Table) | Repair fee model: $m = 9$, $b = 21$, $C(8) = 93$. |
| **EXT-6** | Extension / Lesson 6 | Solvable | Consistent | Verified | N/A (Table) | Smudged table: $y(7) = 39$, $x(89) = 17$. |
| **PRAC-6.1** | Practice 1 / Lesson 6 | Solvable | Consistent | Verified | N/A (Points) | $(5, 65)$ and $(15, 145) \implies y = 8x + 25$, $y(25) = 225$. |
| **PRAC-6.2** | Practice 2 / Lesson 6 | Solvable | Consistent | Verified (%, h) | N/A (Word) | Battery discharge: $m = -4\%/\text{h}$, $b = 98\%$, empty at $24.5$ h. |
| **TASK-7.1** | Launch / Lesson 7 | Descriptive Context | Consistent | Verified | Figure 7.1 checked | Introduces Tank A and Tank B narrative. |
| **TASK-7.2** | Core Lab / Lesson 7 | Solvable | Consistent | Verified (gal, min) | Figure 7.1 checked | Tank A ($15t + 40$) and Tank B ($-20t + 320$) verified. |
| **TASK-7.3** | Core Lab / Lesson 7 | Solvable | Consistent | Verified (gal, min) | Figure 7.1 checked | Capacity at 14 min (flatline), empty at 16 min, cross at $(8, 160)$. |
| **CFU-7** | Exit Ticket / Lesson 7 | Solvable | Consistent | Verified (gal, min) | N/A (Word) | Draining pool: $m = -24$, $b = 450$, empty at $18.75$ min. |
| **EXT-7** | Extension / Lesson 7 | Solvable | Consistent | Verified (gal, min) | N/A (Word) | Synchronized empty rate: $m = -160/7 \approx -22.86$ gal/min. |
| **PRAC-7.1** | Practice 1 / Lesson 7 | Solvable | Consistent | Verified (m, min) | N/A (Word) | Balloon descent: $m = -40$ m/min, $b = 700$ m, ground at $17.5$ min. |
| **PRAC-7.2** | Practice 2 / Lesson 7 | Solvable | Consistent | Verified ($^\circ\text{F}$, min) | N/A (Word) | Soup cooling: $T = -2.5m + 190$, $T(24) = 130^\circ\text{F}$, target at 30 min. |
| **TASK-8.1** | Launch / Lesson 8 | Solvable | Consistent | Verified (mi, h) | Figure 8.0 checked | **Minor visual flag:** Text label collides with tick `"5"`. |
| **TASK-8.2A**| Core Part 1 / Lesson 8 | Solvable | Consistent | Verified (m, min) | Figure 8.1 checked | Drone ascent: $1$ min/line, $25$ m/line, $A(11) = 325$ m. |
| **TASK-8.2B**| Core Part 2 / Lesson 8 | Solvable | Consistent | Verified (gal, mi) | Figure 8.1 checked | Truck fuel: $20$ mi/line, $5$ gal/line, $F = -0.1d + 24$. |
| **CFU-8** | Exit Ticket / Lesson 8 | Partially Ambiguous | Consistent Eq. / Flawed Graph | Verified (in, h) | Figure 8.2 checked | **Major audit flag:** $P_1(4, 16)$ and $P_2(8, 26)$ are off-grid with no numerical labels; top tick labeled `40` instead of `42`. |
| **EXT-8** | Extension / Lesson 8 | Solvable | Consistent | Verified (mpg, gal) | N/A (Word) | Economy = $10$ mpg; auxiliary tank shifts $b$ to $39$, slope unchanged. |
| **PRAC-8.1** | Practice 1 / Lesson 8 | Solvable | Consistent | Verified (\\$, shirts) | N/A (Points) | T-shirts: $C = 8n + 75$, $C(80) = \\$715$. |
| **PRAC-8.2** | Practice 2 / Lesson 8 | Solvable | Consistent | Verified (ft, min) | N/A (Points) | Trail descent: $E = -12t + 900$, river reached at $t = 75$ min. |

---

## 5. Summary of Audit Judgments & Remaining Limits

1. **Independent Readability:** All three lessons provide comprehensive mathematical tasks with consistent units and realistic contextual modeling scenarios.
2. **Pedagogical Integrity of Non-Unit Scales:** Lessons 6, 7, and 8 systematically develop student understanding from unit tables to irregular tables and non-unit scaled coordinate planes.
3. **Artifact-Specific Recommendations for Future Iterations:**
   - In `task8_1_trap_sketch.svg`, adjust the vertical position of the red dimension annotation `"1 grid box right"` to prevent overlapping the tick label `"5"`.
   - In `cfu8_snow_graph.svg`, either (a) print explicit coordinate callouts $(4, 16)$ and $(8, 26)$ beside $P_1$ and $P_2$ as done in Figure 8.1, or (b) adjust the points/grid so that the marked points fall directly on visible grid line intersections, and correct the top tick label from `40` to `42`.
4. **Statement of Limitations:** This report is the output of an autonomous model independent reading check. It does not constitute human teacher classroom testing, peer panel approval, or empirical student error analytics.
