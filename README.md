# OSTRAM-RDM

OSTRAM-RDM adds **Robust Decision Making (RDM)** to
[OSTRAM](https://github.com/Climate-Lead-Group/OSTRAM), the OSeMOSYS-based
framework for power-system scenario studies with detailed transmission and
cross-border interconnectors. OSTRAM answers "what if" for a handful of
hand-built scenarios. OSTRAM-RDM asks how a plan performs across **many
futures**, and you describe those futures in one Excel workbook, without
touching code or the model's input files.

This branch (`RDM`) is OSTRAM plus the RDM extension. Everything OSTRAM does
still works the same way. For OSTRAM itself, see the
[original repository](https://github.com/Climate-Lead-Group/OSTRAM) and its
[documentation](https://ostram.readthedocs.io/).

## What OSTRAM-RDM adds

| | OSTRAM | OSTRAM-RDM adds |
|---|---|---|
| Scenarios | Hand-built scenarios in `config/scenarios/` | **Futures** defined in an Excel interface: a root scenario plus a list of changes |
| Uncertainty | One value per parameter | **Ranged uncertainties**, sampled by Latin Hypercube inside each named future (`F01_s001`, `F01_s002` …) |
| Running | One command per scenario set | `rdm run` builds, compiles, solves and collects every future in one go, and carries on past a future that fails |
| Results | Results per scenario | One **experiment design**, one **inputs** and one **outputs** CSV for the whole run, ready for scenario discovery |
| Checks | – | The workbook is checked before anything runs; bounds a future breaks are reported with the workbook row that caused them |
| Diagnosis | – | `diagnosis_for_rdm/`: perturbed inputs, inputs and outputs by set, infeasibility leads for unsolved futures, and two HTML dashboards |

## Setup

In an Anaconda Prompt on Windows, clone to a short path:

```bat
git clone https://github.com/jeenogeorge/OSTRAM.git OSTRAM
cd OSTRAM
git switch RDM
conda env create -f environment.yaml
conda activate OSTRAM-env
python -m pip install -e .
set PYTHONUTF8=1
```

In PowerShell the last line is `$env:PYTHONUTF8 = '1'`. Repeat
`conda activate` and `PYTHONUTF8` in every new prompt. GLPK and CBC come with
the environment.

Check that the RDM commands are there:

```bat
git branch
python -m ostram rdm --help
```

`git branch` marks `RDM` with `*`, and the help lists `template`, `generate`,
`run` and `collect`. If `rdm` is an unknown command, the environment is
running OSTRAM from another folder: run `pip install -e .` again from this
clone.

## Build the baseline first

Every future starts from a root scenario, so prepare and solve the roots once.
The examples use the two-region training model (`unescap_training`:
Bangladesh and India East), which solves in minutes.

```bat
python -m ostram example prepare unescap_training
python -m ostram --setup unescap_training run --scenarios "A_Calibrated_BAU,B_Optimised_VRE" --skip-pull
```

Without `--setup`, commands use the full South Asia model.

## Run the futures

```bat
:: 1. Write the interface workbook, with dropdowns filled from the root
python -m ostram --setup unescap_training rdm template --out Interface_OSTRAM_RDM.xlsx

:: 2. Fill the workbook in Excel and save it

:: 3. Check the workbook and preview the futures, without running anything
python -m ostram --setup unescap_training rdm generate --interface Interface_OSTRAM_RDM.xlsx

:: 4. Build, solve and collect every future
python -m ostram --setup unescap_training rdm run --interface Interface_OSTRAM_RDM.xlsx --overwrite
```

The workbook has these sheets:

| Sheet | What you fill in |
|---|---|
| `Setup` | `Run_Name`, `Base_Scenario`, `Samples_Per_Future`, `Random_Seed`, `Run_Central_Future`, model years |
| `Futures` | The named futures (`F00`, `F01` …) and whether each runs |
| `Future_Changes` | One row per change to a future: target sheet, parameter, technology or fuel, operation (`Multiply`, `Multiply_Ramp`, `Set`, `Copy_From_Tech`), value and years |
| `Uncertainty_Table` | One row per ranged uncertainty: which futures it applies to, the parameter, `Min_Value`, `Max_Value` and years |
| `Outputs` | Which input parameters and results go into the RDM CSVs |

With `Samples_Per_Future` = N, each named future that has an uncertainty
becomes N sampled futures. Sample `s` uses the same draw in every named
future, so `F01_s007` and `F02_s007` differ only by the futures' own changes.

Other commands:

| Command | Use it to |
|---|---|
| `rdm run … --compile-only` | Build and compile every future without solving |
| `rdm collect --run <Run_Name>` | Rebuild the CSVs after a run stopped part way, or after changing the Outputs sheet |

## Outputs

Each run has its own folder, `workspace\setups\<setup>\rdm\<Run_Name>\`
(`workspace\rdm\<Run_Name>\` for South Asia). Nothing under `config\` or
`inputs\` changes.

| File | Content |
|---|---|
| `RDM_Run_Status.csv` | Each future: `solved`, `compiled` or `missing` |
| `RDM_Experiment_Design.csv` | One row per future with its sampled values: the "X" of scenario discovery |
| `RDM_Inputs.csv` | The exported input parameters of every future |
| `RDM_Outputs.csv` | The exported results of every future |
| `interface.xlsx` | A copy of the workbook the run came from |
| `scenarios\<future>\scenario.yaml` | Each future as the edits applied to its root |

The CSVs join on `Future_ID`.

## Diagnosis and dashboards

`diagnosis_for_rdm/` looks inside a finished run. It is separate from the
pipeline: it only reads the run folder and writes to the run's `diagnosis\`
subfolder.

```bat
python diagnosis_for_rdm\run_diagnosis.py --list
python diagnosis_for_rdm\run_diagnosis.py --run test01
python diagnosis_for_rdm\build_results_dashboard.py
```

In Spyder, open `run_diagnosis.py`, set `"run"` in the `CONFIG` block, and
press F5.

| File in `<run>\diagnosis\` | What it shows |
|---|---|
| `RDM_Outputs_Dashboard.html` | Results of the solved futures: overview, power, countries, costs, interconnectors and robustness tabs, named futures side by side |
| `Perturbed_Inputs_Dashboard.html` | How each lever was drawn and where it landed, with an "Inputs by set" explorer |
| `Perturbed_Inputs.xlsx` | Every lever's draw in every future, and its effect on the inputs |
| `Inputs_by_Set.xlsx`, `Outputs_by_Set.xlsx` | Every input and result that differs between futures, by set and year |
| `Infeasibility_Diagnosis.xlsx` | For each unsolved future: verdict, suspect levers and conflicting bounds |
| `Unsolved_Futures.csv` | The futures that did not solve, with the solver's status |

Run it on the computer that solved the run for the full picture. It works from
a copied run folder too, using only `RDM_Inputs.csv`.

## Documentation

| Page | For |
|---|---|
| [OSTRAM and RDM user guide](docs/OSTRAM_RDM_User_Guide.md) | Step by step from a fresh clone to RDM results, with what runs at each stage |
| [RDM futures](docs/rdm.md) | Short reference: workbook columns, operations, checks, run folder, limits |
| [diagnosis_for_rdm](diagnosis_for_rdm/README.md) | Diagnosis options and how the infeasibility verdict is reached |
| [OSTRAM documentation](https://ostram.readthedocs.io/) | The OSTRAM pipeline, scenarios and data |

## Keeping up with OSTRAM

This branch follows the original OSTRAM. To bring in its updates:

```bat
git remote add upstream https://github.com/Climate-Lead-Group/OSTRAM.git
git fetch upstream
git merge upstream/main
```

The first line is needed only once.

## Licence and citation

Apache License 2.0, as OSTRAM (see [LICENSE](LICENSE)). When you use
OSTRAM-RDM, cite OSTRAM as given in [CITATION.cff](CITATION.cff).