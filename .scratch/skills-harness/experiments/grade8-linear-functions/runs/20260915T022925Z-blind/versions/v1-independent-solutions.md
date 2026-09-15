# Independent Solution and Mathematical Audit Report (v0.1)

**Target Student Material:** `lesson6_7_8_student_materials.md`  
**Accompanying Graphics Inspected:**  
1. `lesson7_reservoir_models.svg`  
2. `lesson8_scaled_graphs.svg`  
**Review Type:** Autonomous Independent Read & Mathematical Verification  
**Evaluation Scope:** Complete inventory coverage of Lessons 6, 7, and 8 student tasks.

---

## Executive Summary & Audit Methodology

This audit was conducted strictly from the student-facing artifacts without access to teacher answer keys, instructional rationale documents, or generation prompts. Every problem was independently solved and checked for:
1. **Mathematical Determinacy:** Whether the task provides sufficient data to uniquely determine the solution.
2. **Numeric and Unit Consistency:** Whether dimensional units, arithmetic operations, and coordinate scales align.
3. **Graphic Fidelity:** Whether referenced SVG diagrams and ASCII sketches accurately match the numerical statements.
4. **Pedagogical and Notational Ambiguities:** Any discrepancies, missing visual artifacts, or accidental information leaks.

---

## 1. Complete Task-by-Task Independent Solutions

### Lesson 6: Constructing Linear Functions from Irregular Tables

---

#### Task ID: TASK-6.1 — Launch: Notice and Wonder with Two Tables

##### 1. Table 1 (Plan A) Analysis
* **Given Data:** $(0, 5), (1, 9), (2, 13), (3, 17)$.
* **Sub-questions & Solutions:**
  * **Increase in $x$ between consecutive rows ($\Delta x$):**
    $$\Delta x = 1 - 0 = 2 - 1 = 3 - 2 = 1$$
    **Answer:** $\Delta x = 1$
  * **Increase in $y$ between consecutive rows ($\Delta y$):**
    $$\Delta y = 9 - 5 = 13 - 9 = 17 - 13 = 4$$
    **Answer:** $\Delta y = 4$
  * **Rate of change:**
    $$\text{Rate} = \frac{\Delta y}{\Delta x} = \frac{4}{1} = 4$$
    **Answer:** $4$ (or $4\text{ units of } y \text{ per unit of } x$)
  * **Initial value ($b = y$ when $x = 0$):**
    Directly read from first row $(0, 5)$:
    **Answer:** $b = 5$
  * **Equation for Table 1:**
    $$y = 4x + 5$$

##### 2. Table 2 (Plan B) Analysis
* **Given Data:** $(2, 11), (5, 23), (8, 35), (14, 59)$.
* **Sub-questions & Solutions:**
  * **Step from Row 1 $(2, 11)$ to Row 2 $(5, 23)$:**
    $$\Delta x = 5 - 2 = 3$$
    $$\Delta y = 23 - 11 = 12$$
    **Answer:** $\Delta x = 3$, $\Delta y = 12$
  * **Step from Row 3 $(8, 35)$ to Row 4 $(14, 59)$:**
    $$\Delta x = 14 - 8 = 6$$
    $$\Delta y = 59 - 35 = 24$$
    **Answer:** $\Delta x = 6$, $\Delta y = 24$
  * **Evaluation of Jordan's Claim:**
    * *Jordan's Claim:* "The outputs jump by 12, and then by 24, so this table cannot be linear."
    * **Independent Assessment:** Disagree with Jordan.
    * **Mathematical Justification:** Linearity requires the *ratio* of change $\frac{\Delta y}{\Delta x}$ (the unit rate of change) to be constant across all intervals, not $\Delta y$ in isolation. 
      - On Interval 1: $\frac{\Delta y}{\Delta x} = \frac{12}{3} = 4$.
      - On Interval 3: $\frac{\Delta y}{\Delta x} = \frac{24}{6} = 4$.
      Because $\Delta x$ doubled from $3$ to $6$, $\Delta y$ also doubled from $12$ to $24$, preserving the constant unit rate of change of $4$.

---

#### Task ID: TASK-6.2 — Core Activity: Determining Rate of Change and Extrapolating the Initial Value

##### 1. Unit Rate of Change ($m$) for Table 2
* **Calculations by Interval:**
  * Interval 1 (from $x = 2$ to $x = 5$):
    $$\frac{\Delta y}{\Delta x} = \frac{23 - 11}{5 - 2} = \frac{12}{3} = 4$$
  * Interval 2 (from $x = 5$ to $x = 8$):
    $$\frac{\Delta y}{\Delta x} = \frac{35 - 23}{8 - 5} = \frac{12}{3} = 4$$
  * Interval 3 (from $x = 8$ to $x = 14$):
    $$\frac{\Delta y}{\Delta x} = \frac{59 - 35}{14 - 8} = \frac{24}{6} = 4$$
* **Constant Rate Determination:**
  * Is the rate of change constant? **Yes.**
  * Value of $m$: **$m = 4$**.

##### 2. Finding the Initial Value ($b$)
* **Extrapolation Method:**
  * Point used: $(2, 11)$, constant rate $m = 4$.
  * *Method A (Algebraic substitution):*
    $$y = mx + b \implies 11 = 4(2) + b \implies 11 = 8 + b \implies b = 3$$
  * *Method B (Stepping back to $x = 0$):*
    $$\Delta x = 0 - 2 = -2 \implies \Delta y = m \cdot \Delta x = 4(-2) = -8 \implies y(0) = 11 - 8 = 3$$
