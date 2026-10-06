# Infodemiology study of alpha-gal syndrome awareness in Australia: a comprehensive research protocol

**Australia's first infodemiology study of alpha-gal syndrome (AGS) can be built on the Romeiser et al. (2024) template but should extend it substantially, leveraging CSIRO's unique national surveillance dataset of 15,000+ alpha-gal IgE tests to directly correlate public awareness (measured by Google Trends search volume) with diagnostic testing patterns.** This protocol outlines a complete methodological framework covering search strategy, statistical analysis, content analysis, ethical governance, and novel innovations across eight domains. The study addresses a clear gap: no prior Australian awareness study exists for AGS, despite Australia having the world's highest rates of mammalian meat allergy (MMA), with some regions reaching **744 per 100,000** population.

---

## 1. Systematic infodemiology frameworks and reporting standards

The study should anchor its methodology in an established hierarchy of infodemiology frameworks, each serving a distinct function. The foundational conceptual framework is **Eysenbach (2009)**, who coined the term "infodemiology" and defined it as the science of distribution and determinants of health information on the internet. This study is a classic **demand-based passive infoveillance** study under Eysenbach's taxonomy — it analyses search behaviour to track public awareness of a disease condition.

For operational methodology, the primary guide should be the **Mavragani & Ochoa (2019) methodology framework** (*JMIR Public Health Surveillance*, 5(2):e13439), which provides the first dedicated step-by-step protocol for Google Trends research in health contexts. This framework mandates four steps: (1) keyword selection, including testing "search terms" versus "topics" and documenting quotation mark usage; (2) region selection with explicit documentation of geographic level; (3) time period selection with awareness that temporal granularity is determined by range length; and (4) category selection, with the "Health" filter recommended to reduce noise from non-health searches.

For reproducibility standards, the **Nuti et al. (2014) checklist** (*PLoS ONE*, 9(10):e109583) remains the benchmark documentation standard. Their systematic review of 70 Google Trends health studies found that **only 7% were fully reproducible** based on search strategy documentation — a finding that underscores the importance of complete reporting. The Nuti checklist requires documentation of: exact search terms and operators, rationale for selection, geographic area, time period, category filter, date of data retrieval, and Google property used.

The most recent and comprehensive quality framework is **Hölzl et al. (2024)** (*Social Science Research*, doi:10.1016/j.ssresearch.2024.103082), which synthesises all prior checklists and adds requirements for internal validity (cross-validation with related queries, confounding event checks), reliability (multiple sampling dates, reporting coefficient of variation), and generalizability (internet penetration rates, Google market share, demographic biases). The **Mavragani, Ochoa & Tsagarakis (2018) systematic review** (*J Med Internet Res*, 20(11):e270) provides additional methodological classification, categorising Google Trends studies into five approaches: visualisation, seasonality analysis, correlations, forecasting, and modelling.

**Minimum documentation requirements for this study** (synthesised across all frameworks):

- Exact search terms with quotation marks and operators
- Search type classification ("search term" vs. "topic" vs. "syndrome")
- Rationale for term selection, including pilot testing results
- Geographic setting: Australia (national) and state/territory breakdown
- Time period with exact dates
- Google Trends category: Health
- Google property: Web Search
- Date(s) of data retrieval
- Number of data pulls and approach to sampling variability
- Temporal resolution of downloaded data
- Whether "include low search volume regions" was enabled
- Validation data source description
- Statistical methods with software versions
- Confounders considered (media events, seasonality)
- Limitations explicitly enumerated

No specific STROBE extension exists for infodemiology, but the **STROBE** checklist for observational studies applies to the ecological study design, and **RECORD** (REporting of studies Conducted using Observational Routinely-collected health Data) guidelines apply to the pathology surveillance data component.

---

## 2. Google Trends and Glimpse methodology for Australian data

### Geographic resolution constraints

Google Trends provides data for Australia at **three levels**: country-wide, state/territory (8 units: NSW, VIC, QLD, WA, SA, TAS, NT, ACT), and possibly city-level for major metropolitan areas. Critically, **Google Trends does not use ABS Statistical Geography** — there is no SA2, SA3, or SA4 resolution available. The platform uses its own geographic hierarchy that does not correspond to the Australian Statistical Geography Standard (ASGS). For the United States, Google Trends offers DMA (Designated Market Area) sub-state resolution, but no equivalent exists for Australia. This means the finest reliable geographic resolution for this study is **state/territory level**, giving 8 geographic units for spatial analysis.

