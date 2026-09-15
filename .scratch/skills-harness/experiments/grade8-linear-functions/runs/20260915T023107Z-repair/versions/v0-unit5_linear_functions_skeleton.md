# Grade 8 Unit 5: Linear Functions and Contextual Modeling
## Full 18-Period Unit Skeleton and Target-Evidence Architecture (Candidate v1.1)

**Target Grade:** Grade 8 (US Public School Curriculum)  
**Unit Duration:** Exactly 18 Regular Periods (50 Minutes each)  
**Primary CCSS Content Standards:** 
- **8.F.B.4:** Construct a function to model a linear relationship between two quantities. Determine the rate of change and initial value of the function from a description of a relationship or from two $(x, y)$ values, including reading these from a table or from a graph. Interpret the rate of change and initial value of a linear function in terms of the situation it models, and in terms of its graph or a table of values.
- **8.F.B.5:** Describe qualitatively the functional relationship between two quantities by analyzing a graph (e.g., where the function is increasing or decreasing, linear or nonlinear). Sketch a graph that exhibits the qualitative features of a function that has been described verbally.
**Integrated Standards for Mathematical Practice:** MP1 (Problem solving & perseverance), MP2 (Quantitative & abstract reasoning), MP4 (Mathematical modeling), MP6 (Precision & units), MP7 (Making use of structure).  
**Classroom Operating Conditions:** 28 students; individual, partner, and small-group routines; black-and-white paper printouts, pencils, rulers, standard grid paper, basic four-function/ordinary calculators, and a single teacher projector. No 1:1 student devices or laboratory hardware required.

---

## 1. Unit Narrative and Representational Progression

### 1.1 The Developmental Trajectory of Unit 5
Unit 5 serves as the vital bridge in Grade 8 mathematics from structural function definitions (Unit 4: 8.F.A) to applied mathematical modeling (8.F.B) and simultaneous linear systems (Unit 6: 8.EE.C.8). In Unit 4, students established that a function assigns to each input exactly one output, and that linear functions are governed by the equation $y = mx + b$, producing straight-line graphs. 

In Unit 5, students transition from identifying functions to actively constructing, interpreting, and applying them. The progression is deliberately sequenced across five instructional clusters:

1. **Cluster 1: Foundations of Rate of Change and Initial Value (Periods 1–4):**  
   Students confront the cognitive shift from Grade 7 proportional relationships ($y = kx$) to affine linear models ($y = mx + b$). The primary hurdle is dismantling the habit of computing $\frac{y}{x}$ rather than the difference quotient $\frac{\Delta y}{\Delta x}$. Students explore what the initial value $b$ represents physically and graphically when $x = 0$.
2. **Cluster 2: Constructing Linear Models Across Multiple Representations (Periods 5–9):**  
   Students systematically learn to construct $y = mx + b$ across four major representational formats:
   - Tables with unit steps ($\Delta x = 1$)
   - Tables with non-consecutive inputs ($\Delta x > 1$) [Detailed expansion: Lesson 6]
   - Contextual word problems and physical systems (Filling & Draining tanks) [Detailed expansion: Lesson 7]
   - Coordinate graphs with scaled axes (overcoming the "counting grid squares" trap) [Detailed expansion: Lesson 8]
   - Coordinate point pairs $(x_1, y_1)$ and $(x_2, y_2)$ using algebraic solving for $b$.
3. **Cluster 3: Mid-Unit Synthesis & Contextual Precision (Periods 10–11):**  
   A mid-unit check-in measures student fluency in determining $m$ and $b$. Lesson 11 deepens quantitative reasoning (MP2, MP6), requiring students to write rigorous contextual interpretations specifying units for both parameters.
4. **Cluster 4: Qualitative Analysis and Sketching of Functions (Periods 12–15, 8.F.B.5):**  
   The mathematical lens shifts from algebraic computation to qualitative curve reading. Students analyze non-numeric graphs, identifying intervals of increase, decrease, and constancy, distinguishing constant rates (straight segments) from variable rates (curves), and sketching continuous graphs from narrative stories.