* **Initial Value:** $b = 3$.
* **Complete Linear Function Equation:**
  $$y = 4x + 3$$

##### 3. Verification
* Test with point $(14, 59)$:
  $$y(14) = 4(14) + 3 = 56 + 3 = 59$$
  The calculated value matches the table entry $y = 59$.

---

#### Task ID: TASK-6.3 — Partner Practice: A Decreasing Relationship

* **Given Context & Table:** Remaining volume $W$ (gallons) at time $t$ (minutes).
  * Data: $(4, 156), (9, 126), (15, 90), (22, 48)$.

1. **Rate of change between $(4, 156)$ and $(9, 126)$:**
   $$\frac{\Delta W}{\Delta t} = \frac{126 - 156}{9 - 4} = \frac{-30}{5} = -6\text{ gallons per minute}$$
   **Answer:** $-6\text{ gal/min}$ (or $-6\text{ gallons per minute}$)

2. **Rate of change between $(15, 90)$ and $(22, 48)$:**
   $$\frac{\Delta W}{\Delta t} = \frac{48 - 90}{22 - 15} = \frac{-42}{7} = -6\text{ gallons per minute}$$
   **Answer:** $-6\text{ gal/min}$

3. **Interpretation of Negative Sign:**
   * **Mathematical meaning:** $W$ is a strictly decreasing function of $t$.
   * **Contextual meaning:** The cooling tank is losing water over time at a steady rate of $6$ gallons every minute (e.g., draining, evaporation, or cooling consumption).

4. **Initial Water Volume ($t = 0$):**
   * Using point $(4, 156)$ and $m = -6$:
     $$W(0) = 156 - (-6)(4) = 156 + 24 = 180\text{ gallons}$$
     *(Alternatively: $156 = -6(4) + b \implies 156 = -24 + b \implies b = 180$)*
   * **Answer:** $b = 180\text{ gallons}$

5. **Equation Relating $W$ and $t$:**
   $$W = -6t + 180 \quad (\text{or } W = 180 - 6t)$$

6. **Time to Empty Tank ($W = 0$):**
   $$0 = -6t + 180 \implies 6t = 180 \implies t = \frac{180}{6} = 30\text{ minutes}$$
   **Answer:** $30\text{ minutes}$

---

#### Task ID: CFU-6 — Independent Check for Understanding (Exit Ticket 6)

* **Given Data:** $(4, 57), (9, 102), (15, 156)$. Total charge $C$ ($) for labor time $h$ (hours).

1. **Hourly Labor Rate ($m$):**
   $$m = \frac{102 - 57}{9 - 4} = \frac{45}{5} = 9\text{ dollars per hour}$$
   *(Verification on second interval: $\frac{156 - 102}{15 - 9} = \frac{54}{6} = 9$)*
   **Answer:** $m = 9\text{ dollars per hour}$

2. **Fixed Home-Visit Fee ($b$):**
   $$C = mh + b \implies 57 = 9(4) + b \implies 57 = 36 + b \implies b = 21$$
   **Answer:** $b = \$21$

3. **Linear Equation for $C$ in terms of $h$:**
   $$C = 9h + 21 \quad (\text{or } C = 21 + 9h)$$

4. **Total Charge for 8-Hour Job:**
   $$C(8) = 9(8) + 21 = 72 + 21 = 93$$
   **Answer:** $\text{Total} = \$93$

---

#### Task ID: EXT-6 — Extension Task (Optional Challenge)

* **Given Table with Smudged Values:**
  * $x$: $3$, $7$, $12$, $?$
  * $y$: $19$, $?$, $64$, $89$

1. **Determine Rate of Change $m$ and Initial Value $b$:**
   * Using complete pairs $(3, 19)$ and $(12, 64)$:
     $$m = \frac{64 - 19}{12 - 3} = \frac{45}{9} = 5$$
     $$b = 19 - 5(3) = 19 - 15 = 4$$
   * **Answer:** $m = 5$, $b = 4$ (Equation: $y = 5x + 4$)

2. **Determine the Missing Values:**
   * Missing $y$-value at $x = 7$:
     $$y = 5(7) + 4 = 35 + 4 = 39$$
   * Missing $x$-value at $y = 89$:
     $$89 = 5x + 4 \implies 5x = 85 \implies x = 17$$
   * **Answer:** Smudged output at $x = 7$ is $39$; smudged input at $y = 89$ is $17$.

---

#### Task ID: PRAC-6 — Independent Practice Problems (Lesson 6)

##### Problem 1
* **Given Points:** $(5, 65)$ and $(15, 145)$.
  * **Rate of change $m$:**
    $$m = \frac{145 - 65}{15 - 5} = \frac{80}{10} = 8$$
  * **Initial value $b$:**
    $$b = 65 - 8(5) = 65 - 40 = 25$$
  * **Function rule:**
    $$y = 8x + 25$$
  * **Output when $x = 25$:**
    $$y(25) = 8(25) + 25 = 200 + 25 = 225$$

