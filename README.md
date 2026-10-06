# aGal_infoepi: infodemiology of alpha-gal syndrome / mammalian meat allergy in Australia

This project measures public awareness of, and information-seeking about, **alpha-gal syndrome
(AGS)**, known in Australia as **mammalian meat allergy (MMA)**. It uses two digital data sources:

* **Google Trends**: monthly relative search volume (RSV) for Australia, 2014 onwards, for
  AGS/MMA terms, tick terms and a control term.
* **MediaCloud**: Australian online news coverage of AGS/MMA.

The analysis covers long-term trends, seasonality (aligned to the *Ixodes holocyclus* paralysis
tick season, Oct–Mar), media–search associations and the effect of specific media events. It is
loosely modelled on Romeiser et al.'s US alpha-gal Google Trends study and adapted to Australian
terminology and seasons.

**Author:** Alexander W. Gofton (CSIRO)

---

## Repository structure

```
aGal_infoepi/
├── code/                                  # Current data-collection pipeline
│   ├── google_trends_downloader.py        # pytrends downloader (single-term + co-queries, cat 0 & 45)
│   ├── schedule_run.sh                    # Runs the downloader once a day for N days
│   └── archive/                           # Previous downloader version (2014-02 to 2026-02, cat 0)
├── data/
│   ├── google_trends_monthly_au_<term>_<YYYY-MM-DD>.csv   # Repeated daily downloads (Jul–Oct 2026)
│   ├── google_trends_2014-01_2026-10/     # Extended-range downloads (single + co-query, cat 0 & 45)
│   │   └── download_log.csv               # Provenance log for every query
│   └── media_cloud/                       # MediaCloud exports (counts, article list, sources, words)
├── new_analysis/                          # Current analysis
│   ├── code/ags_awareness_analysis.qmd    # Main Quarto (R) analysis document
│   ├── figures/                           # Figures written by the .qmd (fig1–fig13, fig_s1–s3)
│   └── processed_data/                    # Averaged Google Trends series, monthly media counts
├── old_analysis/                          # Earlier analysis (Feb–Mar 2026 downloads), kept for comparison
│   ├── code/                              # Earlier .qmd analyses and R helper functions
│   ├── data/, mediacloud/, processed_data/, figures/
├── CSIRO_colours.R                        # CSIRO brand colour palette for plots
├── LICENSE
└── README.md
```