5. **Cluster 5: Integration, Evaluation, and Bridge (Periods 16–18):**  
   Students synthesize all representations, take an 18-period target-sampled summative exam, debrief misunderstandings, and analyze a preview problem where two linear functions intersect, establishing the entry condition for Unit 6 (Systems of Equations).

---

## 2. Pacing Skeleton: 18-Period Target-Evidence Alignment

| Period | Cluster | Lesson Title & CCSS Focus | Core Student Task / Activity | Diagnostic Learning Evidence & Teacher Action |
| :---: | :---: | :--- | :--- | :--- |
| **P1** | 1 | **Unit Diagnostic & Proportional vs. Non-Proportional Review**<br>*(8.EE.B.5, 8.F.A.3)* | Compare two water delivery pricing plans: Plan A ($C = 4g$) vs. Plan B ($C = 3g + 15$). Graph both on grid paper; analyze why Plan A passes through $(0, 0)$ while Plan B has an initial fee. | **Entry Diagnostic:** Detect whether students recognize that Plan B does not have a constant ratio $C/g$. *Action:* Highlight the vertical shift of 15 on the projector. |
| **P2** | 1 | **Rate of Change vs. Coordinate Ratio**<br>*(8.F.B.4, MP7)* | Given a table for a car rental ($x = 2$ days, $\$110$; $x = 5$ days, $\$215$). Test student claims: does $\frac{110}{2} = 55$ equal $\frac{215}{5} = 43$? Compute $\frac{215 - 110}{5 - 2} = \frac{105}{3} = \$35/\text{day}$. | **Evidence:** Students explain in writing why dividing a single $(x, y)$ coordinate fails when $b \neq 0$, and why $\frac{\Delta y}{\Delta x}$ remains invariant. |
| **P3** | 1 | **Identifying and Extrapolating the Initial Value ($b$)**<br>*(8.F.B.4)* | Analyze tables and graphs where $x = 0$ is missing. Use constant rate of change to extrapolate backward to $x = 0$. Contrast initial value with $x$-intercept. | **Evidence:** Students successfully calculate $b = y_1 - m(x_1)$ instead of assuming the first listed table value is $b$. |
| **P4** | 1 | **Constructing $y = mx + b$ from Verbal Narratives**<br>*(8.F.B.4, MP2)* | Read real-world situations (e.g., plumber basic service charge plus hourly rate; gym joining fee plus monthly dues). Identify which quantity is fixed ($b$) and which varies ($m$). | **Evidence:** Formative exit ticket: Students write equations without reversing $m$ and $b$ (e.g., avoiding $y = 50x + 25$ when fee is $\$50$ and rate is $\$25/\text{hr}$). |
| **P5** | 2 | **Linear Functions from Tables with Regular Unit Steps ($\Delta x = 1$)**<br>*(8.F.B.4)* | Analyze tables where inputs increase consecutively ($x = 0, 1, 2, 3$). Compute first differences $\Delta y$. Examine both positive and negative rates. | **Evidence:** Students identify rate of change directly from $\Delta y$ when $\Delta x = 1$ and locate $b$ at row $x = 0$. |
| **P6** | 2 | **Linear Functions from Irregular Tables ($\Delta x > 1$)**<br>*(8.F.B.4, MP1, MP6)*<br>***[Expanded Lesson 1/3]*** | Students analyze tables with non-consecutive inputs and missing $x=0$. Calculate $\frac{\Delta y}{\Delta x}$ across multiple intervals to confirm linearity, then solve for initial value $b$. | **Evidence (CFU-6):** Students correctly compute rate across irregular jumps and find $b$ without assuming the first entry is $x=0$. |
| **P7** | 2 | **Contextual Modeling: Filling and Draining Systems**<br>*(8.F.B.4, MP2, MP4)*<br>***[Expanded Lesson 2/3]*** | Multi-representational investigation using supplied data and coordinate diagram `lesson7_reservoir_models.svg`. Model Tank A (filling, positive rate) and Tank B (draining, negative rate). Determine equations and physical domain bounds. | **Evidence (CFU-7):** Students write accurate linear equations for both tanks, interpret positive/negative slopes with physical units, and identify realistic domain boundaries ($V \ge 0$). |
| **P8** | 2 | **Constructing Linear Functions from Scaled Coordinate Graphs**<br>*(8.F.B.4, MP5, MP6)*<br>***[Expanded Lesson 3/3]*** | Students analyze coordinate graphs where horizontal and vertical axis scales differ (`lesson8_scaled_graphs.svg`). Overcome the "counting grid squares" trap by constructing coordinate slope triangles. | **Evidence (CFU-8):** Students extract rate of change using actual coordinate values $\frac{\Delta y}{\Delta x}$ rather than counting visual grid boxes. |
| **P9** | 2 | **Constructing Linear Models from Any Two Points $(x_1, y_1)$ and $(x_2, y_2)$**<br>*(8.F.B.4)* | Abstract the process algebraically: compute $m = \frac{y_2 - y_1}{x_2 - x_1}$, substitute $(x_1, y_1)$ into $y = mx + b$, and solve for $b$. Verify with $(x_2, y_2)$. | **Evidence:** Students solve multi-step algebraic equations with rational numbers to isolate $b$ and verify consistency. |
| **P10** | 3 | **Mid-Unit Formative Assessment & Targeted Synthesis**<br>*(8.F.B.4)* | Individual 30-minute 4-item formative assessment: 1 table, 1 graph, 1 word problem, and 1 two-point item. 20-minute peer discussion of error patterns. | **Diagnostic Profile:** Pinpoints students needing targeted support on negative rates or isolating $b$ before moving to qualitative topics. |
| **P11** | 3 | **Contextual Parameter Interpretation: Attending to Units**<br>*(8.F.B.4, MP2, MP6)* | Discourse routine using structured sentence frames: *"For each 1 [input unit] increase, [output quantity] changes by [rate] [output units]."* Analyze realistic parameters. | **Evidence:** Written explanations correctly attach compound units (e.g., meters/min, gallons/mile) and explain physical meaning of intercept. |
| **P12** | 4 | **Qualitative Features: Increasing, Decreasing, and Constant**<br>*(8.F.B.5)* | Analyze graphs without numbers (e.g., skateboarder speed over time on a half-pipe and flat ground). Label intervals as increasing, decreasing, or constant. | **Evidence:** Connect positive slope to increasing, negative slope to decreasing, and zero slope (horizontal lines) to constancy. |
| **P13** | 4 | **Qualitative Features: Linear vs. Nonlinear Behaviors**<br>*(8.F.B.5, 8.F.A.3)* | Compare graphs representing steady speed (straight line) vs. acceleration/braking (curved segments). Discuss why a curved graph represents a changing rate. | **Evidence:** Students distinguish between constant rate of change and variable rate of change on qualitative graphs. |
| **P14** | 4 | **Sketching Continuous Graphs from Narrative Stories**<br>*(8.F.B.5, MP4)* | Read real-world stories (e.g., student walking to school, stopping for a friend, running because late). Sketch continuous qualitative distance-time graphs on blank axes. | **Evidence:** Sketches correctly represent relative steepness (sprinting is steeper than walking) and horizontal segments (stopping). |
| **P15** | 4 | **Collaborative Qualitative Matching Lab: Commute Stories**<br>*(8.F.B.5, MP3)* | Partner card-sort: Match 6 narrative cards, 6 graph cards, and 6 written justification cards. Students write critiques of non-matching pairs. | **Evidence:** Observational assessment of MP3 arguments justifying why specific graph features correspond to narrative events. |
| **P16** | 5 | **Multi-Representational Synthesis and Structured Review**<br>*(8.F.B.4, 8.F.B.5)* | Four-station rotation activity: Station 1 (Words $\to$ Equation), Station 2 (Table $\to$ Graph), Station 3 (Graph $\to$ Story), Station 4 (Two Points $\to$ Context). | **Evidence:** Self-assessment checklist where students identify their personal fluency across representations before the summative test. |
| **P17** | 5 | **End-of-Unit Summative Assessment**<br>*(8.F.B.4, 8.F.B.5)* | Independent 50-minute assessment sampling targets: Part 1 (Procedural fluency), Part 2 (Contextual modeling from table/graph), Part 3 (Qualitative sketching). | **Evaluative Evidence:** Measures individual student proficiency on sampled targets across both standards. Identifies persistent class needs. |
| **P18** | 5 | **Assessment Debrief & Bridge to Simultaneous Systems**<br>*(8.F.B.4, 8.EE.C.8)* | Debrief assessment problems. Conclude with a preview task: Tank A ($V = 15t + 40$) and Tank B ($V = 320 - 20t$). Ask: *"At what exact minute do both tanks hold equal water?"* | **Bridge to Unit 6:** Students realize the intersection of two linear functions is the shared solution of a system of equations. |