##### Problem 2
* **Given Points:** $(6, 74\%)$ and $(14, 42\%)$ for remaining battery charge $P$ at time $t$ (hours).
  * **Hourly discharge rate:**
    $$m = \frac{42 - 74}{14 - 6} = \frac{-32}{8} = -4\% \text{ per hour}$$
    **Answer:** $-4\%\text{ per hour}$ (or a discharge rate of $4\%\text{ per hour}$)
  * **Battery percentage at $t = 0$:**
    $$P(0) = 74 - (-4)(6) = 74 + 24 = 98\%$$
    **Answer:** $98\%$
  * **Equation for $P$ in terms of $t$:**
    $$P = -4t + 98 \quad (\text{or } P = 98 - 4t)$$
  * **Hour when battery is completely dead ($P = 0\%$):**
    $$0 = -4t + 98 \implies 4t = 98 \implies t = \frac{98}{4} = 24.5\text{ hours}$$
    **Answer:** $t = 24.5\text{ hours}$ (or $24\text{ hours } 30\text{ minutes}$)

---
---

### Lesson 7: Contextual Modeling: Filling and Draining Systems

---

#### Task ID: TASK-7.1 — Launch: Two Tanks, Two Stories
* Contextual setup linking Tank A (filling, solid line) and Tank B (draining, dashed line) to Figure 7.1 (`lesson7_reservoir_models.svg`).
* No independent calculation requested; operationalized in TASK-7.2 and TASK-7.3.

---

#### Task ID: TASK-7.2 — Core Modeling Lab: Tank A and Tank B

##### Part 1: Tank A (The Filling Tank — Solid Line)
1. **Initial Volume ($b_A$):**
   * Graph crosses vertical axis at point $A_0(0, 40)$.
   * **Answer:** $b_A = 40\text{ gallons}$
   * **Physical meaning:** Tank A already contained $40$ gallons of water at the start of the morning observation ($t = 0$) before pumping began.
2. **Filling Rate (Slope $m_A$):**
   * Two marked points: $(4, 100)$ and $(12, 220)$.
   * $\Delta t = 12 - 4 = 8\text{ minutes}$.
   * $\Delta V = 220 - 100 = 120\text{ gallons}$.
   * Rate of change:
     $$m_A = \frac{\Delta V}{\Delta t} = \frac{120}{8} = 15\text{ gallons per minute}$$
   * **Interpretation:** Water is being pumped into Tank A at a constant rate of $15$ gallons every minute.
3. **Linear Function for Tank A:**
   $$V_A = 15t + 40 \quad (\text{or } V_A = 40 + 15t)$$

##### Part 2: Tank B (The Draining Tank — Dashed Line)
4. **Initial Volume ($b_B$):**
   * Graph crosses vertical axis at point $B_0(0, 320)$.
   * **Answer:** $b_B = 320\text{ gallons}$
   * **Physical meaning:** Tank B was filled to its starting capacity of $320$ gallons of water at $t = 0$ before draining commenced.
5. **Draining Rate (Slope $m_B$):**
   * Two marked points: $(4, 240)$ and $(12, 80)$.
   * $\Delta t = 12 - 4 = 8\text{ minutes}$.
   * $\Delta V = 80 - 240 = -160\text{ gallons}$.
   * Rate of change:
     $$m_B = \frac{\Delta V}{\Delta t} = \frac{-160}{8} = -20\text{ gallons per minute}$$
   * **Interpretation:** The rate is negative because water is leaving the tank (volume is decreasing) at $20$ gallons per minute.
6. **Linear Function for Tank B:**
   $$V_B = -20t + 320 \quad (\text{or } V_B = 320 - 20t)$$

---

#### Task ID: TASK-7.3 — Realistic Constraints and Intersection Analysis

1. **Maximum Capacity of Tank A:**
   * Safety shut-off valve triggers at $V = 250\text{ gallons}$.
     $$15t + 40 = 250 \implies 15t = 210 \implies t = \frac{210}{15} = 14\text{ minutes}$$
   * **Answer:** $t = 14\text{ minutes}$
   * **Observation of Graph between $t = 14$ and $t = 18$:**
     In Figure 7.1, from $t = 14$ to $t = 18$, the line turns into a horizontal dashed gray segment at $V = 250$. The volume remains constant at $250$ gallons because the shut-off valve has halted inflow.

2. **Emptying of Tank B:**
   * Tank empty condition ($V_B = 0$):
     $$320 - 20t = 0 \implies 20t = 320 \implies t = 16\text{ minutes}$$
   * **Answer:** $t = 16\text{ minutes}$
   * **Practical Domain:** From $t = 0$ to $t = 16\text{ minutes}$ (interval $[0, 16]$).

3. **Point of Intersection $(8, 160)$:**
   * **Representation of $t = 8$:** At $8$ minutes into the operation, both tanks contain the exact same volume of water.
   * **Representation of $V = 160$:** The shared water volume in each tank at that moment is $160$ gallons.
   * **Verification:**
     * Tank A: $V_A = 15(8) + 40 = 120 + 40 = 160\text{ gallons}$ (Verified)
     * Tank B: $V_B = 320 - 20(8) = 320 - 160 = 160\text{ gallons}$ (Verified)

---

#### Task ID: CFU-7 — Independent Check for Understanding (Exit Ticket 7)

* **Given Data:** Filtration pool initial volume $450$ gallons; $(5, 330)$ and $(12, 162)$.

