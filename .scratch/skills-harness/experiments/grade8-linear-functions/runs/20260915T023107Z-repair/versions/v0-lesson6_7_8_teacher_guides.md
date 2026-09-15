# Grade 8 Mathematics — Teacher Lesson Plans and Evaluation Guides
## Unit 5: Linear Functions and Contextual Modeling
### Continuous Three-Lesson Sequence: Lessons 6, 7, and 8

---

# Lesson 6: Constructing Linear Functions from Irregular Tables

### 1. Lesson Overview and Standards Alignment
- **Primary CCSS Standard:** **8.F.B.4** (Construct a function to model a linear relationship; determine rate of change and initial value from a table).
- **Standards for Mathematical Practice:**
  - **MP1:** Make sense of problems and persevere in solving them (analyzing non-consecutive table jumps).
  - **MP6:** Attend to precision (calculating difference quotients $\frac{\Delta y}{\Delta x}$ accurately with signs and units).
  - **MP7:** Look for and make use of structure (recognizing that linearity requires constant ratio of differences, not constant successive differences in $y$).
- **Daily Learning Targets:**
  - *Target 6A:* I can compute the rate of change $\frac{\Delta y}{\Delta x}$ from a table where input values are not consecutive ($\Delta x > 1$).
  - *Target 6B:* I can extrapolate backward or solve algebraically to determine the initial value $b$ when $x = 0$ is missing from a table.
  - *Target 6C:* I can construct the equation $y = mx + b$ and verify that it holds for all table entries.

### 2. Entry Assumptions and Universal Supports
- **Entry Assumptions:** Students can calculate differences between integers, plot points, and know that $m$ represents rate of change and $b$ represents initial value from regular tables ($\Delta x = 1$) in Lesson 5.
- **Universal Supports & Accommodations:**
  - *Calculation Scaffold:* Basic four-function calculators are available for all students to prevent multi-digit subtraction/division fatigue from masking conceptual progress.
  - *Visual Scaffold:* A two-column difference bracket template printed on grid scratch paper allows students to visually pair $\Delta y$ with its corresponding $\Delta x$.
  - *Language Support:* Sentence frames for explaining rate: *"As the input increases by [$\Delta x$], the output changes by [$\Delta y$], which simplifies to [$\frac{\Delta y}{\Delta x}$] per 1 unit."*

### 3. Materials and Advance Preparation
- **Classroom Materials:** Handout `lesson6_7_8_student_materials.md` (Lesson 6, 1 copy per student), straightedge rulers, pencils, basic ordinary calculators (class set of 28), teacher display projector.
- **Advance Preparation:** Estimated 15 minutes. Verify projector display of Table 1 and Table 2. Pre-cut scratch grid paper for students needing scratch calculations.

### 4. Detailed 50-Minute Instructional Timeline
- **Launch / Notice & Wonder (`TASK-6.1`): 10 minutes**
  - Teacher projects Table 1 and Table 2 side-by-side. 3 minutes quiet individual work, 3 minutes partner share, 4 minutes whole-class framing.
  - *Key Facilitation Move:* Ask: *"Why did Jordan think Table 2 was not linear? Where is Jordan's eye looking, and what is Jordan ignoring?"* Elicit that Jordan only looked at $\Delta y$ without looking at $\Delta x$.
- **Core Guided Investigation (`TASK-6.2`): 15 minutes**
  - Students work in pairs to calculate $\frac{\Delta y}{\Delta x}$ across all three intervals of Table 2.
  - Circulate to ensure students divide $\Delta y$ by $\Delta x$ and do not invert the ratio ($\frac{\Delta x}{\Delta y}$).
  - Gather class to demonstrate finding $b$: either by walking backward from $x = 2$ ($11 - 2(4) = 3$) or by substitution into $y = mx + b$ ($11 = 4(2) + b \implies b = 3$).
- **Collaborative Partner Practice (`TASK-6.3`): 15 minutes**
  - Pairs tackle the decreasing cooling tank problem.
  - Focus teacher circulation on the negative sign: $\Delta W = 126 - 156 = -30$, $\Delta t = 9 - 4 = 5 \implies m = \frac{-30}{5} = -6\text{ gal/min}$.