---

## 3. Pacing, Resource Feasibility, and Strategic Buffer Relationship

### 3.1 Pacing Realism within 50-Minute Periods
Every period in Unit 5 is structured according to a consistent four-phase instructional architecture designed for the 28-student classroom condition:
- **Phase 1: Retrieval Warm-Up (7–8 minutes):** Low-stakes spiral review of previous skills (e.g., calculating differences, plotting points, solving 1-step equations).
- **Phase 2: Launch & Collaborative Exploration (22–25 minutes):** Direct framing by teacher projection, followed by paired or small-group investigation using printed task sheets and rulers/calculators.
- **Phase 3: Structured Whole-Class Synthesis (10–12 minutes):** Teacher-orchestrated discussion comparing student methods and formalizing definitions.
- **Phase 4: Independent Check for Understanding / Cool-Down (5–6 minutes):** 1–2 focused questions completed individually to provide immediate diagnostic data for the teacher.

### 3.2 Distinction Between Core 18 Periods and Annual Buffer Reserve
- **The Core 18 Periods:** All 18 periods detailed above represent the complete, non-negotiable instructional plan for Unit 5. Every required learning target of 8.F.B.4 and 8.F.B.5 is addressed and assessed within this window.
- **The 20-Period Annual Flex Reserve:** The blueprint allocates 20 flexible periods across the year (in four 5-period blocks). If a district calendar experiences severe disruptions (e.g., inclement weather, school assemblies) or if the Period 10 mid-unit assessment reveals widespread foundational deficits in rational number arithmetic, the teacher may utilize a session from the annual buffer reserve. However, Unit 5 does not require or assume extra periods to complete its core curriculum.