1. **Constant Draining Rate (Rate of Change $m$):**
   $$m = \frac{162 - 330}{12 - 5} = \frac{-168}{7} = -24\text{ gallons per minute}$$
   **Answer:** $-24\text{ gallons per minute}$ (or draining rate of $24\text{ gal/min}$)

2. **Initial Volume $b$:**
   Explicitly stated in prompt ($450\text{ gal}$) and verified: $330 - (-24)(5) = 330 + 120 = 450$.
   **Answer:** $b = 450\text{ gallons}$

3. **Linear Equation:**
   $$V = -24t + 450 \quad (\text{or } V = 450 - 24t)$$

4. **Time to Completely Empty ($V = 0$):**
   $$450 - 24t = 0 \implies 24t = 450 \implies t = \frac{450}{24} = \frac{75}{4} = 18.75\text{ minutes}$$
   **Answer:** $t = 18.75\text{ minutes}$ (or $18\text{ minutes } 45\text{ seconds}$)

---

#### Task ID: EXT-7 — Extension Task (Optional Challenge)

* **Problem Statement:** Tank B starts at $320$ gallons. Find the draining rate such that Tank B empties ($V_B = 0$) at the exact same minute Tank A reaches capacity ($t = 14\text{ minutes}$).
* **Solution:**
  Let $r$ be the draining rate (gallons per minute):
  $$320 - 14r = 0 \implies 14r = 320 \implies r = \frac{320}{14} = \frac{160}{7} \approx 22.86\text{ gallons per minute}$$
* **Answer:** $\frac{160}{7}\text{ gal/min}$ (or $22\frac{6}{7}\text{ gal/min} \approx 22.86\text{ gal/min}$).  
  *(As a slope / rate of change: $m = -\frac{160}{7}\text{ gal/min}$)*

---

#### Task ID: PRAC-7 — Independent Practice Problems (Lesson 7)

##### Problem 1 (Hot-Air Balloon Descent)
* **Given Points:** $(3, 580)$ and $(8, 380)$ for altitude $A$ (meters) at time $t$ (minutes).
  * **Rate of change:**
    $$m = \frac{380 - 580}{8 - 3} = \frac{-200}{5} = -40\text{ meters per minute}$$
    **Answer:** $-40\text{ m/min}$ (descent speed is $40\text{ m/min}$)
  * **Initial altitude ($t = 0$):**
    $$A(0) = 580 - (-40)(3) = 580 + 120 = 700\text{ meters}$$
    **Answer:** $700\text{ meters}$
  * **Equation:**
    $$A = -40t + 700 \quad (\text{or } A = 700 - 40t)$$
  * **Time to touch ground ($A = 0$):**
    $$700 - 40t = 0 \implies 40t = 700 \implies t = \frac{700}{40} = 17.5\text{ minutes}$$
    **Answer:** $17.5\text{ minutes}$ (or $17\text{ minutes } 30\text{ seconds}$)

##### Problem 2 (Soup Cooling)
* **Given Data:** Initial temperature $T(0) = 190^\circ\text{F}$, cooling rate $2.5^\circ\text{F/min}$ for $m \le 40$.
  * **Equation for temperature $T$ after $m$ minutes:**
    $$T = -2.5m + 190 \quad (\text{or } T = 190 - 2.5m)$$
  * **Temperature after 24 minutes:**
    $$T(24) = 190 - 2.5(24) = 190 - 60 = 130^\circ\text{F}$$
    **Answer:** $130^\circ\text{F}$
  * **Time to reach target serving temperature $115^\circ\text{F}$:**
    $$115 = 190 - 2.5m \implies 2.5m = 75 \implies m = \frac{75}{2.5} = 30\text{ minutes}$$
    **Answer:** $30\text{ minutes}$ (valid since $30 \le 40$)

---
---

### Lesson 8: Constructing Linear Functions from Scaled Coordinate Graphs

---

#### Task ID: TASK-8.1 — Launch: The "Counting Squares" Trap

* **Given Scenario:** Student counts $2$ grid squares up and $1$ grid square right and claims slope is $\frac{2}{1} = 2$. Horizontal axis is scaled in hours ($0, 5, 10, 15\dots$); vertical axis is scaled in miles ($0, 50, 100, 150\dots$).
* **Questions & Solutions:**
  * **Why is counting grid boxes dangerous?**  
    Counting squares treats every grid box as having an aspect ratio of $1\text{ unit} : 1\text{ unit}$. When axes have non-unit or different scales, $1$ grid square does not equal $1$ physical unit. In this scenario:
    - $1$ vertical grid square $= 50\text{ miles}$.
    - $1$ horizontal grid square $= 5\text{ hours}$.
    Relying on raw box counts ignores physical dimensional scaling.
  * **How should the student find the true rate of change?**  
    The student must multiply box counts by their respective scale values, or identify coordinate pairs $(t_1, d_1)$ and $(t_2, d_2)$ from the axis markings:
    $$\Delta d = 2\text{ boxes} \times 50\text{ miles/box} = 100\text{ miles}$$
    $$\Delta t = 1\text{ box} \times 5\text{ hours/box} = 5\text{ hours}$$
    $$\text{Rate of change} = \frac{\Delta d}{\Delta t} = \frac{100\text{ miles}}{5\text{ hours}} = 20\text{ miles per hour}$$
    The true rate is $20\text{ mph}$, not $2$.