This creates a resolution mismatch: the pathology surveillance data can potentially be geocoded to **SA3 level (359 units, typically 30,000–130,000 people each)** or **SA4 level (108 units, typically 100,000–500,000+ people)**, but Google Trends cannot match this granularity. The recommended approach is to conduct geographic correlation at state/territory level for the Google Trends component, while presenting pathology data at SA3/SA4 level for a richer spatial picture of disease distribution. A **multi-resolution analysis strategy** is warranted: national time series analysis (Google Trends + pathology), state-level geographic correlation (Google Trends RSV × pathology testing rates), and SA3/SA4 spatial analysis (pathology data only, with tick distribution overlay).

### Temporal resolution rules

Google Trends automatically determines data granularity based on the time range:

| Time range | Granularity |
|---|---|
| < 9 months | Daily |
| 9 months to 5 years | Weekly |
| > 5 years | Monthly |

For a study spanning 2014–2024 (11 years), data will be **monthly**. To obtain weekly data for finer seasonal analysis, separate queries for overlapping 5-year windows can be "stitched" together using normalisation techniques available in `pytrends` (Python) or `gtrendsR` (R). Romeiser et al. used the full archive (2004–2023) at monthly resolution.

### Glimpse extension for Australian data

The Glimpse (Google Trends Supercharged) Chrome extension overlays estimated **absolute search volumes** on the standard Google Trends interface. Glimpse claims to provide absolute volume estimates for **any country**, including Australia. The key features relevant to this study are: absolute volume over time (monthly), related search query lists with volume estimates, and trend trajectory (deseasonalised trendline).

However, critical limitations exist. Glimpse's methodology for estimating absolute volumes is **proprietary and not peer-reviewed** — it likely combines Google Keyword Planner data, clickstream data, and other signals. No validation studies exist for its accuracy in any country, let alone Australia specifically. The "Discover Trends" browsing feature may be US-centric. The free tier is limited to approximately 10 lookups per month; paid plans are required for systematic research.

**Recommendation**: Use Glimpse to obtain absolute volume estimates as a **supplementary measure**, but treat standard Google Trends RSV (0–100) as the primary validated data source. Report both metrics. Validate by plotting RSV against Glimpse absolute volumes (Romeiser et al. found Spearman ρ = 0.99 for US data; this correlation should be verified for Australian data).

### Search term strategy for the Australian context

The search term strategy must capture the **distinctive Australian terminology**. "Mammalian meat allergy" (MMA) is the dominant term in Australian clinical and public discourse, used by ASCIA, Allergy & Anaphylaxis Australia, CSIRO, and the foundational researcher Prof. Sheryl van Nunen. "Alpha-gal syndrome" is the international/US-origin term that has gained traction through American media and CDC recognition. Both must be captured.

**Recommended primary terms** (each searched separately, as Glimpse does not support term combination):

1. **"alpha gal"** — Primary international lay term; directly comparable to Romeiser et al.
2. **"mammalian meat allergy"** — Primary Australian clinical and lay term
3. **"meat allergy"** — Broader lay term; higher volume but lower specificity
4. **"tick allergy"** — Broader term capturing tick-related allergy interest
5. **"paralysis tick"** — Australian-specific; replaces "lone star tick" from the US study

**Recommended secondary terms** (pilot test for adequate volume):

6. **"alpha-gal syndrome"** — Formal medical term; may have very low Australian volume
7. **"red meat allergy"** — Common lay description
8. **"tick bite allergy"** — Related but nonspecific
9. **"alpha-gal allergy"** — Spelling variant

**Methodological protocol**: Pilot all terms at national (Australia) level for 2004–present. Terms returning predominantly zero values should be excluded. Compare results with and without quotation marks. Apply the "Health" category filter. Test both "search term" and "topic" classifications where available (topics aggregate semantically related queries across spelling variations). Document which terms return the Google Trends "topic" or "syndrome" classification versus remaining as literal "search terms."

### Low-volume data challenges