- **Whole-Class Synthesis & Discussion: 5 minutes**
  - Highlight the two-step invariant method: (1) Find constant rate $m = \frac{\Delta y}{\Delta x}$; (2) Find initial value $b = y_1 - m(x_1)$.
- **Independent Check for Understanding (`CFU-6`): 5 minutes**
  - Individual, silent exit ticket collected at the door.

---

### 5. Facilitation Guide, Anticipated Responses, and Interventions

#### Anticipated Student Responses (Design Predictions)
1. **Misconception A (The "Delta Y Only" Trap):**
   - *Anticipated Student Claim:* In `TASK-6.1`, Jordan is right because $23 - 11 = 12$, but $59 - 35 = 24$. The jumps are not the same!
   - *Teacher Move:* Ask the student: *"How many steps in $x$ did it take to jump 12 in $y$? How many steps in $x$ did it take to jump 24 in $y$? What is the rate per 1 step in $x$?"*
2. **Misconception B (Inverting the Difference Quotient):**
   - *Anticipated Student Claim:* Student computes $\frac{5 - 2}{23 - 11} = \frac{3}{12} = 0.25$.
   - *Teacher Move:* Connect back to Grade 7 unit rate: *"Does slope measure change in $x$ per $y$, or change in $y$ per $x$?"* Reference the standard form $y = mx + b$, showing $m$ multiplies $x$ to yield $y$.
3. **Misconception C (First Row is Initial Value):**
   - *Anticipated Student Claim:* In Table 2, $b = 11$ because $(2, 11)$ is the first row.
   - *Teacher Move:* Point to Table 1: *"Why was $b = 5$ in Table 1? Because $x = 0$! In Table 2, what is $x$ in the first row? It is 2. How much did $y$ grow during those first 2 steps?"*

---

### 6. Complete Mathematical Solutions and Evaluation Keys

#### Solutions for `TASK-6.1`
1. Table 1:
   - $\Delta x = 1$.
   - $\Delta y = 4$.
   - Rate of change $= \frac{4}{1} = 4$.
   - Initial value $b = 5$ (at $x = 0$).
   - Equation: $y = 4x + 5$.
2. Table 2:
   - First step: $\Delta x = 5 - 2 = 3$; $\Delta y = 23 - 11 = 12$.
   - Third step: $\Delta x = 14 - 8 = 6$; $\Delta y = 59 - 35 = 24$.
   - Disagree with Jordan: Jordan only looked at $\Delta y$. The ratio $\frac{\Delta y}{\Delta x} = \frac{12}{3} = 4$ and $\frac{24}{6} = 4$. The rate of change is constant, so Table 2 is linear.

#### Solutions for `TASK-6.2`
1. Rate of Change calculations:
   - Interval 1: $\frac{23 - 11}{5 - 2} = \frac{12}{3} = 4$.
   - Interval 2: $\frac{35 - 23}{8 - 5} = \frac{12}{3} = 4$.
   - Interval 3: $\frac{59 - 35}{14 - 8} = \frac{24}{6} = 4$.
   - Rate of change is constant: $m = 4$.
2. Initial Value ($b$):
   - Method 1 (Extrapolation): At $x = 2$, $y = 11$. Since $x$ increased by 2 from 0, $y$ increased by $2 \times 4 = 8$. Working backward: $b = 11 - 8 = 3$.
   - Method 2 (Algebraic): $y = 4x + b \implies 11 = 4(2) + b \implies 11 = 8 + b \implies b = 3$.
   - Equation: $y = 4x + 3$.
3. Verification:
   - Substitute $x = 14$: $y = 4(14) + 3 = 56 + 3 = 59$. Matches the table.

#### Solutions for `TASK-6.3`
1. Interval 1: $\frac{126 - 156}{9 - 4} = \frac{-30}{5} = -6\text{ gallons per minute}$.
2. Interval 2: $\frac{48 - 90}{22 - 15} = \frac{-42}{7} = -6\text{ gallons per minute}$.
3. Contextual meaning: Rate is negative because water is leaving the tank (draining/cooling). The tank loses 6 gallons every minute.
4. Initial volume ($b$):
   - At $t = 4$, $W = 156$. Pumping drained $4 \times 6 = 24$ gallons.
   - Initial volume: $b = 156 + 24 = 180\text{ gallons}$ (or $156 = -6(4) + b \implies 156 = -24 + b \implies b = 180$).