---

#### Task ID: TASK-8.2 — Core Investigation: Reading Scaled Coordinate Graphs

##### Part 1: Graph 8A — Drone Ascent Over Time (Figure 8.1)
1. **Axes and Grid Scales:**
   * Horizontal axis quantity and unit: **Time $t$ (minutes)**
   * Each single vertical grid line on the horizontal axis represents: **$1$ minute**  
     *(Check: Between $t = 0$ and $t = 2$, there is an unnumbered vertical grid line at $t = 1$; grid lines occur at $1, 2, 3, \dots, 12$)*
   * Vertical axis quantity and unit: **Altitude $A$ (meters)**
   * Each single horizontal grid line on the vertical axis represents: **$25$ meters**  
     *(Check: Between $A = 0$ and $A = 50$, there is a horizontal grid line at $A = 25$; grid lines occur at $25, 50, 75, \dots, 300$)*
2. **Initial Value ($b$):**
   * Coordinates of vertical intercept: **$(0, 50)$**
   * Initial altitude at $t = 0$: **$b = 50\text{ meters}$**
   * Physical meaning: The drone was launched from an elevated platform, rooftop, or hillside $50$ meters above ground level.
3. **Rate of Change via Slope Triangle:**
   * Given triangle between $(2, 100)$ and $(6, 200)$:
     - $\Delta t = 6 - 2 = 4\text{ minutes}$
     - $\Delta A = 200 - 100 = 100\text{ meters}$
   * Rate of change (climb speed):
     $$m = \frac{\Delta A}{\Delta t} = \frac{100\text{ m}}{4\text{ min}} = 25\text{ meters per minute}$$
   * **Error Check Explanation:**  
     On the physical grid, the triangle spans $4$ grid squares vertically (from $y = 100$ to $200$, each square being $25\text{ m}$) and $4$ grid squares horizontally (from $t = 2$ to $6$, each square being $1\text{ min}$). A student counting boxes gets $\frac{4}{4} = 1$, which represents "boxes per box", not meters per minute. The true rate is $\frac{4 \text{ boxes} \times 25\text{ m/box}}{4 \text{ boxes} \times 1\text{ min/box}} = 25\text{ m/min}$.
4. **Equation and Extrapolation:**
   * Linear function equation:
     $$A = 25t + 50 \quad (\text{or } A = 50 + 25t)$$
   * Altitude at $t = 11\text{ minutes}$:
     $$A(11) = 25(11) + 50 = 275 + 50 = 325\text{ meters}$$

##### Part 2: Graph 8B — Delivery Truck Fuel Remaining (Figure 8.1)
1. **Axes and Grid Scales:**
   * Horizontal axis quantity and unit: **Distance Traveled $d$ (miles)**
   * Each vertical grid line represents: **$20$ miles**  
     *(Check: Distance axis has tick labels every $40\text{ mi}$ with an intermediate grid line at $20\text{ mi}$)*
   * Vertical axis quantity and unit: **Fuel Remaining $F$ (gallons)**
   * Each horizontal grid line represents: **$2.5$ gallons**  
     *(Check: Fuel axis has tick labels every $5\text{ gal}$ with an intermediate grid line at $2.5\text{ gal}$)*
2. **Initial Value ($b$):**
   * Coordinates of vertical intercept: **$(0, 24)$**
   * Initial fuel in tank: **$b = 24\text{ gallons}$**
3. **Rate of Change via Slope Triangle:**
   * Triangle between $(40, 20)$ and $(120, 12)$:
     - $\Delta d = 120 - 40 = 80\text{ miles}$
     - $\Delta F = 12 - 20 = -8\text{ gallons}$
   * Rate of change:
     $$m = \frac{\Delta F}{\Delta d} = \frac{-8}{80} = -\frac{1}{10}\text{ gallons per mile} = -0.1\text{ gallons per mile}$$
   * Contextual meaning: The truck consumes $0.1$ gallons of fuel for every $1$ mile traveled (or consumes $1$ gallon per $10$ miles).
4. **Equation and Intercept Interpretation:**
   * Linear function equation:
     $$F = -0.1d + 24 \quad \left(\text{or } F = -\frac{1}{10}d + 24\right)$$
   * Meaning of point $(240, 0)$:  
     After driving $240$ miles, the fuel tank has $0$ gallons remaining (the truck runs out of fuel; $240$ miles is the maximum driving range on this tank).

---

#### Task ID: CFU-8 — Independent Check for Understanding (Exit Ticket 8)

* **Given ASCII Graph:** Snow Depth $S$ (inches) vs. time $t$ (hours).  
  Labeled points: $(0, 6), (4, 16), (8, 26), (12, 36)$.

1. **Initial Snow Depth ($b$):**
   Read at $t = 0$: point $(0, 6)$.
   **Answer:** $b = 6\text{ inches}$

2. **Rate of Snowfall ($m$):**
   Using $(0, 6)$ and $(4, 16)$ (or any pair):
   $$m = \frac{16 - 6}{4 - 0} = \frac{10}{4} = 2.5\text{ inches per hour} \quad \left(\text{or } \frac{5}{2}\text{ in/hr}\right)$$
   **Answer:** $2.5\text{ inches per hour}$

