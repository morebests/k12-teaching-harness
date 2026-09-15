# Remaining formatting repair v0.1

Object: actual candidate 20260915T023107Z-repair. This is organizer feedback from real rendering, not classroom evidence.

The student sheet now has 22 KaTeX errors (down from 58). They all still contain unescaped underscore placeholders inside math text. Teacher math has zero parser errors. Fix the remaining instances in the actual student file, preserving mathematical tasks, numerical data, graphs and teaching choices. Use the provided check_rendering tool on the actual file, inspect its returned errors, and correct the remaining instances until it succeeds or you report a concrete limit. Do not hand off on the strength of a claim about compatibility.

Keep the prior repair findings and version history in repair-report.md; append this pass rather than silently erasing its history. Correct any design report that claims all parser failures have already been removed. Do not treat zero parser errors as print acceptance or mathematical validation.

The previous repair report specifically asserts “Full workspace search confirmed zero unescaped underscores” despite these actual failures and no search/render tool execution in that run. Correct that assertion and other sweeping “zero pre-filled formulas”/“all checked” statements to the real evidence. Deliberate worked examples can be useful, but are not evidence of unaided construction. Do not repeat a verification claim without its actual result.

One smaller unresolved item from review 1: CFU-6's diagnostic table still labels a single incorrect answer a “persistent misconception” or a “relapsing habit.” Make these possible interpretations with a confirming follow-up, rather than stable student diagnoses. Preserve numerical keys and existing useful prompts.

Actual failing expressions (duplicates retained because they occur in different places):

- `\text{Rate } = \text{________ gallons per minute}`
- `\text{Rate } = \text{________ gallons per minute}`
- `\text{Initial Volume } b = \text{________ gallons}`
- `m = \text{________ dollars per hour}`
- `b = \$\text{________}`
- `C = \text{________________________}`
- `\text{Total Charge} = \$\text{________}`
- `m_A = \frac{\Delta V}{\Delta t} = \text{________ gallons per minute}`
- `V_A = \text{________________________}`
- `m_B = \frac{\Delta V}{\Delta t} = \text{________ gallons per minute}`
- `V_B = \text{________________________}`
- `\text{Rate of change } m = \text{________________________}`
- `b = \text{________ gallons}`
- `V = \text{________________________}`
- `m = \frac{\Delta A}{\Delta t} = \text{________ meters per minute}`
- `A = \text{________________________}`
- `A(11) = \text{________ meters}`
- `m = \frac{\Delta F}{\Delta d} = \text{________ gallons per mile}`
- `F = \text{________________________}`
- `S = \text{________________________}`
- `\text{Depth after 15 hours} = \text{________ inches}`
- `\$\text{________}`