Australia's population (**~26 million**) is approximately one-thirteenth of the US (~330 million), fundamentally limiting search volume. At state level, smaller jurisdictions (Tasmania ~570K, ACT ~460K, NT ~250K) will very frequently return zero values for niche medical terms. Even larger states may show zeros for "alpha-gal syndrome" in certain months. Google applies a **privacy threshold** below which data is suppressed — a zero means insufficient data, not necessarily zero searches.

**Mitigation strategies**: Use broader search terms where specific terms return zeros. Aggregate time into longer periods (quarterly or annual instead of monthly) for geographic analysis. Use "topics" rather than exact "search terms" to capture more queries. Collect data on multiple days and average (following Romeiser et al.'s 10-day protocol). Consider the `gtrendsR` option to include low search volume regions.

Australia's **Google market share (~93–95%)** is higher than both the global average (~84%) and the US (~87%), which is a significant advantage — Google Trends captures a very high proportion of all Australian web searches. Internet penetration is also high (~95%), though rural/remote areas, older Australians, and Indigenous communities may be underrepresented.

---

## 3. Correlation analysis frameworks for linking search data with surveillance data

### Core correlation methods

The fundamental analysis links two time series: Google Trends search volume (RSV or absolute volume) for AGS-related terms and pathology testing data (number of alpha-gal IgE tests requested and/or proportion positive) over the same period.

**Spearman rank correlation** is the recommended primary measure, given that Google Trends RSV is ordinal-scaled and surveillance count data are typically non-normally distributed. Romeiser et al. used Spearman correlation after confirming non-normality via Shapiro-Wilk tests, finding geographic correlations of ρ = 0.59–0.82 between alpha-gal and lone star tick searches across US states. For the Australian study, state-level Spearman correlations between search RSV and testing rates (per 100,000 population by state) should be computed across 3-year time blocks to ensure stable estimates.

**Cross-correlation function (CCF) analysis** extends basic correlation by evaluating the relationship at different time lags. This determines whether search volume **leads, coincides with, or lags** pathology testing volumes. Published examples show Google Trends leading disease surveillance by 1–4 weeks for infectious diseases (dengue: r = 0.91 at optimal lag; influenza: ~1 week lead). For AGS, the lag structure may differ — awareness-driven searches might precede testing requests (patient-initiated pathway) or follow media events that also trigger GP consultations. Implementation uses `stats::ccf()` in R, applied to pre-whitened or differenced time series to ensure stationarity.

**Granger causality testing** provides the most rigorous assessment of predictive relationships. Based on Vector Autoregressive (VAR) models, it tests whether past values of search volume help predict future pathology testing volumes beyond what the testing series' own history provides. A critical advantage: a BMC Medical Research Methodology study (2021) found Granger causality **reduces false positives by approximately two-thirds** compared to simple Pearson correlation in infodemiology studies, primarily by controlling for media-driven spurious associations. Stationarity must be confirmed via Augmented Dickey-Fuller tests before applying; if non-stationary, the Toda-Yamamoto modification should be used. Both directions should be tested (bidirectional), and **Benjamini-Hochberg correction** applied for multiple comparisons across search terms. R implementation: `vars` package for VAR models, `lmtest::grangertest()`.

**Distributed lag non-linear models (DLNMs)** offer the most flexible approach for assessing delayed, potentially non-linear relationships between search behaviour and testing patterns. The `dlnm` R package (Gasparrini et al., 2010, *Statistics in Medicine*) creates a "cross-basis" modelling both the exposure-response and lag-response relationships simultaneously. This is particularly valuable for AGS, where the causal pathway from tick bite → sensitisation → symptom onset → information seeking → testing may involve complex, variable delays.

### Handling the RSV-versus-counts challenge

Google Trends provides RSV on a 0–100 scale while surveillance data gives absolute counts or rates. Most published studies simply correlate the two without conversion — the correlation measures co-movement regardless of scale. Both series can be z-score normalised. Alternatively, log-transforming both series stabilises variance and improves linearity. For regression models, RSV can serve as a predictor in Poisson/negative binomial models with log(population) as an offset term.

### Ecological study design limitations

All Google Trends correlation studies are ecological by design and subject to the **ecological fallacy**: associations at the aggregate level may not hold individually. A high correlation between state-level search volume and state-level testing rates does not mean the people searching are those being tested. Media coverage is the principal confounder — search spikes may reflect media exposure rather than genuine awareness of personal risk. Demographic biases in internet use (age, socioeconomic status, urban/rural) cannot be assessed or controlled. These limitations must be explicitly reported, and causal language strictly avoided.

---

## 4. Australian-specific considerations that distinguish this study from the US

### Terminology divergence is the single most important methodological difference

In Australia, **"mammalian meat allergy" (MMA)** is the dominant term used by ASCIA, Allergy & Anaphylaxis Australia, CSIRO, TiARA (Tick-induced Allergies Research & Awareness), and Prof. Sheryl van Nunen, who first described the tick–meat allergy association in her seminal 2007 abstract and 2009 MJA paper. "Alpha-gal syndrome" is a more recent US-origin term driven by CDC recognition and American media coverage. Both terms circulate in Australian discourse, creating a **dual-terminology landscape** that the search strategy must capture. The study can uniquely analyse whether there has been a terminological shift over time — whether Australians have increasingly adopted "alpha-gal" terminology as US-driven media coverage has grown — which would itself be a finding about information globalisation in health literacy.

### Different tick vector, different ecology

*Ixodes holocyclus* (the Australian paralysis tick) is distributed along the **eastern seaboard from Cooktown (Far North QLD) to Lakes Entrance (VIC)**, generally within 20 km of the coast but extending 100+ km inland at moist escarpments. Its univoltine life cycle produces adult activity peaking **August–December** (late winter through early summer), with overall human exposure risk highest **September–March**. This creates a **reversed seasonal pattern** compared to the US lone star tick (*Amblyomma americanum*), which peaks April–September. The warm-season binary variable used by Romeiser et al. (May–September = 1 for the US) must be inverted for Australia: **October–March = 1** (or more refined: September–March). Range expansion modelling suggests *I. holocyclus* habitat may extend southward under climate change, potentially reaching areas around Perth and expanding into inland Victoria.

### Unique population-geography overlap

Approximately **60% of Australians** live within the range of *I. holocyclus* — a remarkably high proportion of exposed population compared to the US, where lone star tick distribution covers a subset of southeastern/eastern states. Australia's five largest cities are coastal, and three (Sydney, Melbourne partially, Brisbane) are within or adjacent to prime tick habitat. The Northern Beaches of Sydney — where van Nunen has her clinical practice and TiARA is based — is simultaneously one of the highest-risk tick areas and a wealthy, densely populated suburb with high internet usage. This concentration creates both an advantage (large exposed population generating search data) and a confound (most data comes from a few metro areas).

### Healthcare system differences

AGS testing in Australia operates through **Medicare-funded pathology services**, primarily via specific IgE to alpha-gal (Galactose-alpha-1,3-galactose, ImmunoCAP code U953). The MBS restricts allergy testing to **4 episodes per year with a maximum of 4 single allergens per request**, meaning alpha-gal testing competes with other allergen tests within these limits. The CSIRO surveillance partnership with Sonic Healthcare subsidiary laboratories (QML Pathology, Sullivan Nicolaides Pathology, Douglass Hanly Moir Pathology, Laverty Pathology) gives access to the largest private pathology dataset in the country, though this creates a potential geographic bias toward eastern states where these providers dominate. Unlike the US, **AGS is not a notifiable condition** in any Australian jurisdiction (Arkansas made it reportable in 2023), making pathology data the only systematic national surveillance mechanism.

### No prior awareness research exists

While the US CDC found that **42% of surveyed healthcare professionals** had never heard of AGS, no equivalent Australian clinician or public awareness study has been published. This study would be the first to quantify Australian AGS awareness using any methodology, filling a clear research gap. Given that Australia has the **world's highest rates of MMA** and national cases are increasing ~40% annually since 2020, the awareness gap is both a research finding and a public health concern.

---

## 5. Time series analysis methods

### Primary analytical model: quasi-Poisson regression with penalised splines

This is the core model used by Romeiser et al. and should be the primary approach. Quasi-Poisson regression accommodates **overdispersion** (variance exceeding mean) in count data by estimating a dispersion parameter φ. Penalised splines provide flexible, data-driven modelling of non-linear temporal trends without requiring parametric assumptions about the shape of the trend. The penalty term prevents overfitting by penalising excessive curvature.

**Model specification for the Australian study:**

```
log(E[Y_t]) = β₀ + f(time_t) + β₁ × warm_season_t + β₂ × media_t + offset(log(population_t))
```

Where `Y_t` = monthly count outcome (search volume or pathology tests), `f(time_t)` = penalised spline on year/month, `warm_season_t` = binary indicator (October–March = 1, April–September = 0, adjusted for Southern Hemisphere), and `media_t` = binary indicator for months containing major national media coverage of AGS/MMA.

Implementation in R uses `mgcv::gam()` with `family = quasipoisson` and `s(time, bs = "cr")` for penalised cubic regression splines, or `stats::glm()` with `splines::ns()` for natural splines. The dispersion parameter is reported as the ratio of residual deviance to degrees of freedom.

### Average Annual Percent Change (AAPC) calculation

AAPC provides a single summary metric communicating trend magnitude to non-technical audiences. Following the methodology of **Clegg et al. (2009)** (*Statistics in Medicine*, 28(29):3670–3682), AAPC is calculated as the weighted average of segment-specific Annual Percent Changes, with weights proportional to segment length. For the Australian study, calculate AAPC for: the full study period (2014–2024), any accelerated sub-period identified by visual inspection or joinpoint analysis, and each search term separately.

### Joinpoint regression for change-point detection

The **NCI Joinpoint Regression Program** (free, version 5.4.0) uses piecewise log-linear models connected at "joinpoints" identified through Monte Carlo permutation tests. Each segment yields an APC = 100 × (e^β − 1). This method identifies **when** search interest or testing volumes changed significantly — for instance, whether a specific media event, clinical guideline update, or research publication triggered an acceleration. Joinpoint regression works best with annual data and assumes piecewise linear trends; it is less suited for strong seasonality. Apply to annually aggregated data for trend detection, then use the quasi-Poisson model for full monthly analysis with seasonal adjustment.

### Seasonal analysis adapted for the Southern Hemisphere

The tick seasonality signal for *I. holocyclus* is distinct from the US pattern. Three approaches should be compared:

1. **Binary warm-season indicator**: October–March = 1 (Southern Hemisphere spring/summer; primary tick-human exposure period). Simple, directly comparable to Romeiser et al.'s approach.
2. **Harmonic (Fourier) terms**: Pairs of sin(2πkt/12) and cos(2πkt/12) with k = 1–2 harmonics, capturing sinusoidal seasonal patterns without assuming a specific warm/cool binary. More flexible than the binary approach.
3. **Cyclic penalised splines**: `s(month, bs = "cc")` in `mgcv::gam()`, providing fully nonparametric seasonal modelling. Most flexible but may overfit with limited data.

For the pathology surveillance data, seasonality should be examined separately from search data — tick bite frequency peaks September–March, but there may be a **diagnostic delay** of weeks to months between exposure and testing. Cross-correlation at different lags can quantify this delay.

### SARIMA for forecasting and model comparison

SARIMA(p,d,q)(P,D,Q)₁₂ models explicitly handle seasonal time series with period m = 12 (monthly data). `forecast::auto.arima()` in R automates parameter selection via AIC/BIC. SARIMAX extends this to include exogenous predictors (media coverage indicators, climate variables). SARIMA serves dual purposes: as a standalone forecasting model for search volume, and as a baseline for comparison with the quasi-Poisson approach.

### Interrupted time series analysis for media events

When major media events are identified (e.g., ABC Landline coverage, CSIRO press releases, Senate inquiry testimony), **interrupted time series analysis (ITSA)** can quantify both immediate level changes and sustained slope changes in search behaviour. Segmented regression within the quasi-Poisson framework tests: `β_intervention` (immediate change) and `β_time×intervention` (change in slope). Google's **CausalImpact** R package provides a Bayesian alternative, estimating counterfactual time series to determine what search volume would have been absent the media event, with posterior inference on the causal effect.

### Wavelet analysis for time-varying periodicity

Cross-wavelet analysis examines coherence between search volume and pathology testing series across both time and frequency dimensions simultaneously. This reveals whether the relationship between awareness and testing **changes over the study period** — for instance, whether correlation strengthens as awareness grows. The `WaveletComp` or `biwavelet` R packages produce time-frequency coherence plots with phase information showing lead-lag relationships at each periodicity. This is particularly suited to detecting changes in seasonal coupling as AGS awareness evolves.

---

## 6. Content analysis of related search queries

### Data collection protocol

Following Romeiser et al.'s validated approach, collect related search query lists from Glimpse for each primary search term at 2:00 PM daily for **10 consecutive days**. Combine lists across days, remove duplicates, and catalogue unique queries. Romeiser et al. identified **371 unique related searches** for "alpha gal" in the US; the Australian count will likely be smaller due to lower search volumes.

### Analytical framework: directed content analysis

A **directed content analysis** approach (per Hsieh & Shannon, 2005, *Qualitative Health Research*, 15(9):1277–88) is recommended, using Romeiser et al.'s 10-theme framework as the initial coding scheme while allowing new Australian-specific themes to emerge inductively. The 10 themes from the US study were: diet (25.9%), symptoms (11.9%), diagnosis/testing (10.8%), general education (10.5%), specific sources/locations (10.2%), treatment (9.4%), medications/contraindications (7.8%), tick-related, alternative terminology, and unrelated/other.

**Australian-specific themes to anticipate**: queries about *Ixodes holocyclus*/paralysis tick (replacing lone star tick), references to Australian health services (ASCIA, HealthDirect, TiARA), MMA-specific terminology, Medicare/PBS-related queries, and geographic queries about tick-endemic regions (Northern Beaches, Central Coast, Sunshine Coast).

### Coding procedure

Two independent coders should classify all unique queries into themes and subthemes. **Cohen's kappa (κ)** measures inter-rater reliability, with κ ≥ 0.70 as the target threshold (κ ≥ 0.61 constitutes "substantial agreement"). Discrepancies are resolved through discussion and consensus. The process iterates: initial coding → comparison → resolution → subcategory refinement within each theme.

A key limitation acknowledged by Romeiser et al. applies equally here: Glimpse does not provide absolute volume for individual related queries, so theme proportions represent **diversity of query types** (number of unique queries), not necessarily search popularity.

### Enhancement through thematic analysis

Supplement the directed content analysis with elements of **Braun & Clarke's reflexive thematic analysis** (2006, *Qualitative Research in Psychology*, 3(2):77–101): familiarisation with data, initial coding, theme searching, theme reviewing, defining/naming, and reporting. This hybrid approach preserves comparability with the US study while allowing richer interpretation of Australian search patterns.

---

## 7. Data linkage, privacy, and ethical governance

### Ethics approval pathway

The study involves two data types: publicly available Google Trends data and aggregated de-identified pathology surveillance data. Under the **NHMRC National Statement on Ethical Conduct in Human Research (2023)**, Section 2.1, research may be eligible for **exemption from ethics review** if it uses collections of data from which all personal identifiers have been removed (condition a) or uses publicly available information (condition d).

Google Trends data requires no ethics approval — it is publicly accessible, fully aggregated, and anonymised. Romeiser et al. reported no IRB/ethics requirement for their study. The pathology surveillance data, if obtained as aggregated summaries (total tests per state per quarter, positivity rates by region) with no individual identifiers, similarly falls outside the Privacy Act 1988 definition of "personal information."

**Recommended pathway**: Submit a **low-risk ethics notification or exemption application** to the institutional HREC (e.g., CSIRO's Ethics Committee), citing National Statement 2023 Section 2.1 conditions (a) and (d). Prepare a brief **Privacy Impact Assessment** documenting that no personal information is used. Execute **data sharing agreements** with pathology data custodians (Sonic Healthcare subsidiaries) specifying aggregated, de-identified data provision only.

### Australian Privacy Principles

The **Australian Privacy Principles (APPs)** under the Privacy Act 1988 apply to personal information. Aggregated population-level statistics without individual identifiers **fall outside APP scope**. Section 95 Guidelines are relevant when handling personal health information for research but do not apply to publicly available aggregated data. NHMRC's **Principles for Accessing and Using Publicly Funded Data for Health Research (2015)** support the use of these data types for research, emphasising that data access should be efficient and transparent while protecting individual privacy.

### Data governance at CSIRO

CSIRO has established institutional data governance policies and ethics processes. As the pathology surveillance data was collected through formal partnerships with QML, Douglass Hanly Moir, Sullivan Nicolaides, and Laverty Pathology, existing data sharing agreements may already cover research use. Verify that the Google Trends analysis is within scope of existing approvals or obtain an amendment. Document all data handling procedures, storage locations, and access controls in a **Data Management Plan** conforming to FAIR principles (Findable, Accessible, Interoperable, Reusable).

### Privacy-preserving record linkage context

While this ecological study does not require individual-level linkage, Australia's expertise in **Privacy Preserving Record Linkage (PPRL)** using Bloom filters is worth noting for future extensions. If subsequent studies require linking individual pathology records with clinical or administrative datasets, established Australian data linkage centres (CHeReL in NSW/ACT, CVDL in Victoria, AIHW DISC nationally) provide governed pathways.

---

## 8. Study design innovations beyond Romeiser et al.

### Supplementary data sources to triangulate awareness

**Wikipedia pageview data** offers a freely available, granular complement to Google Trends. The Pageviews Analysis tool (pageviews.toolforge.org) provides daily view counts for articles on "Alpha-gal allergy," "Mammalian meat allergy," and "Ixodes holocyclus." Alibudbud (2023, *Frontiers in Big Data*) and Mondia et al. (2022, *Frontiers in Oncology*) have validated Wikipedia pageviews as an infodemiology metric. Unlike Google Trends (which captures information-seeking behaviour), Wikipedia captures **information-consumption behaviour**, providing a complementary signal.

**News media monitoring** using MediaCloud (open-source) or GDELT (Global Database of Events, Language, and Tone) can **quantify the dose of media exposure** rather than treating it as a simple binary variable. By counting the number of Australian media articles mentioning AGS/MMA per month, the study can model a continuous media exposure variable, enabling more precise estimation of the media–awareness–testing pathway. This directly addresses a limitation of Romeiser et al., who used a binary media indicator.

**YouTube Search trends** via Google Trends' YouTube Search filter can capture video-specific health information seeking. Social media analysis of **Reddit** (r/alphagal, r/Allergies, r/australia) and **Twitter/X** using sentiment analysis tools can reveal patient experiences, misinformation themes, and information needs not captured by search query data alone. Emerging evidence shows GPT-4-class LLMs outperform traditional NLP tools (VADER, DistilBERT) for nuanced health sentiment classification.

**HealthDirect Australia** (healthdirect.gov.au) analytics — page views and search terms for allergy-related content — would provide Australia-specific health information-seeking data from the government's primary health portal. This would require a data sharing agreement with the Australian Digital Health Agency.

### Advanced statistical innovations

**Bayesian Structural Time Series (BSTS)** models (Scott & Varian, 2014) represent the most significant methodological advancement over Romeiser et al.'s frequentist approach. BSTS simultaneously decomposes time series into trend, seasonality, and regression components while providing **full uncertainty quantification through posterior distributions**. Spike-and-slab priors enable automatic variable selection from multiple search terms, and the framework naturally incorporates multiple covariates (weather data, media volume, policy changes). The `bsts` R package implements this approach; Kohns & Siliverstovs (2022, *International Journal of Forecasting*) demonstrated its superiority for Google Trends-based nowcasting.

**CausalImpact analysis** (Brodersen et al., 2015, *Annals of Applied Statistics*) — developed by Google — extends BSTS to estimate **counterfactual scenarios**: what would search volume or testing rates have been in the absence of a specific intervention (media event, clinical guideline update, Senate inquiry)? This provides causal effect estimates with Bayesian credible intervals, substantially more rigorous than the binary media variable approach used by Romeiser et al.

**Nowcasting and forecasting** represent a novel applied contribution: can current Google Trends data predict near-future pathology testing demand before official data becomes available? This has direct practical value for pathology laboratory capacity planning and public health resource allocation. Cross-correlation with lag structures establishes the predictive window; BSTS or SARIMAX models generate forecasts.

### Spatial analysis innovations

**GIS overlay analysis** combining three spatial layers — Google Trends interest by state, *I. holocyclus* distribution maps, and AGS testing rates by SA3/SA4 — would produce a richer geographic picture than any prior study. Spatial statistics including **Moran's I** for spatial autocorrelation, **Kulldorff's spatial scan statistic** for cluster detection, and **geographically weighted regression** for spatially varying relationships can identify areas where awareness lags behind disease burden (potential intervention targets) or where awareness exceeds burden (potentially media-driven).

### Climate-environment integration

Integration with **Bureau of Meteorology (BoM) climate data** — temperature, humidity, rainfall — enables modelling of the full causal chain: climate → tick activity → human exposure → sensitisation → symptoms → information seeking → testing. Multivariate models can disentangle weather-driven seasonal patterns from awareness-driven search behaviour, addressing a fundamental confound in all infodemiology studies of vector-borne diseases.

### Extended infodemiology framework

Building on Tan et al.'s (2022) framework, the study can examine four dimensions of health information dynamics: **content** (what people search for), **congruence** (whether public social media posts reveal different concerns from private searches), **context** (how the information environment shapes behaviour), and **conduits** (how information flows through search engines, social media, health portals, and Wikipedia). This multi-platform triangulation would make the study methodologically distinctive.

---

## Implementation timeline and analytical workflow

**Phase 1 — Search term piloting and data collection (Months 1–2):** Pilot all candidate search terms at national level. Identify terms with sufficient volume. Implement 10-day data collection protocol via Glimpse. Download standard Google Trends RSV for all viable terms at national and state levels. Compile media event timeline from Australian sources (ABC, ASCIA, TiARA, CSIRO, Senate records). Download Wikipedia pageview data. Set up MediaCloud/GDELT monitoring.

**Phase 2 — Data preparation and descriptive analysis (Months 2–3):** Clean and merge Google Trends, pathology surveillance, and supplementary data sources. Align temporal resolution (monthly). Calculate descriptive statistics. Produce choropleth maps. Assess stationarity (ADF tests). Examine distributions (Shapiro-Wilk). Compute dispersion diagnostics.

**Phase 3 — Time series modelling (Months 3–4):** Fit quasi-Poisson regression models with penalised splines for each search term and pathology testing series. Calculate AAPC for full period and identified sub-periods. Run joinpoint regression on annually aggregated data. Fit SARIMA/BSTS models. Conduct ITSA/CausalImpact analysis for identified media events.

**Phase 4 — Correlation and spatial analysis (Month 4):** Compute Spearman correlations between search RSV and testing rates at state level across time blocks. Run cross-correlation functions to identify lead-lag relationships. Conduct Granger causality tests (both directions, with BH correction). Fit DLNM models for non-linear lagged effects. Perform spatial analysis of pathology data at SA3/SA4 level with tick distribution overlay.

**Phase 5 — Content analysis (Months 4–5):** Catalogue and deduplicate related search queries. Two coders independently classify using directed content analysis with Romeiser et al.'s framework. Calculate Cohen's κ. Resolve discrepancies. Identify Australian-specific themes. Analyse temporal evolution of query themes.

**Phase 6 — Synthesis and reporting (Months 5–6):** Integrate findings across all analytical streams. Write manuscript following Mavragani & Ochoa (2019), Nuti et al. (2014), and Hölzl et al. (2024) reporting standards plus STROBE for ecological study design. Prepare supplementary materials including full search strategy documentation, sensitivity analyses, and reproducibility information.

## Conclusion

This protocol positions the Australian AGS infodemiology study to substantially advance beyond Romeiser et al.'s foundational work in three ways. First, the **direct linkage of awareness data with clinical surveillance data** (15,000+ alpha-gal IgE tests) is something the US study could not do, and enables true correlation analysis between public information-seeking and diagnostic testing behaviour. Second, **multi-platform triangulation** — combining Google Trends, Wikipedia pageviews, news media quantification, and potentially social media analysis — provides a more complete picture of the information ecosystem than any single-platform study. Third, the **Bayesian analytical framework** (BSTS, CausalImpact) offers more rigorous causal inference and uncertainty quantification than the frequentist approach used by Romeiser et al. The primary constraint is Google Trends' state-level geographic resolution for Australia, which cannot match the SA3/SA4 granularity available in the pathology data — a limitation that should be addressed through the multi-resolution analysis strategy. The study will produce the first quantitative assessment of AGS awareness in a country that carries the world's highest disease burden, filling a critical gap in both Australian public health and global infodemiology scholarship.