3. **Linear Function Equation:**
   $$S = 2.5t + 6 \quad \left(\text{or } S = \frac{5}{2}t + 6\right)$$

4. **Snow Depth after 15 Hours:**
   $$S(15) = 2.5(15) + 6 = 37.5 + 6 = 43.5\text{ inches}$$
   **Answer:** $43.5\text{ inches}$ (or $43\frac{1}{2}\text{ inches}$)

---

#### Task ID: EXT-8 — Extension Task (Optional Challenge)

1. **Converting Rate of Change ($-0.1\text{ gal/mi}$) to Fuel Economy in Miles per Gallon (mpg):**
   * The rate $-0.1\text{ gallons per mile}$ means $\frac{0.1\text{ gal}}{1\text{ mi}}$.
   * Fuel economy is the reciprocal of fuel consumption per mile:
     $$\text{Fuel Economy} = \frac{1}{|m|} = \frac{1\text{ mile}}{0.1\text{ gallons}} = 10\text{ miles per gallon (mpg)}$$
   * **Answer:** $10\text{ mpg}$

2. **Impact of Adding a 15-Gallon Auxiliary Tank (Starting Fuel $= 39\text{ gal}$):**
   * **Vertical Intercept:** Changes. It shifts from $(0, 24)$ up to $(0, 39)$ (an increase of $15$ gallons).
   * **Slope:** Does not change. The fuel consumption rate remains $-0.1\text{ gal/mi}$ (assuming engine efficiency is unchanged).
   * **Graph Transformation:** The line undergoes a rigid vertical translation upwards by $15$ units. The new horizontal intercept becomes $\frac{39}{0.1} = 390\text{ miles}$.

---

#### Task ID: PRAC-8 — Independent Practice Problems (Lesson 8)

##### Problem 1 (Custom School T-Shirts)
* **Given Data:** Vertical axis $C$ (grid lines spaced by $\$50$), horizontal axis $n$ (grid lines spaced by $10$ shirts).  
  Vertical intercept at $(0, 75)$; second point at $(20, 235)$.
  * **Setup fee ($b$):**
    $$b = \$75$$
  * **Cost per printed shirt ($m$):**
    $$m = \frac{235 - 75}{20 - 0} = \frac{160}{20} = \$8\text{ per shirt}$$
  * **Function equation:**
    $$C = 8n + 75 \quad (\text{or } C = 75 + 8n)$$
  * **Total cost to print 80 shirts:**
    $$C(80) = 8(80) + 75 = 640 + 75 = \$715$$

##### Problem 2 (Canyon Trail Elevation Descent)
* **Given Points:** $(15, 720)$ and $(45, 360)$ for elevation $E$ (feet) at time $t$ (minutes).
  * **Rate of descent:**
    $$m = \frac{360 - 720}{45 - 15} = \frac{-360}{30} = -12\text{ feet per minute}$$
    **Answer:** $-12\text{ ft/min}$ (descent speed is $12\text{ ft/min}$)
  * **Trailhead elevation ($t = 0$):**
    $$E(0) = 720 - (-12)(15) = 720 + 180 = 900\text{ feet}$$
    **Answer:** $900\text{ feet}$
  * **Equation:**
    $$E = -12t + 900 \quad (\text{or } E = 900 - 12t)$$
  * **Time to reach canyon river ($E = 0$):**
    $$900 - 12t = 0 \implies 12t = 900 \implies t = \frac{900}{12} = 75\text{ minutes}$$
    **Answer:** $75\text{ minutes}$ (or $1\text{ hour } 15\text{ minutes}$)

---

## 2. Findings, Graphic Audits, and Mathematical Inconsistencies

During the independent reading and calculation verification, several subtle issues, graphic behaviors, and phrasing inconsistencies were discovered:

### Finding 1: Missing Graphic in TASK-8.1 Launch
* **Location:** Lesson 8, Task ID `TASK-8.1`.
* **Prompt Text:** `"Look at the small sketch below:"` followed immediately by bulleted text without any image, SVG reference, ASCII sketch, or diagram.
* **Impact on Student:** While the bulleted text provides complete numerical information ($2$ boxes up, $1$ box right, scales of $5\text{ h}$ and $50\text{ mi}$), referring to a "small sketch below" when no sketch exists creates brief confusion.

### Finding 2: Inconsistent Grid Terminology in PRAC-8 Problem 1
* **Location:** Lesson 8, Task ID `PRAC-8`, Problem 1.
* **Prompt Text:**  
  `"The vertical axis (C) has grid lines spaced by $50. The horizontal axis (n) has grid lines spaced by 10 shirts."`  
  `"A second clean grid intersection occurs at (20, 235)."`
* **Mathematical Inconsistency:** If vertical grid lines are spaced by multiples of $\$50$ ($0, 50, 100, 150, 200, 250\dots$), the point $(20, 235)$ **does not lie on a horizontal grid line** ($235$ is not a multiple of $50$). Similarly, the intercept $(0, 75)$ is halfway between grid lines. Calling $(20, 235)$ a "clean grid intersection" contradicts the stated grid spacing. The algebra works out cleanly ($m = 8$), but students attempting to visualize this on the described grid will note that $235$ is off-grid.

