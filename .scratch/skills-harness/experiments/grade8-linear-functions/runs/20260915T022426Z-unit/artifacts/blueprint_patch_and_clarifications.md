# Upstream Curriculum Blueprint Patch and Clarifications (Candidate Patch v1.1)

**Target Document:** `grade8_curriculum_blueprint.md` (Version 1.0)  
**Context:** Resolving organizer review issues prior to Unit 5 lower-level instructional development.  
**Review Source:** Organizer Review of `20260915T021738Z-overall` (Common Study Research Conditions).

---

## 1. Summary of Required Modifications

The organizer review identified five specific areas where the candidate blueprint (`grade8_curriculum_blueprint.md`) required precise alignment with the research conditions and epistemological boundaries of this study:
1. **Resource & Equipment Bounds:** Remove references to specialized equipment (scientific calculators, tracing paper, compasses, protractors, transparencies, physical water tanks) and strictly maintain the specified research conditions: black-and-white printing, standard paper/pencil, straightedge/rulers, grid paper, ordinary four-function calculators, and a single teacher projector.
2. **Unit 5 Pacing and Flexible Time:** Affirm that Unit 5 is fully scheduled, taught, and assessed within its **18 regular 50-minute periods**. The 20 annual flex periods remain an unallocated strategic reserve; "access to Buffer Block 2" is an optional responsive safety valve, not required instructional time to complete the core unit.
3. **Epistemological Status of Probes & Sequencing:** Clarify that mathematical feasibility probes verify arithmetic correctness, coordinate consistency, and structural connections; they do not mathematically prove a unique curriculum sequence, an "absolute necessity" for an isolated lesson, or empirical classroom efficacy.
4. **Assessment Mastery Claims:** Reframe summative assessment outcomes as targeted sampling of student performance across specific standards rather than definitive proof of "complete, permanent mastery."
5. **Architectural Separation of Materials:** Separate student-facing worksheets from teacher guides and solutions, using stable task identifiers and standalone SVG diagram files.

---

## 2. Exact Replacement Text and Locations

### Patch Item 1: Classroom Context and Resource Constraints
- **Location:** `grade8_curriculum_blueprint.md`, header block and Section 2.2 (under "MP5").
- **Original Text:**  
  *Header block:* `Classroom Context Assumptions: 28 students per class; collaborative individual/peer/group routines; black-and-white printing, standard paper/pencil, rulers, grid paper, basic scientific calculators, teacher projection. No requirement of 1:1 connected student devices.`  
  *Section 2.2 (MP5):* `Students use physical tracing paper and compasses in Unit 1, transparent rulers and grid paper in Units 2, 5, and 9, and basic four-function/scientific calculators in Units 7 and 8...`
- **Replacement Text:**  
  *Header block:* `Classroom Context Assumptions: 28 students per class; collaborative individual, peer, and small-group routines. Materials are strictly limited to black-and-white printing on standard paper, pencils, straightedge/rulers, standard coordinate grid paper, ordinary four-function calculators, and a front teacher projector. No scientific calculators, compasses, protractors, tracing paper, transparencies, physical laboratory tanks, or 1:1 student connected devices are assumed or required.`  
  *Section 2.2 (MP5):* `Students strategically employ ordinary four-function calculators for multi-step arithmetic, straightedge/rulers for drawing and verifying linear graphs, and printed coordinate grid paper for slope triangles and rate-of-change analysis across Units 2, 5, 6, and 9.`

---

### Patch Item 2: Pacing and Flexible Time Independence
- **Location:** `grade8_curriculum_blueprint.md`, Section 4.1.
- **Original Text:**  
  `- Allocated Time: 18 Regular Instructional Periods (50 minutes each) + Access to Responsive Buffer Block 2 (5 periods).`
- **Replacement Text:**  
  `- Allocated Time: Exactly 18 Regular Instructional Periods (50 minutes each). All essential learning, guided explorations, formative modeling labs, and unit summative assessments are fully contained within these 18 regular periods. The 20 annual flex periods remain a distinct school-wide buffer; Responsive Buffer Block 2 (5 periods) is an optional post-unit intervention reservoir for calendar disruptions or targeted remediation, not required curriculum time for Unit 5 completion.`

---

### Patch Item 3: Design Rationale vs. Empirical Claims for Probes
- **Location:** `grade8_curriculum_blueprint.md`, Section 5.2 (Juncture 2).
- **Original Text:**  
  `Curriculum Impact: Proved the absolute necessity of dedicating Lesson 2 of Unit 5 exclusively to dismantling the y/x division habit acquired in Grade 7.`
- **Replacement Text:**  
  `Curriculum Impact: Identified the transition from coordinate division (y/x) to interval difference quotients (Δy/Δx) as a pivotal conceptual obstacle when b ≠ 0. The placement of an explicit lesson on rate of change versus coordinate ratio (Lesson 2) represents a deliberate, revisable curriculum design judgment to provide structured opportunity for learners to confront this difference, rather than an empirical proof of a unique instructional order.`

---

### Patch Item 4: Summative Assessment Evidence Scope
- **Location:** `grade8_curriculum_blueprint.md`, Section 4.4, Table Row P17, Column 4.
- **Original Text:**  
  `Summative Mastery: Evidence of complete mastery on 8.F.B.4 and 8.F.B.5.`
- **Replacement Text:**  
  `Summative Assessment Evidence: Provides structured evaluative evidence of student ability to construct linear models, interpret rate of change and initial value, and describe qualitative features across the sampled task contexts. Single-assessment performance indicates current procedural and representational proficiency under test conditions, but does not constitute proof of complete, permanent, or context-independent mastery.`

---

## 3. Structural Boundary Affirmation for Task B

Under these patched conditions:
1. All student materials in Task B are authored to print cleanly in black-and-white.
2. Modeling tasks utilize realistic tabular and graphical data sets rather than hands-on fluid hardware.
3. Lessons 2, 3, and 4 are delivered as an interconnected instructional candidate block, while Lessons 1 and 5–18 are preserved at the curriculum skeleton tier.