---

## 4. Selection and Rationale for the Continuous Three-Lesson Sequence (Periods 6, 7, 8)

To evaluate the instructional viability of this curriculum design, **Periods 6, 7, and 8** are selected for full, deep lesson delivery. 

### Why Periods 6, 7, and 8?
These three consecutive lessons form the critical developmental core of standard 8.F.B.4:
1. **Lesson 6 (Numerical/Tabular Representation):** Moves students beyond simple $+1$ counting patterns by presenting irregular tables where $\Delta x > 1$ and $x = 0$ is absent. It forces students to construct the difference quotient $\frac{\Delta y}{\Delta x}$ and algebraically/numerically extrapolate to find the initial value $b$.
2. **Lesson 7 (Contextual/Applied Modeling):** Takes the mathematical mechanics of Lesson 6 and contextualizes them within a realistic physical system (the Water Storage Reservoir, featuring Tank A filling and Tank B draining). Students confront positive and negative rates of change, physical units, and realistic domain constraints ($V \ge 0$).
3. **Lesson 8 (Visual/Graphical Representation):** Translates the contextual and tabular models into the coordinate plane. It directly tackles the classic pedagogical pitfall where students count visual grid squares on graphs with unequal axis scales rather than computing true coordinate differences $\frac{\Delta y}{\Delta x}$.

Together, Lessons 6, 7, and 8 constitute an unbreakable representational triad—**Table $\to$ Real-World Context $\to$ Graph**—ensuring that students master rate of change and initial value conceptually, numerically, and visually before abstracting to general two-point formulas in Lesson 9.