### Finding 3: Premature Rate Disclosure ("Spoilers") in Figure 7.1 Legend
* **Location:** `lesson7_reservoir_models.svg` referenced in `TASK-7.1` and `TASK-7.2`.
* **Graphic Text in Legend:**  
  `Tank A (Filling: +15 gal/min)`  
  `Tank B (Draining: -20 gal/min)`
* **Impact on Task:** In `TASK-7.2`, students are asked to calculate $m_A = \frac{\Delta V}{\Delta t}$ and $m_B = \frac{\Delta V}{\Delta t}$ from coordinate points. However, the legend box in the upper right of Figure 7.1 explicitly states `+15 gal/min` and `-20 gal/min`, revealing the target answers before the students perform the slope ratio calculations.

### Finding 4: Graphic Verification of SVG Coordinates (Passed with High Precision)
* **Figure 7.1 (`lesson7_reservoir_models.svg`):**
  - Origin at $(80, 480)$ pixels.
  - Horizontal mapping: $32\text{ px/min}$ ($t = 0 \to 80$, $t = 4 \to 208$, $t = 8 \to 336$, $t = 12 \to 464$, $t = 14 \to 528$, $t = 16 \to 592$).
  - Vertical mapping: $1\text{ px/gal}$ ($V = 0 \to 480$, $V = 40 \to 440$, $V = 100 \to 380$, $V = 160 \to 320$, $V = 220 \to 260$, $V = 240 \to 240$, $V = 250 \to 230$, $V = 320 \to 160$).
  - Shutoff behavior: Correctly transitions to a horizontal dashed line at $V = 250$ from $t = 14$ to $t = 18$.
* **Figure 8.1 (`lesson8_scaled_graphs.svg`):**
  - Panel 1 (Graph 8A): Horizontal scale is $30\text{ px/min}$ ($1\text{ box} = 1\text{ min}$); vertical scale is $1\text{ px/m}$ ($1\text{ box} = 25\text{ m}$). Slope triangle correctly measures $\Delta t = 4\text{ boxes} = 4\text{ min}$ and $\Delta A = 4\text{ boxes} = 100\text{ m}$.
  - Panel 2 (Graph 8B): Horizontal scale is $1.5\text{ px/mi}$ ($1\text{ box} = 20\text{ mi}$); vertical scale is $10\text{ px/gal}$ ($1\text{ box} = 2.5\text{ gal}$). Vertical intercept at $F = 24$ is plotted at $y = 160$ ($400 - 240 = 160$), which exactly matches $24\text{ gal}$. Slope triangle spans $4\text{ boxes}$ horizontally ($80\text{ mi}$) and $3.2\text{ boxes}$ vertically ($-8\text{ gal}$ / $80\text{ px}$).

### Finding 5: Fractional and Rational Outputs in Student Contexts
* In `CFU-7`, the drainage time is $t = 18.75\text{ minutes}$ ($18\text{ min } 45\text{ s}$).
* In `EXT-7`, the draining rate is an exact repeating fraction: $\frac{160}{7} = 22.\overline{857142}\text{ gal/min} = 22\frac{6}{7}\text{ gal/min}$. Students without guidance on rounding or fractional forms might struggle with writing a clean decimal.
* In `PRAC-6` Problem 2, the empty time is $t = 24.5\text{ hours}$.
* All are mathematically exact and physically valid.

---

## 3. Full Coverage Inventory

Every task and sub-item across the three lessons in `lesson6_7_8_student_materials.md` has been independently reviewed, solved, and verified.