5. Equation: $W = -6t + 180$ (or $W = 180 - 6t$).
6. Emptying time: $0 = -6t + 180 \implies 6t = 180 \implies t = 30\text{ minutes}$.

#### Solutions for `CFU-6` (Exit Ticket)
1. Rate of change: $\frac{102 - 57}{9 - 4} = \frac{45}{5} = 9$ (or $\frac{156 - 102}{15 - 9} = \frac{54}{6} = 9$). Rate is $\$9$ per hour.
2. Initial fee $b$: $C = 9h + b \implies 57 = 9(4) + b \implies 57 = 36 + b \implies b = 21$. Fixed fee is $\$21$.
3. Equation: $C = 9h + 21$.
4. For $h = 8$: $C = 9(8) + 21 = 72 + 21 = \$93$.

#### Solutions for `EXT-6`
1. Known points $(3, 19)$ and $(12, 64)$: $m = \frac{64 - 19}{12 - 3} = \frac{45}{9} = 5$.
   Initial value: $19 = 5(3) + b \implies 19 = 15 + b \implies b = 4$. Equation: $y = 5x + 4$.
2. Smudged value at $x = 7$: $y = 5(7) + 4 = 35 + 4 = 39$.
   Smudged value at $y = 89$: $89 = 5x + 4 \implies 5x = 85 \implies x = 17$.

#### Solutions for `PRAC-6`
1. Points $(5, 65)$ and $(15, 145)$:
   - $m = \frac{145 - 65}{15 - 5} = \frac{80}{10} = 8$.
   - $b = 65 - 8(5) = 65 - 40 = 25$.
   - Equation: $y = 8x + 25$.
   - When $x = 25$: $y = 8(25) + 25 = 200 + 25 = 225$.
2. Battery discharge:
   - $m = \frac{42 - 74}{14 - 6} = \frac{-32}{8} = -4\%\text{ per hour}$.
   - $P = -4t + b \implies 74 = -4(6) + b \implies 74 = -24 + b \implies b = 98\%$.
   - Equation: $P = -4t + 98$ (or $P = 98 - 4t$).
   - Dead battery: $0 = -4t + 98 \implies 4t = 98 \implies t = 24.5\text{ hours}$ (24 hours 30 minutes).

### 7. Diagnostic Evidence Rubric for Lesson 6
| Assessment Evidence (`CFU-6`) | Identified Mathematical State | Next Pedagogical Action |
| :--- | :--- | :--- |\n| Correctly computes $m = 9$, $b = 21$, $C = 9h + 21$, and $\$93$. | Full operational mastery of irregular tables and initial value extrapolation. | Advance to Lesson 7 contextual modeling; assign `EXT-6` or student-led debrief. |\n| Calculates $m = 9$ correctly, but writes $C = 9h + 57$ (assumes first entry is $b$). | Procedural understanding of rate, but persistent misconception that first row is always $y$-intercept. | Provide targeted 2-minute feedback card: *"What is $h$ in the first row? If $h \neq 0$, where does the graph cross the axis?"* |\n| Computes $m = 45$ (subtracts $102 - 57$ but ignores $\Delta h = 9 - 4 = 5$). | Relapsing into the "Delta Y Only" trap from regular tables. | Highlight table headers with color pencils: green for $\Delta C$, orange for $\Delta h$, draw fraction bar connecting them. |\n| Inverts rate: $m = \frac{5}{45} = 0.11$. | Ratio orientation confusion (mixing up dependent and independent variables). | Anchor with physical meaning: *"Does the technician charge 11 cents per hour, or does it take hours per dollar?"* |

---
\pagebreak
---

# Lesson 7: Contextual Modeling: Filling and Draining Systems

### 1. Lesson Overview and Standards Alignment
- **Primary CCSS Standard:** **8.F.B.4** (Construct a function to model a linear relationship between two quantities; interpret the rate of change and initial value in terms of the situation it models).
- **Standards for Mathematical Practice:**
  - **MP2:** Reason abstractly and quantitatively (contextualizing algebraic slopes as fluid flow rates and intercepts as initial capacities).
  - **MP4:** Model with mathematics (mapping real reservoir behavior onto linear functions and identifying domain boundaries).
