# Running the decision-support application

The application **reads** the tables the analysis pipeline produced. It does not
fit, train or tune anything at runtime. Its interactive controls explore the
evidence; they never overwrite the official pre-registered results.

## 1. Environment, once

From the project root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

macOS or Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## 2. Data

The raw data is not committed. See [`data/README.md`](data/README.md) for the
download command, licence and checksum.

## 3. Run the pipeline, in order

```bash
cd src
../.venv/Scripts/python.exe data_audit.py                # Phase 1: audit, changes nothing
../.venv/Scripts/python.exe timestamp_correction.py      # Phase 2A: timestamp hypothesis
../.venv/Scripts/python.exe prepare_data.py              # Phase 2B-D: processed dataset
../.venv/Scripts/python.exe baseline_model.py            # Phase 2E-H: baseline, sensitivity
../.venv/Scripts/python.exe ml_challenger.py             # Phase 3: pooled curve + challenger
../.venv/Scripts/python.exe decision_register.py         # Phase 4: decision register
../.venv/Scripts/python.exe build_deliverables.py        # Phase 4: deck and memo PDF
../.venv/Scripts/python.exe export_presentation_tables.py  # Phase 4B: chart tables
```

Roughly two to four minutes, most of it in `ml_challenger.py`.

## 4. Start the application

```bash
.venv/Scripts/python.exe -m streamlit run app/app.py
```

Opens at `http://localhost:8501`. For a different port, add
`--server.port 8512`.

## 5. The five sections

1. **Executive cockpit** — the recommendation, energy accounting and leading
   events. A price slider, method selector, turbine filter and an energy-basis
   toggle. Readable in about thirty seconds.
2. **Investigation explorer** — the event register as a scatter plot, a monthly
   heatmap and a ranked table, with filters and a per-event timeline, hypotheses,
   required records and escalation criteria.
3. **Method and scenario lab** — why the three methods disagree, and the
   synthetic detection benchmark. Model performance appears here and nowhere else.
4. **Data trust** — the audit trail as a funnel, exclusion chart, completeness
   heatmap, timestamp test and missing-gap chart.
5. **Ask the analysis** — grounded question answering over the project's own files.

---

# Optional: the "Ask the analysis" assistant

**The application is fully usable without an API key.** Without one, the page runs
the same local retrieval and shows the matching passages from the project's own
files, clearly labelled as project text rather than an AI-generated answer.

## What is sent to the model

Only the retrieved passages. **The raw dataset is never sent anywhere.**

Retrieval is local and transparent: these files are split into chunks and scored
by how many of the question's terms they contain.

| Retrieved from |
|---|
| `README.md` |
| `docs/phase_1_findings.md` |
| `docs/phase_2_findings.md` |
| `docs/phase_3_method.md` |
| `docs/phase_3_findings.md` |
| `docs/phase_4_findings.md` |
| `docs/methodology_decisions.md` |
| `docs/executive_memo.md` |
| the CSVs in `outputs/tables/` (tables over 40 rows are truncated to 25) |

There are no embeddings. The evidence pack is small, term overlap works, and a
reader can check why a passage was selected. The passages used for each answer
are listed under "Evidence used".

## Local setup

Either set an environment variable:

```bash
set OPENAI_API_KEY=sk-REPLACE-WITH-YOUR-OWN-KEY
```

Or copy the example secrets file and fill it in:

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

`.streamlit/secrets.toml` is git-ignored. **Never commit a real key.**

## Streamlit Community Cloud

In the app's dashboard, open **Settings → Secrets** and paste:

```toml
OPENAI_API_KEY = "sk-REPLACE-WITH-YOUR-OWN-KEY"
OPENAI_MODEL = "gpt-6-luna"
```

Secrets are held server-side and are never exposed to the browser. Do not put a
key in a text input, a CSV or the repository.

## Configuration

| Setting | Default | Notes |
|---|---|---|
| `OPENAI_API_KEY` | none | Environment variable or server-side secret only |
| `OPENAI_MODEL` | `gpt-6-luna` | OpenAI's efficient model for focused, high-volume tasks, which suits grounded question answering over a small evidence pack. `gpt-6.1-sol` and `gpt-6-astra` are more capable and cost more. |
| Response limit | 700 output tokens | `MAX_OUTPUT_TOKENS` in `app/assistant.py` |
| Per-session questions | 12 | `MAX_QUESTIONS_PER_SESSION`, to limit accidental cost |
| Passages per question | 8 | `MAX_CHUNKS_SENT` |

**API use may incur charges** on the account that owns the key.

## Turning the assistant off

Remove `OPENAI_API_KEY` from the environment and from
`.streamlit/secrets.toml`. The page keeps working and returns retrieved passages
instead. To remove the page entirely, delete `"Ask the analysis"` from the `PAGES`
list in `app/app.py`.

## Errors it handles

Authentication failure, rate limit or quota, connection failure, and an
unavailable model each produce a specific message. **None of them affects the
other four pages.**

## Troubleshooting

**`FileNotFoundError` on a CSV** — the pipeline has not been run, or not all of
it. Run step 3 in order, including `export_presentation_tables.py`.

**Charts look stale after editing `app/charts.py`** — Streamlit reloads the main
script but not imported modules. Restart the server.

**Port already in use** — pass a different `--server.port`.

---

Independent project using public data: ENGIE La Haute Borne wind farm, Etalab
Open Licence 2.0, obtained via the OpenOA repository (NatLabRockies/OpenOA). No
Clir Renewables data, software or methodology is used, and nothing here describes
Clir, its platform, its methods or its customers.
