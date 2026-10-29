# Verification & claims register

| Item | Status | Evidence |
|---|---|---|
| Original source recovered | Confirmed | Source files dated 2026-10-05 |
| Original Korean/English reports | Recovered locally | Separate downloadable portfolio archive |
| GitHub model training | **Not verified** | No known trained weights or training logs |
| CNN test accuracy | **Not verified** | Do not fabricate a percentage |
| Macro-F1 / confusion matrix | **Not verified** | Await actual held-out test run |
| MixedWM38 data QA | Confirmed in local audit | 38,015 → 8,015 → 7,910 |
| Die-state gate / unit tests | Previously passed (3 tests) | Test source provided in tests/ |
| Browser UI concept / schematic | Explained | This is not a deployed wafer-testing system |
| InFact project announcement | Screenshot supplied by author | This is not proof of attendance or awards |
| Industry process-causality evaluation | Not attempted | No tool/lot/recipe history |

## Required steps before claiming CNN performance
1. Archive environment and package versions.
2. Save stratified split indices and training seed.
3. Run actual model fitting, keeping test data held out.
4. Export confusion matrix, macro-F1 and classwise recall.
5. Check minority-class behavior and any source duplication leakage.
6. Upload the real output artifacts and distinguish predictions from source labels.