- **Daily Learning Targets:**
  - *Target 7A:* I can construct linear functions representing both increasing and decreasing physical processes from a graph and contextual description.
  - *Target 7B:* I can interpret rate of change and initial value using concrete physical units (gallons, minutes, gallons per minute).
  - *Target 7C:* I can identify realistic domain constraints (e.g., maximum capacity shut-off, empty tank at $V = 0$).

### 2. Entry Assumptions and Universal Supports
- **Entry Assumptions:** Students can compute rate of change $\frac{\Delta y}{\Delta x}$ from points (mastered in Lesson 6) and locate $y$-intercepts on a coordinate axis.
- **Universal Supports & Accommodations:**
  - *Grayscale Graphic Clarity:* In Figure 7.1 (`lesson7_reservoir_models.svg`), Tank A is drawn with a solid thick stroke and Tank B is drawn with a distinct dashed stroke, ensuring accessibility on standard black-and-white copies without color dependency.
  - *Physical Realia / Concrete Metaphor:* If students struggle with negative slope, refer to an everyday beverage cup: filling adds liquid (positive rate, rising line); sipping through a straw removes liquid (negative rate, falling line).
  - *Calculators:* Four-function calculators support solving multi-step equations for shut-off times and empty times.

### 3. Materials and Advance Preparation
- **Classroom Materials:** Handout `lesson6_7_8_student_materials.md` (Lesson 7), straightedge rulers, pencils, ordinary calculators (class set of 28), teacher projector displaying `lesson7_reservoir_models.svg`.
- **Advance Preparation:** Estimated 10 minutes. Project Figure 7.1 on the board. Ensure projection focus shows grid tick labels clearly.

### 4. Detailed 50-Minute Instructional Timeline
- **Launch / Contextual Framing (`TASK-7.1`): 8 minutes**
  - Project Figure 7.1. Direct attention to the two lines: one rising, one falling.
  - Ask: *"Before doing any calculations, which line is Tank A and which is Tank B? How do you know?"* Elicit that Tank A is filling (positive slope, going uphill from left to right) and Tank B is draining (negative slope, going downhill).
- **Core Modeling Lab (`TASK-7.2`): 22 minutes**
  - Students work in pairs on Part 1 (Tank A) and Part 2 (Tank B).
  - *Teacher Circulation Focus:* Listen for students verbalizing rates. Ensure students write: *"Tank A increases by 15 gallons per minute"* and *"Tank B decreases by 20 gallons per minute"* (or has a rate of change of $-20\text{ gal/min}$).
- **Constraints & Intersection Analysis (`TASK-7.3`): 10 minutes**
  - Whole-class guided discussion on physical boundaries:
    - Tank A reaches 250 gallons at $t = 14$. Point out the horizontal dotted line on Figure 7.1—why is it flat? Because the pump shut off!
    - Tank B reaches 0 gallons at $t = 16$. Can the line keep going below the horizontal axis? No, negative water volume is physically impossible.
    - Examine $(8, 160)$: At 8 minutes, both tanks contain exactly 160 gallons.
- **Synthesis & Cool-Down (`CFU-7`): 10 minutes**
  - 4 minutes summarizing key insights: rate is flow speed; intercept is starting water; lines cannot extend past physical limits.
  - 6 minutes independent exit ticket `CFU-7`.

---

### 5. Facilitation Guide, Anticipated Responses, and Interventions

#### Anticipated Student Responses (Design Predictions)
1. **Misconception A (Dropping the Negative Sign in Draining Rate):**
   - *Anticipated Student Claim:* In Part 2, student writes $m_B = 20\text{ gal/min}$ and equation $V_B = 20t + 320$.
   - *Teacher Move:* Ask the student: *"Use your equation to calculate the volume at $t = 4$. $20(4) + 320 = 400$ gallons. Did Tank B gain water or lose water? Look at the graph!"* Guide them to recognize $\Delta V = 80 - 240 = -160$, so $m = \frac{-160}{8} = -20$.
2. **Misconception B (Ignoring Domain Limits):**
   - *Anticipated Student Claim:* In `TASK-7.3`, student says Tank B's volume at $t = 20$ minutes is $320 - 20(20) = -80$ gallons.
   - *Teacher Move:* Ask: *"Can you pour $-80$ gallons of water on a garden? What happens when a tank runs out of water?"* Emphasize MP4: Mathematical models describe reality only within their valid domain ($0 \le t \le 16$).

