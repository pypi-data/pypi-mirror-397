# ohmly - An electrical and mechanical analysis tool of overhead conductors

Ohmly is a lightweight Python library for engineers who work with **overhead
transmission and distribution lines**.

It provides the core mechanical tools needed to evaluate conductor behavior under
real-world loading conditions: sag, tension, wind, ice, temperature, variation,
and more.

The library includes:

-   A built-in database of conductor properties.
-   Catenary-based sag-tension calculations.
-   Multiple load-case (hypothesis evaluation).
-   Temperature-dependent tension models.
-   Wind & ice loading.

> [!IMPORTANT]
> All mechanical calculations currently follow **Spanish ITC-LAT 07** only.
> Other regulations are not yet implemented.

> [!WARNING]
> Electrical analysis modules will be added in future releases.


## Disclaimer

Ohmly is an MIT-licensed engineering support tool.

Mechanical calculations currently follow Spanish ITC-LAT 07 only and must be
validated by a qualified engineer.

See [DISCLAIMER.md](docs/DISCLAIMER.md) for full details.


## Why Use Ohmly?

-   Fast and lightweight: Designed for quick analysis without heavy dependencies.
-   Regulation-aware: All mechanical calculations follow ITC-LAT 07, ensuring compliance.
-   Flexible scenarios: Easily define custom hypotheses, spans, and environmental conditions.
-   Clear results: Sag-tension tables are easy to read and integrate into reports.


## Documentation

Comprehensive documentation, tutorials, and normative explanations are
available in the project documentation.

The docs cover:

- Mechanical analysis workflow (ITC-LAT 07)
- Conductor definition (database and manual)
- Mechanical analysis zones
- Wind, ice, and apparent load calculations
- Hypothesis definition and validation
- Sag–tension tables and controlling hypotheses

📘 **Read the full documentation here:**  
https://ohmly.readthedocs.io/en/stable/


## Installation

```bash
pip install ohmly
```


## Getting Started

Here's a minimal example that shows how fast it is to compute sag-tension results.

```python
from ohmly import ConductorRepository, MechAnalysis, MechAnalysisZone, MechAnalysisHypothesis

# 1. Load a conductor from the internal database
repo = ConductorRepository()
conductor = repo.get(legacy_code="LA 180")

# 2. Create a mechanical analysis context for zone A
mech = MechAnalysis(conductor, MechAnalysisZone.A)

# 3. Define hypotheses (scenarios) to evaluate
eds = MechAnalysisHypothesis(name="EDS", temp=15, rts_factor=0.15)  # Every-Day Stress
chs = MechAnalysisHypothesis(name="CHS", temp=-5, rts_factor=0.2)   # Cold-Hour Stress

hypos = [eds, chs]

# 4. Define span lengths (in meters)
spans = [100, 200, 300]

# 5. Compute sag-tension table
sagten_table = mech.stt(hypos, spans)

# 6. Print results
print(sagten_table)
```

Sample output:
```bash
                EDS                 CHS
  Span   T (daN), RTS (%)     T (daN), RTS (%)
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   100   930.8383, 14.3338   1298.8000, 20.0000
   200   974.1000, 15.0000   1160.4121, 17.8690
   300   974.1000, 15.0000   1067.9360, 16.4450
```

For a complete, regulation-aligned explanation of each step, see the
[Mechanical Analysis documentation](docs/mechanical-analysis.md).


---

## Project Structure

- `ohmly/` – Core library code
- `docs/` – Mechanical analysis documentation and tutorials (ITC-LAT 07)


