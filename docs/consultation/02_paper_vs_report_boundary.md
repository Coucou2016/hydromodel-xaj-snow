# Paper vs research-report boundary (mandatory)

The project maintains **two** deliverables. ChatGPT must respect this split when suggesting edits.

## A. Manuscript (journal-facing; target HESS)

**Allowed**

- Academic framing, research questions, contribution relative to Tan/Ju/Dong/Wu/Chen2025
- Methods at scientific protocol level (periods, optimizer family, matched budgets, negative-control design)
- Results that are **completed and verified** (pilot; optional refine as supplementary; batch1 as *extended pilot / first look*)
- Cautious language: engineering GO, selective skill recovery, pending large-sample inference
- Code/data availability pointing to the public GitHub snapshot

**Forbidden in the manuscript**

- Absolute machine paths (`D:\…`, user home directories, conda env absolute paths)
- Internal operational trivia: PowerShell one-liners, `$env:HOME=…`, smoke-runner anecdotes, “InvalidIndexError fix log”, personal file names
- Claiming unfinished experiments as complete (`rep=5000`, full 80-basin medium, SWE validation, global map)
- “First XAJ snow / first XAJ–CemaNeige / first large-sample XAJ–snow”
- Over-strong causal language (“proves melt physics”, “independent SWE validation” when using ERA5-Land-linked Caravan fields)

**Relative repository paths** may appear sparingly in Availability/SI, but Methods/Results prose should prefer scientific wording (“paired basins_metrics tables in the public snapshot”) over command recipes.

## B. Research report (engineering archive; Chinese OK)

**Allowed / expected**

- Full process narrative, failed attempts, debug history
- Local relative paths, script names (`RUN_*.ps1`), config YAML names
- Incomplete long-run command stubs and resume notes
- Verbose figure “how to read” pedagogy
- Explicit tables of TODO experiments

The report may be longer and more operational; it is **not** the HESS submission text.

## C. Strength ladder for Results claims

| Evidence | Allowed paper wording | Disallowed paper wording |
|----------|----------------------|--------------------------|
| 2-basin go/no-go `rep`=800 | engineering pilot; selective gain; GO for sampling | population inference; “across CAMELS” |
| SciPy refine on 010 | supplementary local improvement after SCE-UA | primary fairness proof; “final skill” |
| Batch1 n=14 `rep`=200 | first-look / extended pilot; stratified medians | multi-region applicability boundary; global |
| Frozen N=80 | sampling design ready | “we calibrated 80 basins” |
| `rep`=2000 on 010 only | partial budget sensitivity | complete fairness analysis |

## D. Tone targets

Imitate diagnosis-first HESS papers (e.g. Santos et al. 2025 robustness diagnosis; Wu et al. 2025 complexity ladder; Premier et al. 2026 parameter isolation; Husic et al. 2025 process deficiencies) rather than software-release notes.