---

### 6. Complete Mathematical Solutions and Evaluation Keys

#### Solutions for `TASK-7.2`
1. Tank A Initial Volume: $b_A = 40\text{ gallons}$. Physical meaning: Tank A already contained 40 gallons of water at time $t = 0$ before pumping started.
2. Tank A Filling Rate:
   - $\Delta t = 12 - 4 = 8\text{ minutes}$.
   - $\Delta V = 220 - 100 = 120\text{ gallons}$.
   - $m_A = \frac{120}{8} = 15\text{ gallons per minute}$.
   - Contextual sentence: *"Water is pumped into Tank A at a constant rate of 15 gallons for every additional minute."*
3. Tank A Function: $V_A = 15t + 40$.
4. Tank B Initial Volume: $b_B = 320\text{ gallons}$. Physical meaning: Tank B started full with 320 gallons of water at $t = 0$.
5. Tank B Draining Rate:
   - $\Delta t = 12 - 4 = 8\text{ minutes}$.
   - $\Delta V = 80 - 240 = -160\text{ gallons}$.
   - $m_B = \frac{-160}{8} = -20\text{ gallons per minute}$.
   - Meaning of negative sign: Volume is decreasing; water is flowing out of Tank B at 20 gallons per minute.
6. Tank B Function: $V_B = -20t + 320$ (or $V_B = 320 - 20t$).

#### Solutions for `TASK-7.3`
1. Tank A Shut-Off:
   - $15t + 40 = 250 \implies 15t = 210 \implies t = 14\text{ minutes}$.
   - Graph description: After $t = 14$, the line becomes flat/horizontal at $V = 250$, indicating volume remains constant (rate of change becomes 0).
2. Tank B Emptying:
   - $320 - 20t = 0 \implies 20t = 320 \implies t = 16\text{ minutes}$.
   - Valid practical domain: $0 \le t \le 16$ minutes.
3. Shared Point $(8, 160)$:
   - $t = 8$ represents the exact moment (8 minutes) when both tanks hold the exact same amount of water.
   - $V = 160$ represents that equal volume (160 gallons).
   - Verifications: $V_A = 15(8) + 40 = 120 + 40 = 160$. $V_B = 320 - 20(8) = 320 - 160 = 160$. Both evaluate to 160.

#### Solutions for `CFU-7` (Exit Ticket)
1. Rate of change: $m = \frac{162 - 330}{12 - 5} = \frac{-168}{7} = -24\text{ gallons per minute}$.
2. Initial volume: $b = 450\text{ gallons}$ (given in narrative; check: $330 - (-24)(5) = 330 + 120 = 450$).
3. Equation: $V = -24t + 450$ (or $V = 450 - 24t$).
4. Empty time: $450 - 24t = 0 \implies 24t = 450 \implies t = \frac{450}{24} = 18.75\text{ minutes}$ (or $18\frac{3}{4}$ min, 18 min 45 sec).

#### Solutions for `EXT-7`
- Tank B starts at 320 gallons and must empty in 14 minutes:
  $320 - r(14) = 0 \implies 14r = 320 \implies r = \frac{320}{14} = \frac{160}{7} \approx 22.86\text{ gallons per minute}$.

#### Solutions for `PRAC-7`
1. Balloon Descent:
   - $m = \frac{380 - 580}{8 - 3} = \frac{-200}{5} = -40\text{ meters per minute}$.
   - $A = -40t + b \implies 580 = -40(3) + b \implies 580 = -120 + b \implies b = 700\text{ meters}$.
   - Equation: $A = -40t + 700$.
   - Touchdown ($A = 0$): $0 = -40t + 700 \implies 40t = 700 \implies t = 17.5\text{ minutes}$.
2. Soup Cooling:
   - Equation: $T = -2.5m + 190$ (or $T = 190 - 2.5m$).
   - At $m = 24$: $T = -2.5(24) + 190 = -60 + 190 = 130^\circ\text{F}$.
   - Serving at $115^\circ\text{F}$: $115 = -2.5m + 190 \implies -75 = -2.5m \implies m = 30\text{ minutes}$.