| Lesson | Task Identifier | Problem / Sub-item Description | Status | Verification Result |
| :--- | :--- | :--- | :--- | :--- |
| **Lesson 6** | `TASK-6.1` Q1 | Table 1 $\Delta x, \Delta y$, rate, initial value $b$, equation | Solved | Fully consistent ($\Delta x=1, \Delta y=4, m=4, b=5, y=4x+5$) |
| **Lesson 6** | `TASK-6.1` Q2 | Table 2 step differences & evaluation of Jordan's claim | Solved | Disagree; $\Delta y/\Delta x = 4$ is constant |
| **Lesson 6** | `TASK-6.2` Q1 | Table 2 three-interval slope calculations & constant $m$ | Solved | All intervals equal $4$; $m=4$ |
| **Lesson 6** | `TASK-6.2` Q2 | Table 2 extrapolation to $x=0$, $b$ value, equation | Solved | $b=3$, $y=4x+3$ |
| **Lesson 6** | `TASK-6.2` Q3 | Verification using point $(14, 59)$ | Solved | $4(14)+3=59$ confirms |
| **Lesson 6** | `TASK-6.3` Q1-2 | Rates for intervals $(4,156)\to(9,126)$ and $(15,90)\to(22,48)$ | Solved | Both equal $-6\text{ gal/min}$ |
| **Lesson 6** | `TASK-6.3` Q3-6 | Sign interpretation, initial volume $b$, equation, empty time | Solved | Decreasing; $b=180\text{ gal}$; $W=-6t+180$; $t=30\text{ min}$ |
| **Lesson 6** | `CFU-6` Q1-4 | Technician hourly rate, fixed fee, equation, cost for $8\text{ h}$ | Solved | $m=\$9/\text{h}, b=\$21, C=9h+21, C(8)=\$93$ |
| **Lesson 6** | `EXT-6` Q1-2 | Smudged table: rate, intercept, missing values | Solved | $m=5, b=4, y(7)=39, x(89)=17$ |
| **Lesson 6** | `PRAC-6` Prob 1 | Given $(5,65)$ and $(15,145)$: $m, b$, equation, $y(25)$ | Solved | $m=8, b=25, y=8x+25, y(25)=225$ |
| **Lesson 6** | `PRAC-6` Prob 2 | Battery discharge $(6,74\%)$ and $(14,42\%)$: $m, b$, equation, dead time | Solved | $m=-4\%/\text{h}, b=98\%, P=-4t+98, t=24.5\text{ h}$ |
| **Lesson 7** | `TASK-7.1` | Launch narrative linking to Figure 7.1 | Verified | Matches SVG graphics |
| **Lesson 7** | `TASK-7.2` Q1-3 | Tank A initial volume, filling rate, equation | Solved | $b_A=40\text{ gal}, m_A=15\text{ gal/min}, V_A=15t+40$ |
| **Lesson 7** | `TASK-7.2` Q4-6 | Tank B initial volume, draining rate, equation | Solved | $b_B=320\text{ gal}, m_B=-20\text{ gal/min}, V_B=-20t+320$ |
| **Lesson 7** | `TASK-7.3` Q1 | Tank A capacity trigger at $250\text{ gal}$ & graph behavior | Solved | $t=14\text{ min}$; graph becomes horizontal at $V=250$ |
| **Lesson 7** | `TASK-7.3` Q2 | Tank B emptying time & practical domain | Solved | $t=16\text{ min}$; domain $[0, 16]\text{ min}$ |
| **Lesson 7** | `TASK-7.3` Q3 | Intersection point $(8, 160)$ interpretation & verification | Solved | Equal volume of $160\text{ gal}$ at $t=8\text{ min}$; verified |
| **Lesson 7** | `CFU-7` Q1-4 | Draining rate, initial volume, equation, empty time | Solved | $m=-24\text{ gal/min}, b=450\text{ gal}, V=-24t+450, t=18.75\text{ min}$ |
| **Lesson 7** | `EXT-7` | Tank B synchronized emptying rate at $t=14\text{ min}$ | Solved | Rate $= \frac{160}{7}\approx 22.86\text{ gal/min}$ |
| **Lesson 7** | `PRAC-7` Prob 1 | Balloon descent $(3,580)\to(8,380)$: $m, b$, equation, ground time | Solved | $m=-40\text{ m/min}, b=700\text{ m}, A=-40t+700, t=17.5\text{ min}$ |
| **Lesson 7** | `PRAC-7` Prob 2 | Soup cooling $190^\circ\text{F}$ at $2.5^\circ\text{F/min}$: equation, $T(24)$, time to $115^\circ\text{F}$ | Solved | $T=-2.5m+190, T(24)=130^\circ\text{F}, m=30\text{ min}$ |
| **Lesson 8** | `TASK-8.1` | Launch: "Counting Squares" trap explanation | Solved | Missing sketch identified; math logic verified ($20\text{ mph}$ vs $2$) |
| **Lesson 8** | `TASK-8.2` 8A | Drone ascent: scales, $b$, slope triangle, equation, $A(11)$ | Solved | $x\text{-grid}=1\text{ min}, y\text{-grid}=25\text{ m}, b=50\text{ m}, m=25\text{ m/min}, A(11)=325\text{ m}$ |
| **Lesson 8** | `TASK-8.2` 8B | Fuel remaining: scales, $b$, slope triangle, equation, $(240,0)$ | Solved | $x\text{-grid}=20\text{ mi}, y\text{-grid}=2.5\text{ gal}, b=24\text{ gal}, m=-0.1\text{ gal/mi}, F=0\text{ at } 240\text{ mi}$ |
| **Lesson 8** | `CFU-8` Q1-4 | Snow depth ASCII: $b$, snowfall rate, equation, depth at $15\text{ h}$ | Solved | $b=6\text{ in}, m=2.5\text{ in/h}, S=2.5t+6, S(15)=43.5\text{ in}$ |
| **Lesson 8** | `EXT-8` Q1-2 | Fuel economy conversion to mpg & auxiliary tank shift | Solved | $10\text{ mpg}$; slope unchanged, intercept shifts to $39\text{ gal}$ |
| **Lesson 8** | `PRAC-8` Prob 1 | T-shirt cost graph: setup fee, unit cost, equation, cost for $80$ | Solved | Grid wording inconsistency noted; $b=\$75, m=\$8/\text{shirt}, C(80)=\$715$ |
| **Lesson 8** | `PRAC-8` Prob 2 | Canyon hiker descent $(15,720)\to(45,360)$: $m, b$, equation, river time | Solved | $m=-12\text{ ft/min}, b=900\text{ ft}, E=-12t+900, t=75\text{ min}$ |

---

## 4. Scope and Limitations of this Autonomous Read

* **Source Materials Only:** This report reflects an independent mathematical solution based entirely on the text of `lesson6_7_8_student_materials.md` and the SVG vector assets `lesson7_reservoir_models.svg` and `lesson8_scaled_graphs.svg`.
* **Model Autonomous Evaluation:** This work represents automated mathematical reading and programmatic verification using symbolic/numeric tools; it does not constitute a human expert review panel evaluation or empirical classroom observations of student performance.
