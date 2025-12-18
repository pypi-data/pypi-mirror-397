PLANNER_EXAMPLES = """
## Example — Region Plot With EAS LD

## Intent
Generate a regional plot for the second lead variant

## Required Data / References
- Sumstats object loaded
- 1KG EAS LD reference panel
- Genome build (ask if unknown)

## Step-by-step Plan
1. call_utility_runner : get_reference_file_path → get reference file path
   context:
   - desc=1KG EAS LD reference panel (source: Required Data / References)
   notes: returns ref_path for LD and plotting
2. call_utility_runner : get_lead → get lead variants dataframe <df_0>
   notes: returns lead variants dataframe
3. call_utility_runner : get_region_start_and_end → get plotting window
   context:
   - chr=df_0.CHR[1] (source: step 2)
   - pos=df_0.POS[1] (source: step 2)
   notes: returns region_start and region_end
4. call_plotter : plot_region → get regional plot using dependencies
   context:
   - ref_path=<resolved_value> (source: step 1)
   - highlight=df_0.SNPID (source: step 2)
   - region_start=<resolved_value> (source: step 3)
   - region_end=<resolved_value> (source: step 3)
   notes: figures render locally; return a short confirmation only

---

## Example — Manhattan Plot With SNP Highlights

## Intent
Render a Manhattan plot highlighting top lead variants on even-number chromosomes

## Required Data / References
- Sumstats object loaded
- Genome build (ask if unknown)

## Step-by-step Plan
1. call_utility_runner : get_lead → get lead variants dataframe <df_0>
   notes: returns lead variants dataframe for plot highlights
2. call_plotter : plot_manhattan → render Manhattan plot with highlights
   context:
   - highlight=df_0.query("CHR % 2 == 0").SNPID (source: step 2)
   notes: figures render locally; return a short confirmation only

---

## Example — Manhattan Plot With common SNP (0.05<EAF<0.95) 

## Intent
Render a Manhattan plot  with common SNP (0.05<EAF<0.95) 

## Required Data / References
- Sumstats object loaded

## Step-by-step Plan
1. call_filter : filter_value → get common SNP (0.05<EAF<0.95) sumstats object <subset_0>
   notes: returns a sumstats object of common SNP dataframe for plot
2. call_plotter : plot_manhattan → render Manhattan plot
   subset_id=subset_0 (source: step 1)
   notes: figures render locally; return a short confirmation only
"""

PLANNER_REQUIRED_MD = """
# Required Output Format (Always Markdown)

## **If operational request:**

## Intent
<one-sentence summary>

## Required Data / References
- <required dataset>
- <required reference>
- If unknown → ask the user

## Step-by-step Plan
Use orchestrator wrappers directly. Provide a clear, consistent structure that both humans and the Executor can follow.
1. call_<wrapper> : <tool_name> → get <expected state/output>
   context:
   - <key1>=<resolved_value> (source: <step|resource>)
   - <key2>=<resolved_value> (source: <step|resource>)
   notes: map each input to its source (e.g., subset_id from step N; ref_path from PathManager)
2. call_<wrapper> : <tool_name> → get <expected state/output> using <param> from step <N>
   context:
   - <keyX>=<resolved_value> (source: <step|resource>)
   - <keyY>=<resolved_value> (source: <step|resource>)
   notes: reference dependencies explicitly (e.g., lead_rs from step 2; window from step 3)

---

## **If conceptual/explanatory:**

## Intent
explanation

## Required Data / References
- none

## Step-by-step Plan
(no operational steps required)

---

## **If essential data is missing:**

## Intent
<summary>

## Required Data / References
- Missing: <item>

## Step-by-step Plan
Please provide the missing information. If a path or resource is missing, add a step to call [pathmanager] to retrieve or register it.
"""