### 7. Diagnostic Evidence Rubric for Lesson 7
| Assessment Evidence (`CFU-7`) | Identified Mathematical State | Next Pedagogical Action |
| :--- | :--- | :--- |\n| Correctly determines $m = -24\text{ gal/min}$, $b = 450$, $V = -24t + 450$, and $t = 18.75\text{ min}$. | Strong conceptual integration of negative rates, contextual functions, and domain bounds. | Prepared for Lesson 8 graphical coordinate scaling; assign extension or peer coaching role. |\n| Calculates rate as $+24$ (positive) and writes $V = 24t + 450$. | Procedural fluency with slope formula, but neglecting direction of change in real contexts. | Prompt during warm-up 8: *"If volume is 450 and rate is $+24$, does water level go up or down? Check physical reality!"* |\n| Writes correct equation, but solves $450 - 24t = 0$ incorrectly (e.g. subtracting $450$ and getting negative time). | Minor algebraic equation-solving slip with negative signs. | Review solving two-step equations involving negative coefficients ($ax + b = c$). |

---
\pagebreak
---

# Lesson 8: Constructing Linear Functions from Scaled Coordinate Graphs

### 1. Lesson Overview and Standards Alignment
- **Primary CCSS Standard:** **8.F.B.4** (Construct a linear function; determine rate of change and initial value from a graph).
- **Standards for Mathematical Practice:**
  - **MP5:** Use appropriate tools strategically (using straightedges and coordinate grid lines to draw precise slope triangles).
  - **MP6:** Attend to precision (reading axis labels, accounting for scale increments where 1 grid box $\neq 1$ unit).
- **Daily Learning Targets:**
  - *Target 8A:* I can determine the scale of each axis on a coordinate grid and avoid the "counting grid squares" error.
  - *Target 8B:* I can construct a slope triangle using clean grid intersections and calculate the true rate of change $\frac{\Delta y}{\Delta x}$.
  - *Target 8C:* I can identify the vertical intercept $(0, b)$ and construct the linear equation $y = mx + b$ directly from a scaled graph.

### 2. Entry Assumptions and Universal Supports
- **Entry Assumptions:** Students know how to calculate $\frac{\Delta y}{\Delta x}$ from coordinate pairs and understand positive vs. negative slope from Lesson 7.
- **Universal Supports & Accommodations:**
  - *High-Contrast Grid Handout:* Figure 8.1 (`lesson8_scaled_graphs.svg`) provides bolded major grid lines and shaded slope triangles with labeled $\Delta x$ and $\Delta y$ dimensions.
  - *Physical Rulers:* Every student receives a straightedge ruler to align coordinate lattice points and trace horizontal/vertical legs without visual distortion.
  - *Step-by-Step Anchor Chart:* Post in room: 
    1. *Check Axes:* What do the ticks count by on $x$? On $y$?
    2. *Find $b$:* What is $y$ when $x = 0$?
    3. *Pick 2 Clean Points:* Write their $(x, y)$ coordinates.
    4. *Compute Rate:* Divide $\frac{\text{change in } y}{\text{change in } x}$.

### 3. Materials and Advance Preparation
- **Classroom Materials:** Handout `lesson6_7_8_student_materials.md` (Lesson 8), straightedge rulers, pencils, ordinary calculators, teacher projector displaying `lesson8_scaled_graphs.svg`.
- **Advance Preparation:** Estimated 10 minutes. Project Figure 8.1. Check that the projection clearly distinguishes the tick marks on both Graph 8A and Graph 8B.

### 4. Detailed 50-Minute Instructional Timeline
- **Launch / Confronting the Trap (`TASK-8.1`): 8 minutes**
  - Direct class attention to the "Counting Squares" trap prompt.
  - Ask: *"A student counts 2 boxes up and 1 box right, and says slope is 2. But the vertical boxes count by 50 miles, and horizontal boxes count by 5 hours. What is the real slope?"* Elicit: $\frac{100\text{ miles}}{5\text{ hours}} = 20\text{ mph}$, NOT $2$.
  - State the rule: *Never count boxes; always calculate coordinate changes!*
