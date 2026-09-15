# Upstream Blueprint Corrections and Refinements (Candidate v1.1 Patch)

**Document Reference:** Amends and patches `grade8_curriculum_blueprint.md` (Candidate Version 1.0, provenance hash `d76ae98003...`).  
**Purpose:** Formally resolves concrete issues identified in the Organizer Review prior to the detailed design of Unit 5, without altering unaffected curriculum units.

---

### Item 1: Classroom Equipment and Resource Alignment

- **Location in Blueprint:** Part 1 (front matter, line 8), Part 2.2 (MP5 description), and Unit Descriptions (e.g., Unit 1, Unit 7).
- **Issue Identified:** The blueprint introduced items outside the research conditions (specifically: scientific calculators, tracing paper, compasses, protractors, and transparencies). The common research conditions specify only: ordinary calculators, paper/pencil, rulers, grid paper, and a teacher projector. No 1:1 connected student devices or specialized laboratory apparatus are available.
- **Exact Replacement Text:**
  > **Classroom Context Assumptions (Amended):**  
  > 28 students per class; collaborative individual, peer, and small-group structures. Permitted and available classroom resources are strictly limited to: black-and-white printing, standard paper and pencils, straightedge rulers, grid paper, basic four-function/ordinary calculators, and a single teacher display projector. No student internet devices, specialized geometric hardware (compasses, protractors), or physical fluid apparatus are assumed. All geometric transformations rely on coordinate rules and grid-paper constructions with straightedges; all contextual modeling tasks (such as water reservoir dynamics) use supplied mathematical data tables, descriptions, and coordinate diagrams rather than physical lab equipment.

---

### Item 2: Unit 5 Time Allocation and Annual Buffer Policy

- **Location in Blueprint:** Part 4.1 ("Allocated Time") and Part 3.2 ("Scheduling of Flex Periods").
- **Issue Identified:** The blueprint stated that Unit 5 has 18 regular periods plus "access to Responsive Buffer Block 2 (5 periods)," implying an expanded 23-period instructional requirement. The 20 annual flexible periods must remain a reserved buffer across the entire 180-day school year and cannot be commandeered as mandatory instructional time for Unit 5.
- **Exact Replacement Text:**
  > **Unit 5 Pacing and Schedule Authority (Amended):**  
  > Unit 5 is strictly bounded to **18 regular instructional periods (50 minutes each)**, comprising regular direct instruction, collaborative investigation, review, and assessment. The 20 annual flex periods remain an independent strategic reserve for district calendar interruptions, school-wide testing, or post-unit diagnostic reteaching. The 18-period schedule for Unit 5 is fully autonomous and complete; no required core lesson or assessment in Unit 5 depends upon access to Buffer Block 2. Any buffer sessions remain strictly optional, responsive intervention routines that take place outside the 18-period unit envelope.

---

### Item 3: Epistemic Status of Mathematical Probes and Curricular Order

- **Location in Blueprint:** Part 1.3 ("Progression Narrative"), Part 4.3 ("Detailed Unit Narrative"), and Part 5.2 ("Summary of Feasibility Probes").
- **Issue Identified:** The blueprint used overly dogmatic language (e.g., "absolute necessity of dedicating Lesson 2 exclusively," "geometrically proves that Unit 2 must precede Unit 4"). Mathematical probes verify specific numerical calculations and logical relationships; they do not establish empirical classroom effectiveness or prove that a single curriculum order is uniquely mandatory. Local design constraints are designer proposals, not human-confirmed mandates.
- **Exact Replacement Text:**
  > **Epistemic Status and Design Judgments (Amended):**  
  > The mathematical feasibility probes verify the internal numerical accuracy, algebraic consistency, and geometric relationships between representations (such as similar triangles preserving slope ratios, and difference quotients isolating rates of change when $b \neq 0$). These mathematical verifications provide sound pedagogical reasons for our curricular sequence (such as introducing geometric slope triangles before algebraic rate formulas, and explicitly addressing $\frac{y}{x}$ versus $\frac{\Delta y}{\Delta x}$). However, they constitute reasoned, revisable curricular design judgments rather than dogmatic proofs of a uniquely possible lesson order or guaranteed classroom efficacy. Pacing allocations and sequencing remain subject to empirical evaluation and teacher adaptation.

---

### Item 4: Summative Assessment Claims and Learning Evidence

- **Location in Blueprint:** Part 3.3 ("Spiral Review and Assessment") and Part 4.4 (Period 17).
- **Issue Identified:** Period 17 claimed that the end-of-unit summative assessment provides "Evidence of complete mastery on 8.F.B.4 and 8.F.B.5." A single 50-minute exam samples specific performance targets and cannot establish permanent, stable mastery.
- **Exact Replacement Text:**
  > **Assessment Role and Scope of Evidence (Amended):**  
  > The Period 17 summative assessment provides cross-sectional formative and evaluative evidence regarding student proficiency on the specific sampled tasks corresponding to 8.F.B.4 and 8.F.B.5 (e.g., calculating rate of change from an irregular table, identifying initial value from a scaled coordinate graph, and sketching qualitative shapes from verbal narratives). Performance on this exam serves as an indicator of current procedural and conceptual fluency; it does not constitute proof of complete, permanent, or unshakeable mastery. Continued retention and contextual transfer are monitored through ongoing spiral warm-ups in subsequent units (Units 6 and 9).

---

### Item 5: Structural Separation of Teacher and Student Materials

- **Location in Blueprint:** Accompanying file `probe_tasks_student_and_teacher.md`.
- **Issue Identified:** While divided into Section I and Section II, the probe notes shared an artifact, and future unit deliverables must ensure that student-facing task sheets and teacher answer keys/lesson guides reside in entirely separate documents to allow clean, unassisted student work and independent verification.
- **Resolution in Unit 5 Delivery:**  
  All instructional materials for the Unit 5 three-lesson sequence are partitioned into dedicated files:
  - `lesson6_7_8_student_materials.md`: Contains purely student-facing materials, task sheets, coordinate grids, and exit tickets, free of teacher keys or annotations.
  - `lesson6_7_8_teacher_guides.md`: Contains teacher lesson plans, diagnostic rubrics, questioning scripts, and complete worked solutions with common Task IDs.