Rendered HTML reports, Python virtual environments, `__pycache__` and scheduler logs are not
tracked (see `.gitignore`). To rebuild the reports, see [Reproducing the analysis](#reproducing-the-analysis).

---

## Data

### Google Trends

| Item | Value |
|---|---|
| Source | Google Trends via [`pytrends`](https://github.com/GeneralMills/pytrends) (`interest_over_time`) |
| Geography | Australia (`geo = "AU"`), national |
| Resolution | Monthly (time range > 5 years) |
| Search type | Search terms (not Topics), no operators |
| Property | Web Search |
| Terms | `alpha gal`, `Alpha-gal syndrome`, `mammalian meat allergy`, `meat allergy`, `tick allergy`, `paralysis tick`, `ticks`, `food allergy` (control) |

**Repeated downloads.** Google Trends returns a sample of searches, so values vary slightly
between requests. Each term was downloaded many times on different days, and the analysis uses
the mean RSV across downloads. The coefficient of variation across downloads is reported as a
reliability measure.

**Two download sets:**

1. `data/google_trends_monthly_au_*.csv`: 14 download days (1–3 Jul 2026 and
   22 Sep–2 Oct 2026). Single-term queries, category 0 (All categories), Feb 2014–Feb 2026. These
   are the inputs to `new_analysis/`.
2. `data/google_trends_2014-01_2026-10/`: extended range (Jan 2014–Oct 2026) from the current
   downloader. It adds:
   * **co-queries** (up to 5 terms per payload, sharing one scale) so that term levels can be
     compared directly, e.g. "alpha gal" vs "mammalian meat allergy";
   * **category 45 (Health)** as a sensitivity analysis alongside category 0;
   * AEST timezone (`tz = -600`);
   * `download_log.csv`, which records every query's parameters, status and whether the final
     month was incomplete (`last_month_partial`). Drop partial months from analyses.

> **Interpreting RSV.** Each single-term series is scaled 0–100 relative to *its own* busiest
> month. Shapes can be compared between terms, but levels cannot. Use the co-query files to
> compare levels.

### MediaCloud

Exports from the [MediaCloud](https://www.mediacloud.org) Australian online news collection
(`data/media_cloud/`):

| File suffix | Contents |
|---|---|
| `-counts.csv` | Daily matching article count, total collection size and ratio |
| `-content.csv` | One row per matching article: date, outlet, title, URL (no article text) |
| `-top-sources.csv` | Outlets with the most matching articles |
| `-top-words.csv` | Most frequent words in matching articles |

The analysis removes off-topic articles with title-based regex filters and de-duplicates
syndicated stories.

---

## Analysis overview (`new_analysis/code/ags_awareness_analysis.qmd`)

1. **Data loading.** All Google Trends CSVs are found automatically, and the term and download
   date are parsed from the file names. MediaCloud data are filtered and aggregated to months.
2. **Data reliability.** Sampling variability across downloads (CV), agreement between download
   batches (Lin's CCC), and agreement with the earlier Feb–Mar 2026 downloads.
3. **Descriptive trends.** Faceted time series, shape comparison of AGS/MMA terms, summary
   statistics and an annual heatmap.
4. **Media coverage.** Media timeline against search interest, article list, coverage by year,
   collection-size check and top sources.
5. **Seasonality.** STL-detrended seasonal profiles and Kruskal–Wallis tests.
6. **Trend quantification.** Quasi-Poisson GAMs with a cyclic seasonal smooth, trend derivatives
   to find *when* interest was rising, and joinpoint (segmented) regression with annual percent
   change.
7. **Media–search association.** Spearman correlations, cross-correlation (lead–lag), a GAM of
   the media effect after adjusting for trend and season, and Granger causality.
8. **Media events.** Interrupted time series for the August 2023 media cluster (Newey–West SEs),
   and excess search interest for Nov 2025–Feb 2026 compared with a pre-event forecast.
9. **Summary, limitations and recommendations** for the next data pull.

Figures are saved to `new_analysis/figures/` and processed tables to `new_analysis/processed_data/`.

---

## Reproducing the analysis

### Requirements

**Python** (data collection), 3.10 or later:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas pytrends
```

**R** (analysis), 4.3 or later, plus [Quarto](https://quarto.org):

```r
install.packages(c("tidyverse", "patchwork", "mgcv", "tseries", "lmtest",
                   "sandwich", "segmented", "vars", "scales"))
```

### 1. Download Google Trends data (optional; the data are already in `data/`)

```bash
# Single run (writes to data/google_trends_2014-01_2026-10/ by default)
python3 code/google_trends_downloader.py

# Or write to another folder
python3 code/google_trends_downloader.py --output-dir /path/to/folder

# Repeated daily downloads (default 20 runs, 24 h apart), in the background
nohup bash code/schedule_run.sh > code/schedule_run.nohup 2>&1 &
```

Run these from the project root. Google rate-limits requests, so the downloader waits between
calls and retries with exponential backoff. `schedule_run.sh` sets `PYTHON_BIN` to the Python
interpreter that has `pytrends` installed; edit it for your system.

### 2. Render the analysis

```bash
cd new_analysis/code
quarto render ags_awareness_analysis.qmd
```

This writes a self-contained `ags_awareness_analysis.html` (all resources embedded) and
regenerates the figures and processed data.

---

## Limitations

* Google Trends gives **relative**, sampled search volumes, not absolute counts. Separately
  queried terms cannot be compared on level.
* The finest Google Trends geography for Australia is state/territory. There is no ABS SA2–SA4
  resolution.
* Category 0 (All) includes non-health searches, e.g. "ticks" in non-medical contexts. Category 45
  is downloaded as a sensitivity check.
* The design is **ecological**. Media–search associations are population-level and do not show
  causation.
* MediaCloud covers online news only (no TV, radio or social media), its collection size changes
  over time, and off-topic filtering is title-based.

For the full discussion, see the *Limitations* section of the analysis document.

---

## Licence

* **Code**: [MIT](LICENSE)
* **Data, figures and text**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Third-party data stay subject to the terms of Google Trends and MediaCloud. See [LICENSE](LICENSE).

## Citation

If you use this code or data, please cite:

> Gofton, A. W. (2026). *aGal_infoepi: Infodemiology of alpha-gal syndrome / mammalian meat
> allergy in Australia* [Computer software]. https://github.com/alexandergofton/aGal_infoepi

## Contact

Alexander W. Gofton (CSIRO). Please open an issue on GitHub.