- **Core Guided Investigation (`TASK-8.2` — Part 1: Graph 8A): 15 minutes**
  - Walk through Graph 8A (Drone Ascent).
  - Explicitly identify scales: horizontal ticks count by 1 minute; vertical ticks count by 25 meters.
  - Identify initial altitude: $(0, 50) \implies b = 50\text{ meters}$.
  - Examine the shaded slope triangle between $(2, 100)$ and $(6, 200)$:
    $\Delta t = 4\text{ min}$, $\Delta A = 100\text{ m} \implies m = \frac{100}{4} = 25\text{ m/min}$.
  - Write equation: $A = 25t + 50$.
- **Partner Practice (`TASK-8.2` — Part 2: Graph 8B): 15 minutes**
  - Pairs analyze Graph 8B (Delivery Truck Fuel).
  - *Teacher Circulation Focus:* Watch the vertical axis scale! Major ticks count by 5 gallons, grid lines count by 2.5 gallons. The point at $d = 120$ is at $F = 12$.
  - Slope triangle: $\Delta d = 120 - 40 = 80\text{ miles}$; $\Delta F = 12 - 20 = -8\text{ gallons}$.
  - Rate: $m = \frac{-8}{80} = -0.1\text{ gallons per mile}$.
- **Whole-Class Synthesis: 6 minutes**
  - Connect the graph's horizontal intercept $(240, 0)$ to physical reality: the truck runs out of gas after 240 miles.
  - Reiterate how scaled graphs require MP6 precision.
- **Independent Check for Understanding (`CFU-8`): 6 minutes**
  - Individual, silent exit ticket collected at the door.

---

### 5. Facilitation Guide, Anticipated Responses, and Interventions

#### Anticipated Student Responses (Design Predictions)
1. **Misconception A (Counting Boxes on Graph 8A):**
   - *Anticipated Student Claim:* In Graph 8A, the triangle is 4 boxes high and 4 boxes wide, so slope is $\frac{4}{4} = 1$.
   - *Teacher Move:* Ask the student to point to the vertical axis: *"What altitude is the bottom of that triangle at? 100 meters. What altitude is the top at? 200 meters. How many meters did the drone climb? 100 meters, not 4 meters! The grid boxes are just drawing paper; the numbers on the axes are the real world."*
2. **Misconception B (Misreading Decimal Rate on Graph 8B):**
   - *Anticipated Student Claim:* Student calculates $\frac{-8}{80}$ and writes $-10$ instead of $-0.1$.
   - *Teacher Move:* Ask: *"What is $8$ divided by $80$? Is it greater than 1 or less than 1? Use your calculator to verify: $8 \div 80 = 0.1$."* Discuss what 10 vs. 0.1 would mean: losing 10 gallons every mile would drain the tank in 2 miles!

---

### 6. Complete Mathematical Solutions and Evaluation Keys

#### Solutions for `TASK-8.1`
- Counting grid boxes ignores the scale values assigned to each box. If vertical boxes count by 50 and horizontal boxes count by 5, then 2 boxes up is $2 \times 50 = 100$ units, and 1 box right is $1 \times 5 = 5$ units. The true rate of change is $\frac{100}{5} = 20$, which is 10 times larger than the box count of 2.

#### Solutions for `TASK-8.2` — Part 1 (Graph 8A)
1. Axes & Scales:
   - Horizontal axis: Time $t$ in minutes. Each grid line $= 1$ minute.
   - Vertical axis: Altitude $A$ in meters. Each grid line $= 25$ meters.
2. Initial Value:
   - Vertical intercept: $(0, 50)$. Initial altitude $b = 50\text{ meters}$.
   - Meaning: The drone was launched from an elevated location (e.g., a 50-meter hill or rooftop), not from ground level 0.
3. Rate of Change:
   - $\Delta t = 6 - 2 = 4\text{ minutes}$.
   - $\Delta A = 200 - 100 = 100\text{ meters}$.
   - $m = \frac{100\text{ m}}{4\text{ min}} = 25\text{ meters per minute}$.
   - Error check: 4 boxes up represents $4 \times 25 = 100$ meters; 4 boxes right represents $4 \times 1 = 4$ minutes. Counting boxes gives $\frac{4}{4} = 1$, which completely ignores that each vertical box represents 25 meters.
4. Function Equation:
   - $A = 25t + 50$.
   - At $t = 11$: $A = 25(11) + 50 = 275 + 50 = 325\text{ meters}$.

#### Solutions for `TASK-8.2` — Part 2 (Graph 8B)
1. Axes & Scales:
   - Horizontal axis: Distance traveled $d$ in miles. Each grid line $= 20$ miles.
   - Vertical axis: Fuel remaining $F$ in gallons. Each grid line $= 2.5$ gallons.
2. Initial Value:
   - Vertical intercept: $(0, 24)$. Initial fuel $b = 24\text{ gallons}$.
3. Rate of Change:
   - $\Delta d = 120 - 40 = 80\text{ miles}$.
   - $\Delta F = 12 - 20 = -8\text{ gallons}$.
   - $m = \frac{-8\text{ gal}}{80\text{ mi}} = -\frac{1}{10} = -0.1\text{ gallons per mile}$.
   - Contextual meaning: The delivery truck consumes $0.1$ gallons of fuel for every mile driven (or burns 1 gallon every 10 miles).
4. Equation and Intercept:
   - $F = -0.1d + 24$ (or $F = 24 - 0.1d$).
   - Point $(240, 0)$: After driving 240 miles, the fuel tank is completely empty ($F = 0$). The truck's maximum range on a full tank is 240 miles.

#### Solutions for `CFU-8` (Exit Ticket)
1. Initial depth $b = 6\text{ inches}$ (at $t = 0$).
2. Rate of snowfall:
   - Using $(0, 6)$ and $(4, 16)$: $m = \frac{16 - 6}{4 - 0} = \frac{10}{4} = 2.5\text{ inches per hour}$.
   - (Alternatively, using $(4, 16)$ and $(8, 26)$: $m = \frac{26 - 16}{8 - 4} = \frac{10}{4} = 2.5\text{ in/hr}$).
3. Equation: $S = 2.5t + 6$.
4. Depth after 15 hours: $S = 2.5(15) + 6 = 37.5 + 6 = 43.5\text{ inches}$.

#### Solutions for `EXT-8`
1. Fuel economy in mpg: Since the truck burns $0.1$ gallons per mile, $1\text{ gallon} \div 0.1\text{ gal/mi} = 10\text{ miles per gallon}$. (The reciprocal of the rate).
2. Auxiliary tank effect: The line shifts upward parallel to the original line. The slope remains $-0.1$ gal/mi (fuel efficiency of the engine is unchanged), but the vertical intercept increases from $24$ to $39$ gallons.

#### Solutions for `PRAC-8`
1. T-Shirt Printing:
   - $b = \$75$ (setup fee).
   - $m = \frac{235 - 75}{20 - 0} = \frac{160}{20} = \$8\text{ per shirt}$.
   - Equation: $C = 8n + 75$.
   - For $n = 80$: $C = 8(80) + 75 = 640 + 75 = \$715$.
2. Canyon Hiker:
   - $m = \frac{360 - 720}{45 - 15} = \frac{-360}{30} = -12\text{ feet per minute}$.
   - $E = -12t + b \implies 720 = -12(15) + b \implies 720 = -180 + b \implies b = 900\text{ feet}$.
   - Equation: $E = -12t + 900$.
   - Touching river ($E = 0$): $0 = -12t + 900 \implies 12t = 900 \implies t = 75\text{ minutes}$.

### 7. Diagnostic Evidence Rubric for Lesson 8
| Assessment Evidence (`CFU-8`) | Identified Mathematical State | Next Pedagogical Action |
| :--- | :--- | :--- |\n| Correctly determines $b = 6\text{ in}$, $m = 2.5\text{ in/hr}$, $S = 2.5t + 6$, and $43.5\text{ in}$. | Complete mastery of reading and constructing linear functions from scaled graphs. | Ready for Lesson 9 (algebraic two-point formulation without a graph). |\n| Calculates $m$ by counting grid squares (e.g. 1 unit up, 2 units right $\implies 0.5$). | Still trapped by visual box counting; failing to consult axis numbers. | Re-engage with straightedge: physically underline axis numbers when calculating $\Delta S$ and $\Delta t$. |\n| Computes $m = 2.5$ correctly, but omits $b = 6$ (writes $S = 2.5t$). | Treats situation as proportional ($y = kx$); ignores vertical intercept. | Direct attention to $(0, 6)$: *"At hour 0, was the ground bare or was there already snow?"* |
