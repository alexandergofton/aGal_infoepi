# Infodemiology Analysis of Alpha-Gal Syndrome Awareness in Australia
Alexander W. Gofton
2026-03-02

- [1. Data Loading and Averaging](#1-data-loading-and-averaging)
  - [1.1 Load Google Trends Data](#11-load-google-trends-data)
  - [1.2 Average Across Downloads and Assess Sampling
    Variability](#12-average-across-downloads-and-assess-sampling-variability)
  - [1.3 Load MediaCloud Data](#13-load-mediacloud-data)
- [2. Descriptive Trends in Search
  Interest](#2-descriptive-trends-in-search-interest)
  - [2.1 Time Series of All Search
    Terms](#21-time-series-of-all-search-terms)
  - [2.2 AGS-Specific Terms Combined](#22-ags-specific-terms-combined)
  - [2.3 Summary Statistics per Term](#23-summary-statistics-per-term)
  - [2.4 Heatmap of Annual Search
    Interest](#24-heatmap-of-annual-search-interest)
- [3. Media Coverage Analysis](#3-media-coverage-analysis)
  - [3.1 Monthly Media Coverage
    Timeline](#31-monthly-media-coverage-timeline)
  - [3.2 Key Media Events](#32-key-media-events)
  - [3.3 Media Coverage by Year](#33-media-coverage-by-year)
  - [3.4 Top Media Sources](#34-top-media-sources)
- [4. Seasonality Analysis](#4-seasonality-analysis)
  - [4.1 Monthly Seasonal Patterns](#41-monthly-seasonal-patterns)
  - [4.2 Kruskal-Wallis Test for
    Seasonality](#42-kruskal-wallis-test-for-seasonality)
  - [4.3 Warm vs Cool Season
    Comparison](#43-warm-vs-cool-season-comparison)
- [5. Trend Quantification](#5-trend-quantification)
  - [5.1 Quasi-Poisson GAM with Penalised
    Splines](#51-quasi-poisson-gam-with-penalised-splines)
  - [5.2 GAM Trend Visualisation](#52-gam-trend-visualisation)
  - [5.3 Segmented Regression (Joinpoint
    Analysis)](#53-segmented-regression-joinpoint-analysis)
  - [5.4 Joinpoint Visualisation](#54-joinpoint-visualisation)
- [6. Media-Awareness Correlation
  Analysis](#6-media-awareness-correlation-analysis)
  - [6.1 Spearman Correlations](#61-spearman-correlations)
  - [6.2 Cross-Correlation Analysis](#62-cross-correlation-analysis)
  - [6.3 Optimal Lag Identification](#63-optimal-lag-identification)
- [7. Granger Causality Testing](#7-granger-causality-testing)
  - [7.1 Stationarity Tests](#71-stationarity-tests)
  - [7.2 VAR Model and Granger
    Causality](#72-var-model-and-granger-causality)
- [8. Interrupted Time Series
  Analysis](#8-interrupted-time-series-analysis)
  - [8.1 Identify Key Media Events](#81-identify-key-media-events)
  - [8.2 ITS Analysis for Aug 2023 Media
    Event](#82-its-analysis-for-aug-2023-media-event)
  - [8.3 ITS Analysis for Nov 2025 Coroner
    Inquest](#83-its-analysis-for-nov-2025-coroner-inquest)
- [9. Summary of Findings](#9-summary-of-findings)

``` r
library(tidyverse)
library(patchwork)
library(mgcv)
library(forecast)
library(tseries)
library(lmtest)
library(sandwich)
library(segmented)
library(zoo)
library(scales)
library(vars)

home_dir <- "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi"
data_dir <- file.path(home_dir, "data")
processed_dir <- file.path(home_dir, "processed_data")
media_dir <- file.path(home_dir, "mediacloud")
fig_dir <- file.path(home_dir, "figures")

search_terms <- c(
  "alpha_gal",
  "alpha-gal_syndrome",
  "food_allergy",
  "mammalian_meat_allergy",
  "paralysis_tick",
  "red_meat_allergy",
  "meat_allergy",
  "tick_allergy"
)

# Nice labels for plots
term_labels <- c(
  "alpha_gal" = "Alpha-gal",
  "alpha-gal_syndrome" = "Alpha-gal syndrome",
  "food_allergy" = "Food allergy",
  "mammalian_meat_allergy" = "Mammalian meat allergy",
  "paralysis_tick" = "Paralysis tick",
  "red_meat_allergy" = "Red meat allergy",
  "meat_allergy" = "Meat allergy",
  "tick_allergy" = "Tick allergy"
)

# Download dates
download_dates <- sprintf("2026-02-%02d", 13:28)
```

# 1. Data Loading and Averaging

## 1.1 Load Google Trends Data

We collected Google Trends RSV data for 8 search terms across 16
consecutive days (Feb 13–28, 2026), following the multi-day sampling
protocol recommended by Romeiser et al. (2024) and Holzl et al. (2024)
to account for Google Trends’ stochastic sampling variability.

``` r
# Load all daily downloads for all search terms
all_downloads <- list()

for (date_str in download_dates) {
  for (term in search_terms) {
    file_path <- file.path(
      data_dir,
      paste0("google_trends_monthly_au_", term, "_", date_str, ".csv")
    )

    if (file.exists(file_path)) {
      df <- read_csv(file_path, show_col_types = FALSE)
      colnames(df)[2] <- "rsv"

      # Parse date column
      if (is.character(df$date)) {
        if (grepl("^\\d{1,2}/\\d{1,2}/\\d{4}$", df$date[1])) {
          df$date <- as.Date(df$date, format = "%d/%m/%Y")
        } else {
          df$date <- as.Date(df$date)
        }
      }

      df$search_term <- term
      df$download_date <- date_str
      all_downloads[[paste(term, date_str)]] <- df
    }
  }
}

trends_raw <- bind_rows(all_downloads)

cat("Loaded", n_distinct(trends_raw$download_date), "daily downloads for",
    n_distinct(trends_raw$search_term), "search terms\n")
cat("Date range:", as.character(min(trends_raw$date)), "to",
    as.character(max(trends_raw$date)), "\n")
cat("Total observations:", nrow(trends_raw), "\n")
```

    Loaded 16 daily downloads for 8 search terms
    Date range: 2014-02-01 to 2026-02-01 
    Total observations: 18560 

## 1.2 Average Across Downloads and Assess Sampling Variability

``` r
# Average RSV across all 16 downloads per term per month
trends_avg <- trends_raw |>
  group_by(date, search_term) |>
  summarise(
    mean_rsv = mean(rsv, na.rm = TRUE),
    sd_rsv = sd(rsv, na.rm = TRUE),
    cv_rsv = ifelse(mean_rsv > 0, sd_rsv / mean_rsv * 100, NA),
    se_rsv = sd_rsv / sqrt(n()),
    lower_ci = mean_rsv - 1.96 * se_rsv,
    upper_ci = mean_rsv + 1.96 * se_rsv,
    n_downloads = n(),
    .groups = "drop"
  ) |>
  mutate(
    lower_ci = pmax(lower_ci, 0),
    search_term_label = term_labels[search_term]
  )

# Sampling variability summary
cv_summary <- trends_avg |>
  filter(mean_rsv > 0) |>
  group_by(search_term) |>
  summarise(
    median_cv = median(cv_rsv, na.rm = TRUE),
    mean_cv = mean(cv_rsv, na.rm = TRUE),
    max_cv = max(cv_rsv, na.rm = TRUE),
    .groups = "drop"
  ) |>
  arrange(median_cv)

cat("Sampling variability (CV%) across 16 downloads:\n")
print(cv_summary, n = Inf)

# Flag terms with high sampling variability
unreliable_terms <- cv_summary |>
  filter(median_cv > 100) |>
  pull(search_term)

reliable_terms <- setdiff(search_terms, unreliable_terms)

cat("\nTerms with median CV > 100% (unreliable month-to-month precision):\n")
cat(" ", paste(term_labels[unreliable_terms], collapse = ", "), "\n")
cat("These terms have low absolute search volume, causing Google Trends'",
    "stochastic sampling\nto produce highly variable RSV estimates.",
    "Results for these terms should be interpreted cautiously.\n")
```

    Sampling variability (CV%) across 16 downloads:
    # A tibble: 8 × 4
      search_term            median_cv mean_cv max_cv
      <chr>                      <dbl>   <dbl>  <dbl>
    1 food_allergy                1.52    1.55   3.29
    2 paralysis_tick              3.09    3.32  12.5 
    3 meat_allergy               15.5    32.4  400   
    4 tick_allergy               54.5   108.   400   
    5 alpha_gal                  55.2   148.   400   
    6 mammalian_meat_allergy    180.    210.   400   
    7 red_meat_allergy          278.    285.   400   
    8 alpha-gal_syndrome        400     301.   400   

    Terms with median CV > 100% (unreliable month-to-month precision):
      Mammalian meat allergy, Red meat allergy, Alpha-gal syndrome 
    These terms have low absolute search volume, causing Google Trends' stochastic sampling
    to produce highly variable RSV estimates. Results for these terms should be interpreted cautiously.

## 1.3 Load MediaCloud Data

``` r
# Daily media article counts
media_counts <- read_csv(
  file.path(media_dir, "mc-onlinenews-mediacloud-20260213000613-counts.csv"),
  show_col_types = FALSE
) |>
  mutate(date = as.Date(date))

# Aggregate to monthly
media_monthly <- media_counts |>
  mutate(month_date = floor_date(date, "month")) |>
  group_by(month_date) |>
  summarise(
    articles = sum(count),
    total_articles = sum(total_count),
    .groups = "drop"
  ) |>
  rename(date = month_date)

# Media content (individual articles)
media_content <- read_csv(
  file.path(media_dir, "mc-onlinenews-mediacloud-20260213000622-content.csv"),
  show_col_types = FALSE
) |>
  mutate(publish_date = as.Date(publish_date))

# Top sources
media_sources <- read_csv(
  file.path(media_dir, "mc-onlinenews-mediacloud-20260213000707-top-sources.csv"),
  show_col_types = FALSE
)

cat("Media data: ", nrow(media_counts), " daily records,",
    sum(media_counts$count), "total articles\n")
cat("Date range:", as.character(min(media_counts$date)), "to",
    as.character(max(media_counts$date)), "\n")
cat("Individual articles in content data:", nrow(media_content), "\n")
```

    Media data:  4384  daily records, 95 total articles
    Date range: 2014-02-01 to 2026-02-01 
    Individual articles in content data: 95 

# 2. Descriptive Trends in Search Interest

## 2.1 Time Series of All Search Terms

``` r
ggplot(trends_avg, aes(x = date, y = mean_rsv)) +
  geom_ribbon(aes(ymin = lower_ci, ymax = upper_ci),
              fill = "#2c7fb8", alpha = 0.2) +
  geom_line(colour = "#2c7fb8", linewidth = 0.6) +
  facet_wrap(~ search_term_label, scales = "free_y", ncol = 2) +
  labs(
    title = "Google Trends Search Interest for AGS/MMA-Related Terms in Australia",
    subtitle = paste0("Monthly RSV averaged across ", max(trends_avg$n_downloads),
                      " daily downloads (Feb 13-28, 2026)"),
    x = NULL, y = "Mean Relative Search Volume (RSV)",
    caption = "Ribbon = 95% CI | Source: Google Trends (Health category, Australia)"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    strip.text = element_text(face = "bold", size = 10),
    panel.grid.minor = element_blank(),
    panel.spacing = unit(1, "lines"),
    plot.title = element_text(face = "bold", size = 14),
    plot.subtitle = element_text(colour = "grey40"),
    plot.caption = element_text(hjust = 0, face = "italic", size = 8)
  ) +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y")

ggsave(file.path(fig_dir, "fig1_trends_faceted.png"),
       width = 30, height = 22, units = "cm", dpi = 300)
```

<div id="fig-trends-faceted">

![](ags_awareness_analysis_files/figure-commonmark/fig-trends-faceted-1.png)

Figure 1: Average Google Trends RSV (0-100) for AGS/MMA-related search
terms in Australia, 2014-2026. Ribbons show 95% confidence intervals
from 16 daily data downloads.

</div>

## 2.2 AGS-Specific Terms Combined

``` r
ags_terms <- c("alpha_gal", "alpha-gal_syndrome", "mammalian_meat_allergy",
               "red_meat_allergy", "meat_allergy")

trends_avg |>
  filter(search_term %in% ags_terms) |>
  ggplot(aes(x = date, y = mean_rsv, colour = search_term_label)) +
  geom_line(linewidth = 0.7) +
  labs(
    title = "AGS/MMA-Specific Search Terms in Australia",
    x = NULL, y = "Mean RSV", colour = "Search Term"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    legend.position = "bottom",
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  ) +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y") +
  scale_colour_brewer(palette = "Set1")

ggsave(file.path(fig_dir, "fig2_ags_terms_comparison.png"),
       width = 25, height = 15, units = "cm", dpi = 300)
```

<div id="fig-ags-terms">

![](ags_awareness_analysis_files/figure-commonmark/fig-ags-terms-1.png)

Figure 2: Comparison of AGS-specific search terms showing the dual
Australian/international terminology landscape.

</div>

## 2.3 Summary Statistics per Term

``` r
term_summary <- trends_avg |>
  group_by(search_term_label) |>
  summarise(
    first_nonzero = min(date[mean_rsv > 0], na.rm = TRUE),
    peak_month = date[which.max(mean_rsv)],
    peak_rsv = max(mean_rsv, na.rm = TRUE),
    mean_rsv_overall = round(mean(mean_rsv, na.rm = TRUE), 1),
    pct_months_nonzero = round(sum(mean_rsv > 0) / n() * 100, 1),
    .groups = "drop"
  ) |>
  arrange(first_nonzero)

knitr::kable(term_summary, col.names = c(
  "Search Term", "First Non-Zero Month", "Peak Month", "Peak RSV",
  "Mean RSV", "% Months Non-Zero"
), caption = "Summary of search interest by term")
```

| Search Term | First Non-Zero Month | Peak Month | Peak RSV | Mean RSV | % Months Non-Zero |
|:---|:---|:---|---:|---:|---:|
| Alpha-gal | 2014-02-01 | 2025-11-01 | 99.7500 | 12.5 | 64.1 |
| Food allergy | 2014-02-01 | 2023-11-01 | 100.0000 | 60.6 | 100.0 |
| Meat allergy | 2014-02-01 | 2025-11-01 | 95.2500 | 30.1 | 99.3 |
| Paralysis tick | 2014-02-01 | 2018-10-01 | 100.0000 | 41.5 | 100.0 |
| Tick allergy | 2014-02-01 | 2023-08-01 | 93.4375 | 24.2 | 92.4 |
| Red meat allergy | 2014-04-01 | 2015-02-01 | 91.8125 | 6.1 | 51.7 |
| Mammalian meat allergy | 2015-02-01 | 2015-02-01 | 96.6250 | 10.2 | 66.9 |
| Alpha-gal syndrome | 2015-05-01 | 2025-11-01 | 93.6250 | 1.3 | 7.6 |

Summary of search interest by term

## 2.4 Heatmap of Annual Search Interest

``` r
trends_avg |>
  mutate(year = year(date)) |>
  group_by(year, search_term_label) |>
  summarise(annual_mean = mean(mean_rsv, na.rm = TRUE), .groups = "drop") |>
  ggplot(aes(x = year, y = search_term_label, fill = annual_mean)) +
  geom_tile(colour = "white", linewidth = 0.5) +
  scale_fill_viridis_c(option = "inferno", name = "Mean RSV") +
  labs(title = "Annual Search Interest Heatmap", x = "Year", y = NULL) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold"),
    panel.grid = element_blank()
  )

ggsave(file.path(fig_dir, "fig3_heatmap.png"),
       width = 25, height = 12, units = "cm", dpi = 300)
```

<div id="fig-heatmap">

![](ags_awareness_analysis_files/figure-commonmark/fig-heatmap-1.png)

Figure 3: Annual mean RSV by search term, showing the evolution of AGS
awareness over time.

</div>

# 3. Media Coverage Analysis

## 3.1 Monthly Media Coverage Timeline

``` r
# Combine media monthly with alpha_gal search
alpha_gal_monthly <- trends_avg |>
  filter(search_term == "alpha_gal") |>
  dplyr::select(date, mean_rsv)

media_search_combined <- media_monthly |>
  left_join(alpha_gal_monthly, by = "date")

# Faceted panel (avoids dual y-axis interpretability issues)
p_media <- ggplot(media_search_combined, aes(x = date)) +
  geom_col(aes(y = articles), fill = "#d95f02", alpha = 0.7, width = 25) +
  labs(y = "Media Articles", x = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank()) +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y")

p_search <- ggplot(media_search_combined, aes(x = date)) +
  geom_line(aes(y = mean_rsv), colour = "#2c7fb8", linewidth = 0.8) +
  labs(y = "Alpha-gal RSV", x = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank()) +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y")

p_media / p_search +
  plot_annotation(
    title = "Media Coverage vs. Google Search Interest for Alpha-Gal in Australia",
    subtitle = "Top = media article count | Bottom = Google Trends RSV",
    theme = theme(
      plot.title = element_text(face = "bold", size = 14),
      plot.subtitle = element_text(colour = "grey40")
    )
  )

ggsave(file.path(fig_dir, "fig4_media_vs_search.png"),
       width = 28, height = 18, units = "cm", dpi = 300)
```

<div id="fig-media-timeline">

![](ags_awareness_analysis_files/figure-commonmark/fig-media-timeline-1.png)

Figure 4: Monthly media article counts (top) and alpha-gal search
interest (bottom), showing temporal relationship between media coverage
and public awareness.

</div>

## 3.2 Key Media Events

``` r
# Filter off-topic articles (xenotransplantation, Lyme disease treatment, French-language)
offtopic_patterns <- regex(
  "pig.*(kidney|transplant)|kidney.*pig|xenotransplant|lyme disease treatment|cypru|les tiques se r|animaux venimeux",
  ignore_case = TRUE
)

media_content_filtered <- media_content |>
  filter(!str_detect(title, offtopic_patterns))

n_excluded <- nrow(media_content) - nrow(media_content_filtered)
cat("Excluded", n_excluded, "off-topic articles (xenotransplantation, Lyme disease",
    "treatment, French-language)\n")
cat("Remaining AGS/MMA-relevant articles:", nrow(media_content_filtered), "\n")

# Rebuild monthly aggregation from filtered content
media_monthly_filtered <- media_content_filtered |>
  mutate(month_date = floor_date(publish_date, "month")) |>
  count(month_date, name = "articles") |>
  rename(date = month_date)

# Use filtered data for all downstream analyses
media_monthly <- media_monthly |>
  dplyr::select(date, total_articles) |>
  left_join(media_monthly_filtered, by = "date") |>
  mutate(articles = replace_na(articles, 0))

# Build media event timeline from filtered content data
media_events <- media_content_filtered |>
  dplyr::select(publish_date, title, media_name) |>
  arrange(publish_date) |>
  distinct(title, .keep_all = TRUE)

knitr::kable(
  media_events |> dplyr::select(publish_date, media_name, title),
  col.names = c("Date", "Source", "Title"),
  caption = "Timeline of Australian media articles on AGS/MMA (unique stories, off-topic excluded)"
)
```

    Excluded 17 off-topic articles (xenotransplantation, Lyme disease treatment, French-language)
    Remaining AGS/MMA-relevant articles: 78 

| Date | Source | Title |
|:---|:---|:---|
| 2014-08-12 | smh.com.au | This insect’s bite could turn you into a vegetarian |
| 2015-10-01 | news.com.au | Humans of the future: Short, allergic to meat and with night vision |
| 2015-10-10 | theage.com.au | One bite could be fatal: woman lucky to be alive after tick bite |
| 2016-06-14 | news.com.au | Thousands of Australians, especially on Sydney’s northern beaches, have suddenly become deathly allergic to red meat |
| 2016-09-14 | sbs.com.au | Epidemic of tick-induced meat allergy in Sydney’s Northern Beaches |
| 2016-10-25 | smh.com.au | East coast meat allergy phenomenon linked to tick bites |
| 2018-06-23 | thewest.com.au | Tick bites spark lethal allergy to red meat |
| 2018-06-26 | businessinsider.com.au | The tick bites that make people allergic to red meat and dairy may also increase heart disease risk |
| 2018-07-10 | echo.net.au | Blood-sucking freaks – Echonetdaily |
| 2018-07-16 | businessinsider.com.au | Diseases spread by ticks are on the rise — here’s what you are at risk for throughout the US |
| 2018-08-15 | news.com.au | There’s something strange that happens from this one scary bite |
| 2018-08-28 | camdencourier.com.au | Health warning on the impact of biting critters |
| 2018-08-31 | wauchopegazette.com.au | Wauchope news |
| 2018-09-01 | portnews.com.au | Port Macquarie News |
| 2018-09-01 | manningrivertimes.com.au | Taree news |
| 2018-09-01 | winghamchronicle.com.au | Tick risks and impacts on human health |
| 2018-09-02 | gloucesteradvocate.com.au | Gloucester News |
| 2018-09-04 | naroomanewsonline.com.au | Narooma news |
| 2018-09-04 | illawarramercury.com.au | South Coast woman traces long list of health issues back to tick bite |
| 2018-09-04 | ulladullatimes.com.au | Ulladulla news |
| 2018-09-04 | kiamaindependent.com.au | Kiama Independent-Lake Times |
| 2018-09-04 | southcoastregister.com.au | Ticks are just nasty little suckers |
| 2019-01-18 | abc.net.au | How tick bites can make some people allergic to meat and milk |
| 2019-06-05 | businessinsider.com.au | A mother is warning others about life-threatening tick bites after her 2-year-old was hospitalized: ‘He wailed because it hurt so badly to be touched’ |
| 2019-07-12 | theconversation.com | Ticks spread plenty more for you to worry about beyond Lyme disease |
| 2019-08-14 | echo.net.au | Ticking the boxes for Ixodes holocyclus – Echonetdaily |
| 2019-08-25 | thenewdaily.com.au | Mysterious new meat allergy has scientists stumped |
| 2020-01-01 | abc.net.au | I’ve been bitten by a tick. What next? |
| 2020-01-02 | thenewdaily.com.au | Tick bites can make you sick – so what is the best way to deal with them? |
| 2020-11-18 | dailymercury.com.au | Hot weather and outdoors bring uptick in tick bites |
| 2020-12-26 | abc.net.au | After I was bitten by tick, I developed a rare allergy to meat. Now I’m a quasi-vegetarian |
| 2021-11-19 | theconversation.com | Tick management programs could help stop Lyme disease, but US funding is inadequate |
| 2022-09-26 | townsvillebulletin.com.au | CEO’s daughter takes own life after diagnosis |
| 2022-11-06 | jimboombatimes.com.au | Severe human tick bite reactions cause for concern |
| 2022-12-30 | abc.net.au | Fresh warnings over summer as tick numbers surge, raising risk of deadly meat allergy |
| 2023-06-14 | perthnow.com.au | Why have I developed a pork intolerance late in life? |
| 2023-07-28 | 9news.com.au | Meat allergy caused by a bug ‘getting more common’ |
| 2023-08-05 | sbs.com.au | Tick bites can bring on a potentially deadly meat allergy. Here’s how to protect yourself |
| 2023-08-06 | perthnow.com.au | Tick bite leaves man with DEADLY allergy to smelling meat |
| 2023-08-08 | abc.net.au | What is Lyme disease, the condition supermodel Bella Hadid talked about on social media? |
| 2023-08-21 | theconversation.com | Ticks are becoming a growing health risk in the UK – here’s why |
| 2023-08-25 | abc.net.au | Ticks are thriving after three wet summers and that could lead to more meat allergy cases |
| 2023-08-25 | townsvillebulletin.com.au | Bizarre reason more Aussies are becoming allergic to red meat |
| 2023-08-27 | cairnspost.com.au | Aussies warned of tick bite danger after 450,000 red meat allergy cases emerge in US |
| 2024-05-07 | theconversation.com | Yes, adults can develop food allergies. Here are 4 types you need to know about |
| 2025-05-24 | smh.com.au | ‘It triggers an explosion’: What causes allergies and can they be prevented? |
| 2025-08-05 | theconversation.com | A red meat allergy from tick bites is spreading – and the lone star tick isn’t the only alpha-gal carrier to worry about |
| 2025-08-14 | theland.com.au | Vaccinated to be allergic to meat: when those who preach morals, are immoral |
| 2025-09-29 | theconversation.com | From pea protein to buckwheat: surprising foods that can trigger severe allergic reactions |
| 2025-11-01 | abc.net.au | Tick-bite illnesses can be complex and debilitating. Are we any closer to understanding them? |
| 2025-11-13 | northqueenslandregister.com.au | Allergic to meat: a life-altering syndrome caused by a tick bite is spreading |
| 2025-11-14 | 9news.com.au | ‘Unmitigated tragedy’: US pilot dies from eating hamburger after tick bite |
| 2025-11-17 | thewest.com.au | Teen’s potentially deadly final meal on camping trip |
| 2025-11-19 | 9news.com.au | Little-known allergy probed over death of teen hours after sausage dinner |
| 2025-11-19 | thewest.com.au | Spotlight on teen’s legacy after camping trip death |
| 2025-11-27 | abc.net.au | NSW deputy coroner to decide if teen’s death was caused by meat allergy from tick bites |
| 2026-01-12 | singletonargus.com.au | From bush to harvest: how a life-altering tick bite planted the seeds for Rainbird Farm |

Timeline of Australian media articles on AGS/MMA (unique stories,
off-topic excluded)

## 3.3 Media Coverage by Year

``` r
media_content_filtered |>
  mutate(year = year(publish_date)) |>
  count(year) |>
  ggplot(aes(x = year, y = n)) +
  geom_col(fill = "#d95f02", alpha = 0.8) +
  labs(
    title = "Number of Australian Media Articles on AGS/MMA by Year",
    x = "Year", y = "Article Count"
  ) +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(face = "bold"))

ggsave(file.path(fig_dir, "fig5_media_articles_by_year.png"),
       width = 20, height = 12, units = "cm", dpi = 300)
```

<div id="fig-media-by-year">

<img
src="ags_awareness_analysis_files/figure-commonmark/fig-media-by-year-1.png"
id="fig-media-by-year" />

Figure 5

</div>

## 3.4 Top Media Sources

``` r
knitr::kable(
  media_sources |> head(15),
  col.names = c("Source", "Article Count", "Proportion"),
  caption = "Top 15 media sources covering AGS/MMA in Australia",
  digits = 3
)
```

| Source                    | Article Count | Proportion |
|:--------------------------|--------------:|-----------:|
| abc.net.au                |             9 |      0.095 |
| theconversation.com       |             8 |      0.084 |
| brisbanetimes.com.au      |             5 |      0.053 |
| perthnow.com.au           |             5 |      0.053 |
| smh.com.au                |             5 |      0.053 |
| theage.com.au             |             5 |      0.053 |
| businessinsider.com.au    |             4 |      0.042 |
| cairnspost.com.au         |             4 |      0.042 |
| thewest.com.au            |             4 |      0.042 |
| townsvillebulletin.com.au |             4 |      0.042 |
| 9news.com.au              |             3 |      0.032 |
| geelongadvertiser.com.au  |             3 |      0.032 |
| news.com.au               |             3 |      0.032 |
| sbs.com.au                |             3 |      0.032 |
| echo.net.au               |             2 |      0.021 |

Top 15 media sources covering AGS/MMA in Australia

# 4. Seasonality Analysis

## 4.1 Monthly Seasonal Patterns

``` r
tick_terms <- c("paralysis_tick", "tick_allergy", "alpha_gal", "mammalian_meat_allergy")

seasonal_data <- trends_avg |>
  filter(search_term %in% tick_terms) |>
  mutate(
    month = month(date, label = TRUE),
    month_num = month(date),
    year = year(date),
    warm_season = ifelse(month_num %in% c(10, 11, 12, 1, 2, 3), "Tick season\n(Oct-Mar)", "Cool season\n(Apr-Sep)")
  )

ggplot(seasonal_data, aes(x = month, y = mean_rsv)) +
  geom_boxplot(aes(fill = warm_season), outlier.size = 1) +
  facet_wrap(~ search_term_label, scales = "free_y", ncol = 2) +
  scale_fill_manual(values = c("Tick season\n(Oct-Mar)" = "#fc8d59",
                                "Cool season\n(Apr-Sep)" = "#91bfdb"),
                    name = "Season") +
  labs(
    title = "Seasonal Distribution of Search Interest",
    subtitle = "Southern Hemisphere tick season: October-March (I. holocyclus activity peak)",
    x = "Month", y = "RSV"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    strip.text = element_text(face = "bold"),
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(colour = "grey40"),
    panel.grid.minor = element_blank(),
    legend.position = "bottom"
  )

ggsave(file.path(fig_dir, "fig6_seasonality.png"),
       width = 28, height = 20, units = "cm", dpi = 300)
```

<div id="fig-seasonality">

![](ags_awareness_analysis_files/figure-commonmark/fig-seasonality-1.png)

Figure 6: Seasonal patterns by month for tick-related and AGS-specific
search terms. Tick season (Oct-Mar, shaded) corresponds to the I.
holocyclus activity period.

</div>

## 4.2 Kruskal-Wallis Test for Seasonality

The raw Kruskal-Wallis test can be confounded by secular trends (e.g.,
months in later years having higher RSV simply because the trend is
upward). We therefore also test seasonality after detrending via STL
decomposition.

``` r
# Raw KW test (may be confounded by trend)
seasonality_raw <- trends_avg |>
  filter(search_term %in% tick_terms) |>
  mutate(month_num = month(date)) |>
  group_by(search_term) |>
  summarise(
    kw_statistic = kruskal.test(mean_rsv ~ factor(month_num))$statistic,
    kw_p_value = kruskal.test(mean_rsv ~ factor(month_num))$p.value,
    .groups = "drop"
  )

# Detrended KW test using STL decomposition
seasonality_detrended <- map_dfr(tick_terms, function(term) {
  term_data <- trends_avg |>
    filter(search_term == term) |>
    arrange(date)

  # Create ts object (monthly, starting from first observation)
  start_year <- year(min(term_data$date))
  start_month <- month(min(term_data$date))
  ts_obj <- ts(term_data$mean_rsv, start = c(start_year, start_month), frequency = 12)

  # STL decomposition to remove trend
  stl_fit <- stl(ts_obj, s.window = "periodic", robust = TRUE)
  detrended <- stl_fit$time.series[, "seasonal"] + stl_fit$time.series[, "remainder"]

  # KW test on detrended values
  month_num <- month(term_data$date)
  kw <- kruskal.test(detrended ~ factor(month_num))

  tibble(
    search_term = term,
    kw_detrended_stat = kw$statistic,
    kw_detrended_p = kw$p.value
  )
})

# Combine raw and detrended results
seasonality_results <- seasonality_raw |>
  left_join(seasonality_detrended, by = "search_term") |>
  mutate(
    sig_raw = ifelse(kw_p_value < 0.05, "Yes", "No"),
    sig_detrended = ifelse(kw_detrended_p < 0.05, "Yes", "No"),
    search_term = term_labels[search_term]
  )

knitr::kable(
  seasonality_results |>
    dplyr::select(search_term, kw_statistic, kw_p_value, sig_raw,
                  kw_detrended_stat, kw_detrended_p, sig_detrended),
  col.names = c("Search Term", "KW Stat (raw)", "p (raw)", "Sig.",
                 "KW Stat (detrended)", "p (detrended)", "Sig."),
  digits = c(0, 2, 4, 0, 2, 4, 0),
  caption = "Kruskal-Wallis test for seasonality: raw vs. STL-detrended RSV"
)
```

| Search Term | KW Stat (raw) | p (raw) | Sig. | KW Stat (detrended) | p (detrended) | Sig. |
|:---|---:|---:|:---|---:|---:|:---|
| Alpha-gal | 3.50 | 0.9823 | No | 25.92 | 0.0067 | Yes |
| Mammalian meat allergy | 11.08 | 0.4367 | No | 14.84 | 0.1898 | No |
| Paralysis tick | 124.12 | 0.0000 | Yes | 131.13 | 0.0000 | Yes |
| Tick allergy | 29.36 | 0.0020 | Yes | 48.11 | 0.0000 | Yes |

Kruskal-Wallis test for seasonality: raw vs. STL-detrended RSV

## 4.3 Warm vs Cool Season Comparison

``` r
# Wilcoxon rank-sum test for each term
season_test_data <- trends_avg |>
  mutate(
    month_num = month(date),
    warm_season = month_num %in% c(10, 11, 12, 1, 2, 3)
  )

wilcox_results <- season_test_data |>
  group_by(search_term) |>
  summarise(
    wilcox_p = wilcox.test(mean_rsv[warm_season], mean_rsv[!warm_season])$p.value,
    .groups = "drop"
  )

season_comparison <- season_test_data |>
  group_by(search_term, warm_season) |>
  summarise(
    mean = mean(mean_rsv, na.rm = TRUE),
    median = median(mean_rsv, na.rm = TRUE),
    .groups = "drop"
  ) |>
  pivot_wider(
    names_from = warm_season,
    values_from = c(mean, median),
    names_glue = "{.value}_{ifelse(warm_season, 'warm', 'cool')}"
  ) |>
  left_join(wilcox_results, by = "search_term") |>
  mutate(
    warm_cool_ratio = mean_warm / pmax(mean_cool, 0.1),
    search_term = term_labels[search_term]
  ) |>
  arrange(desc(warm_cool_ratio))

knitr::kable(
  season_comparison |>
    dplyr::select(search_term, mean_warm, mean_cool, warm_cool_ratio, wilcox_p),
  col.names = c("Search Term", "Mean RSV (Warm)", "Mean RSV (Cool)",
                 "Warm/Cool Ratio", "Wilcoxon p"),
  digits = c(0, 2, 2, 2, 4),
  caption = "Warm season (Oct-Mar) vs cool season (Apr-Sep) mean RSV with Wilcoxon rank-sum test"
)
```

| Search Term | Mean RSV (Warm) | Mean RSV (Cool) | Warm/Cool Ratio | Wilcoxon p |
|:---|---:|---:|---:|---:|
| Alpha-gal syndrome | 1.99 | 0.51 | 3.86 | 0.8261 |
| Red meat allergy | 8.30 | 3.95 | 2.10 | 0.3872 |
| Mammalian meat allergy | 12.28 | 8.07 | 1.52 | 0.3680 |
| Paralysis tick | 46.91 | 36.01 | 1.30 | 0.0135 |
| Tick allergy | 26.93 | 21.41 | 1.26 | 0.0600 |
| Alpha-gal | 13.63 | 11.35 | 1.20 | 0.6213 |
| Meat allergy | 32.15 | 28.03 | 1.15 | 0.1706 |
| Food allergy | 59.60 | 61.61 | 0.97 | 0.0386 |

Warm season (Oct-Mar) vs cool season (Apr-Sep) mean RSV with Wilcoxon
rank-sum test

# 5. Trend Quantification

## 5.1 Quasi-Poisson GAM with Penalised Splines

``` r
# Fit GAM models for each search term
gam_results <- list()

for (term in search_terms) {
  term_data <- trends_avg |>
    filter(search_term == term) |>
    mutate(
      time_numeric = as.numeric(date) / 365.25,  # years
      month_num = month(date),
      warm_season = as.integer(month_num %in% c(10, 11, 12, 1, 2, 3)),
      # Add 1 to RSV for quasi-Poisson (avoid log(0))
      rsv_count = round(mean_rsv) + 1
    )

  # Only fit if there's enough non-zero data
  if (sum(term_data$mean_rsv > 0) > 12) {
    gam_fit <- gam(
      rsv_count ~ s(time_numeric, bs = "cr", k = 15) + warm_season,
      family = quasipoisson(),
      data = term_data
    )

    gam_results[[term]] <- list(
      model = gam_fit,
      data = term_data,
      dispersion = summary(gam_fit)$dispersion,
      r_sq = summary(gam_fit)$r.sq,
      warm_effect = coef(gam_fit)["warm_season"],
      warm_p = summary(gam_fit)$p.table["warm_season", "Pr(>|t|)"]
    )
  }
}

# Summary table
gam_summary <- map_dfr(names(gam_results), function(term) {
  r <- gam_results[[term]]
  tibble(
    search_term = term_labels[term],
    r_squared = round(r$r_sq, 3),
    dispersion = round(r$dispersion, 2),
    warm_season_coef = round(r$warm_effect, 3),
    warm_season_irr = round(exp(r$warm_effect), 2),
    warm_season_p = round(r$warm_p, 4)
  )
})

knitr::kable(gam_summary,
             col.names = c("Term", "R-sq", "Dispersion", "Warm Season Coef",
                           "Warm Season IRR", "p-value"),
             caption = "Quasi-Poisson GAM results: trend + warm season effect")

# GAM diagnostics: basis dimension adequacy
cat("\nBasis dimension check (k-index < 1 suggests k may be too low):\n")
gam_diagnostics <- map_dfr(names(gam_results), function(term) {
  r <- gam_results[[term]]
  k_check <- k.check(r$model)
  tibble(
    search_term = term_labels[term],
    k_index = round(k_check[1, "k-index"], 3),
    k_pvalue = round(k_check[1, "p-value"], 4),
    r_sq = round(r$r_sq, 3),
    dispersion = round(r$dispersion, 2),
    fit_quality = case_when(
      r$r_sq < 0.1 ~ "Poor (R-sq < 0.1)",
      r$dispersion > 10 ~ "High overdispersion (>10)",
      TRUE ~ "Adequate"
    )
  )
})

knitr::kable(gam_diagnostics,
             col.names = c("Term", "k-index", "k p-value", "R-sq",
                           "Dispersion", "Fit Quality"),
             caption = "GAM model diagnostics")

cat("\nNote: Models with high overdispersion (>10) may benefit from negative binomial",
    "family.\nModels with R-sq < 0.1 explain negligible variance in the outcome.\n")
```

| Term | R-sq | Dispersion | Warm Season Coef | Warm Season IRR | p-value |
|:---|---:|---:|---:|---:|---:|
| Alpha-gal | 0.868 | 2.75 | 0.003 | 1.00 | 0.9651 |
| Food allergy | 0.748 | 0.64 | -0.039 | 0.96 | 0.0244 |
| Mammalian meat allergy | 0.265 | 4.76 | 0.268 | 1.31 | 0.0264 |
| Paralysis tick | 0.073 | 9.24 | 0.257 | 1.29 | 0.0013 |
| Red meat allergy | 0.234 | 11.22 | 0.501 | 1.65 | 0.0293 |
| Meat allergy | 0.415 | 4.62 | 0.092 | 1.10 | 0.1631 |
| Tick allergy | 0.258 | 11.87 | 0.186 | 1.20 | 0.1102 |

Quasi-Poisson GAM results: trend + warm season effect


    Basis dimension check (k-index < 1 suggests k may be too low):

| Term | k-index | k p-value | R-sq | Dispersion | Fit Quality |
|:---|---:|---:|---:|---:|:---|
| Alpha-gal | 0.898 | 0.1075 | 0.868 | 2.75 | Adequate |
| Food allergy | 0.836 | 0.0300 | 0.748 | 0.64 | Adequate |
| Mammalian meat allergy | 0.929 | 0.2225 | 0.265 | 4.76 | Adequate |
| Paralysis tick | 0.237 | 0.0000 | 0.073 | 9.24 | Poor (R-sq \< 0.1) |
| Red meat allergy | 1.005 | 0.5875 | 0.234 | 11.22 | High overdispersion (\>10) |
| Meat allergy | 0.970 | 0.3375 | 0.415 | 4.62 | Adequate |
| Tick allergy | 0.773 | 0.0025 | 0.258 | 11.87 | High overdispersion (\>10) |

GAM model diagnostics


    Note: Models with high overdispersion (>10) may benefit from negative binomial family.
    Models with R-sq < 0.1 explain negligible variance in the outcome.

## 5.2 GAM Trend Visualisation

``` r
gam_plots <- map(names(gam_results), function(term) {
  r <- gam_results[[term]]
  pred_data <- r$data |>
    mutate(fitted = predict(r$model, type = "response") - 1)

  ggplot(pred_data, aes(x = date)) +
    geom_line(aes(y = mean_rsv), colour = "#2c7fb8", alpha = 0.5) +
    geom_line(aes(y = fitted), colour = "#e41a1c", linewidth = 0.8) +
    labs(title = term_labels[term], x = NULL, y = "RSV") +
    theme_minimal(base_size = 9) +
    theme(plot.title = element_text(face = "bold", size = 10))
})

wrap_plots(gam_plots, ncol = 2) +
  plot_annotation(
    title = "Quasi-Poisson GAM Trend Fits",
    subtitle = "Blue = observed mean RSV | Red = GAM fitted trend",
    theme = theme(
      plot.title = element_text(face = "bold", size = 14),
      plot.subtitle = element_text(colour = "grey40")
    )
  )

ggsave(file.path(fig_dir, "fig7_gam_trends.png"),
       width = 30, height = 22, units = "cm", dpi = 300)
```

<div id="fig-gam-trends">

![](ags_awareness_analysis_files/figure-commonmark/fig-gam-trends-1.png)

Figure 7: Quasi-Poisson GAM fitted trends (red) with observed data
(blue) for each search term.

</div>

## 5.3 Segmented Regression (Joinpoint Analysis)

``` r
# Aggregate to annual for joinpoint analysis
annual_trends <- trends_avg |>
  mutate(year = year(date)) |>
  group_by(year, search_term) |>
  summarise(annual_mean = mean(mean_rsv, na.rm = TRUE), .groups = "drop")

segmented_results <- list()

for (term in search_terms) {
  term_annual <- annual_trends |>
    filter(search_term == term, annual_mean > 0)

  if (nrow(term_annual) >= 5) {
    lm_fit <- lm(log(annual_mean + 0.1) ~ year, data = term_annual)

    tryCatch({
      seg_fit <- segmented(lm_fit, seg.Z = ~ year, npsi = 1)

      segmented_results[[term]] <- list(
        model = seg_fit,
        breakpoint = round(seg_fit$psi[, "Est."], 1),
        slopes = slope(seg_fit)$year
      )
    }, error = function(e) {
      # No significant joinpoint - use linear model
      segmented_results[[term]] <<- list(
        model = lm_fit,
        breakpoint = NA,
        slopes = data.frame(
          Est. = coef(lm_fit)["year"],
          `Std. Err.` = summary(lm_fit)$coefficients["year", "Std. Error"]
        )
      )
    })
  }
}

# AAPC calculation
aapc_results <- map_dfr(names(segmented_results), function(term) {
  r <- segmented_results[[term]]
  term_annual <- annual_trends |>
    filter(search_term == term, annual_mean > 0)

  if (inherits(r$model, "segmented")) {
    slopes_df <- slope(r$model)$year
    tibble(
      search_term = term_labels[term],
      breakpoint = r$breakpoint,
      slope_before = round((exp(slopes_df[1, "Est."]) - 1) * 100, 1),
      slope_after = round((exp(slopes_df[2, "Est."]) - 1) * 100, 1)
    )
  } else {
    overall_slope <- coef(r$model)["year"]
    tibble(
      search_term = term_labels[term],
      breakpoint = NA_real_,
      slope_before = round((exp(overall_slope) - 1) * 100, 1),
      slope_after = NA_real_
    )
  }
})

knitr::kable(aapc_results,
             col.names = c("Term", "Breakpoint Year", "APC Before (%)",
                           "APC After (%)"),
             caption = "Segmented regression: Annual Percent Change with joinpoint detection")

cat("\nCaveats:\n")
cat("- Segmented regression is fit to annual means (n =",
    n_distinct(annual_trends$year), "years), which limits statistical power.\n")
cat("- Very large APC values (e.g., >100%) for low-volume terms reflect small",
    "absolute changes\n  from near-zero baselines and should be interpreted",
    "as directional rather than precise estimates.\n")
cat("- Terms with median CV >100% (", paste(term_labels[unreliable_terms], collapse = ", "),
    ")\n  have unreliable annual means due to high sampling variability.\n")
```

| Term                   | Breakpoint Year | APC Before (%) | APC After (%) |
|:-----------------------|----------------:|---------------:|--------------:|
| Alpha-gal              |          2020.0 |           50.8 |          73.8 |
| Alpha-gal syndrome     |          2023.6 |           -7.7 |         266.3 |
| Food allergy           |          2020.0 |            2.4 |           6.2 |
| Mammalian meat allergy |          2020.1 |          -17.3 |          44.6 |
| Paralysis tick         |          2025.0 |           -1.3 |         -32.1 |
| Red meat allergy       |          2023.9 |            0.0 |         208.7 |
| Meat allergy           |          2015.1 |          166.8 |           4.5 |
| Tick allergy           |          2015.4 |           70.0 |           6.2 |

Segmented regression: Annual Percent Change with joinpoint detection


    Caveats:
    - Segmented regression is fit to annual means (n = 13 years), which limits statistical power.
    - Very large APC values (e.g., >100%) for low-volume terms reflect small absolute changes
      from near-zero baselines and should be interpreted as directional rather than precise estimates.
    - Terms with median CV >100% ( Mammalian meat allergy, Red meat allergy, Alpha-gal syndrome )
      have unreliable annual means due to high sampling variability.

## 5.4 Joinpoint Visualisation

``` r
key_terms <- c("alpha_gal", "mammalian_meat_allergy", "paralysis_tick", "meat_allergy")

annual_plot_data <- annual_trends |>
  filter(search_term %in% key_terms)

ggplot(annual_plot_data, aes(x = year, y = annual_mean)) +
  geom_point(size = 2, colour = "#2c7fb8") +
  geom_smooth(method = "lm", formula = y ~ x, se = TRUE,
              colour = "#e41a1c", fill = "#e41a1c", alpha = 0.15) +
  facet_wrap(~ term_labels[search_term], scales = "free_y", ncol = 2) +
  labs(
    title = "Annual Trends in Key Search Terms",
    x = "Year", y = "Annual Mean RSV"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    strip.text = element_text(face = "bold"),
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  )

ggsave(file.path(fig_dir, "fig8_annual_trends.png"),
       width = 25, height = 15, units = "cm", dpi = 300)
```

<div id="fig-joinpoint">

![](ags_awareness_analysis_files/figure-commonmark/fig-joinpoint-1.png)

Figure 8: Annual trends with segmented regression fits for key
AGS-related terms.

</div>

# 6. Media-Awareness Correlation Analysis

## 6.1 Spearman Correlations

``` r
# Merge media monthly with search trends
correlation_data <- trends_avg |>
  dplyr::select(date, search_term, mean_rsv) |>
  pivot_wider(names_from = search_term, values_from = mean_rsv) |>
  left_join(media_monthly |> dplyr::select(date, articles), by = "date")

# Spearman correlation for each term vs media articles
spearman_results <- map_dfr(search_terms, function(term) {
  x <- correlation_data[[term]]
  y <- correlation_data$articles

  # Remove months where both are zero
  valid <- !is.na(x) & !is.na(y)

  test <- cor.test(x[valid], y[valid], method = "spearman", exact = FALSE)

  tibble(
    search_term = term_labels[term],
    rho = round(test$estimate, 3),
    p_value = test$p.value,
    significant = ifelse(test$p.value < 0.05, "Yes", "No")
  )
}) |>
  # Benjamini-Hochberg correction
  mutate(p_adjusted = p.adjust(p_value, method = "BH")) |>
  arrange(desc(abs(rho)))

knitr::kable(spearman_results,
             col.names = c("Search Term", "Spearman rho", "p-value",
                           "Sig. (p<0.05)", "BH-adjusted p"),
             digits = c(0, 3, 4, 0, 4),
             caption = "Spearman correlations between monthly media article count and search RSV (raw levels)")
```

| Search Term            | Spearman rho | p-value | Sig. (p\<0.05) | BH-adjusted p |
|:-----------------------|-------------:|--------:|:---------------|--------------:|
| Meat allergy           |        0.296 |  0.0003 | Yes            |        0.0016 |
| Mammalian meat allergy |        0.290 |  0.0004 | Yes            |        0.0016 |
| Tick allergy           |        0.277 |  0.0007 | Yes            |        0.0019 |
| Paralysis tick         |        0.228 |  0.0059 | Yes            |        0.0118 |
| Red meat allergy       |        0.138 |  0.0974 | No             |        0.1362 |
| Alpha-gal              |        0.136 |  0.1021 | No             |        0.1362 |
| Alpha-gal syndrome     |        0.124 |  0.1369 | No             |        0.1565 |
| Food allergy           |       -0.029 |  0.7332 | No             |        0.7332 |

Spearman correlations between monthly media article count and search RSV
(raw levels)

The raw Spearman correlations above may be confounded by shared temporal
trends (both media coverage and search interest trend upward). We repeat
the analysis on first-differenced series to remove this confound:

``` r
# Spearman on first-differenced series (trend-adjusted)
spearman_diff_results <- map_dfr(search_terms, function(term) {
  x <- correlation_data[[term]]
  y <- correlation_data$articles

  valid <- !is.na(x) & !is.na(y)
  x_diff <- diff(x[valid])
  y_diff <- diff(y[valid])

  test <- cor.test(x_diff, y_diff, method = "spearman", exact = FALSE)

  tibble(
    search_term = term_labels[term],
    rho_diff = round(test$estimate, 3),
    p_value_diff = test$p.value,
    significant = ifelse(test$p.value < 0.05, "Yes", "No")
  )
}) |>
  mutate(p_adjusted_diff = p.adjust(p_value_diff, method = "BH")) |>
  arrange(desc(abs(rho_diff)))

knitr::kable(spearman_diff_results,
             col.names = c("Search Term", "Spearman rho (diff)", "p-value",
                           "Sig. (p<0.05)", "BH-adjusted p"),
             digits = c(0, 3, 4, 0, 4),
             caption = "Trend-adjusted Spearman correlations (first-differenced series)")
```

| Search Term | Spearman rho (diff) | p-value | Sig. (p\<0.05) | BH-adjusted p |
|:---|---:|---:|:---|---:|
| Meat allergy | 0.339 | 0.0000 | Yes | 0.0003 |
| Mammalian meat allergy | 0.284 | 0.0006 | Yes | 0.0023 |
| Tick allergy | 0.254 | 0.0022 | Yes | 0.0057 |
| Red meat allergy | 0.150 | 0.0733 | No | 0.1465 |
| Paralysis tick | 0.138 | 0.0989 | No | 0.1582 |
| Alpha-gal | 0.121 | 0.1483 | No | 0.1977 |
| Alpha-gal syndrome | -0.079 | 0.3463 | No | 0.3958 |
| Food allergy | 0.045 | 0.5928 | No | 0.5928 |

Trend-adjusted Spearman correlations (first-differenced series)

## 6.2 Cross-Correlation Analysis

``` r
# Focus on key AGS terms
ccf_terms <- c("alpha_gal", "mammalian_meat_allergy", "meat_allergy", "tick_allergy")

ccf_plots <- map(ccf_terms, function(term) {
  term_ts <- correlation_data |>
    dplyr::select(date, all_of(term), articles) |>
    drop_na()

  # Difference both series to ensure stationarity for CCF
  search_diff <- diff(term_ts[[term]])
  media_diff <- diff(term_ts$articles)

  ccf_result <- ccf(media_diff, search_diff, lag.max = 12, plot = FALSE)

  ccf_df <- tibble(
    lag = ccf_result$lag[, 1, 1],
    acf = ccf_result$acf[, 1, 1]
  )

  ci <- qnorm(0.975) / sqrt(length(search_diff))

  ggplot(ccf_df, aes(x = lag, y = acf)) +
    geom_hline(yintercept = 0, colour = "grey50") +
    geom_hline(yintercept = c(-ci, ci), colour = "blue", linetype = "dashed") +
    geom_col(fill = ifelse(abs(ccf_df$acf) > ci, "#e41a1c", "#2c7fb8"),
             width = 0.5) +
    labs(title = term_labels[term], x = "Lag (months)", y = "CCF") +
    theme_minimal(base_size = 9) +
    theme(plot.title = element_text(face = "bold", size = 10))
})

wrap_plots(ccf_plots, ncol = 2) +
  plot_annotation(
    title = "Cross-Correlation: Media Articles vs Search Interest",
    subtitle = "Positive lag = media leads search | Dashed lines = 95% significance bounds",
    theme = theme(
      plot.title = element_text(face = "bold", size = 14),
      plot.subtitle = element_text(colour = "grey40")
    )
  )

ggsave(file.path(fig_dir, "fig9_ccf_analysis.png"),
       width = 28, height = 20, units = "cm", dpi = 300)
```

<div id="fig-ccf">

![](ags_awareness_analysis_files/figure-commonmark/fig-ccf-1.png)

Figure 9: Cross-correlation functions between media article counts and
search RSV at different monthly lags. Positive lags indicate media
leading search interest.

</div>

## 6.3 Optimal Lag Identification

``` r
optimal_lags <- map_dfr(ccf_terms, function(term) {
  term_ts <- correlation_data |>
    dplyr::select(date, all_of(term), articles) |>
    drop_na()

  search_diff <- diff(term_ts[[term]])
  media_diff <- diff(term_ts$articles)

  ccf_result <- ccf(media_diff, search_diff, lag.max = 6, plot = FALSE)

  ccf_df <- tibble(
    lag = ccf_result$lag[, 1, 1],
    acf = ccf_result$acf[, 1, 1]
  )

  # Find lag with maximum absolute correlation (positive lags only = media leads)
  positive_lags <- ccf_df |> filter(lag >= 0)
  best <- positive_lags |> slice_max(abs(acf), n = 1)

  tibble(
    search_term = term_labels[term],
    optimal_lag = best$lag,
    ccf_at_lag = round(best$acf, 3),
    interpretation = case_when(
      best$lag == 0 ~ "Contemporaneous",
      best$lag > 0 ~ paste("Media leads by", best$lag, "month(s)"),
      TRUE ~ paste("Search leads by", abs(best$lag), "month(s)")
    )
  )
})

knitr::kable(optimal_lags,
             col.names = c("Search Term", "Optimal Lag", "CCF", "Interpretation"),
             caption = "Optimal lag between media coverage and search interest")
```

| Search Term            | Optimal Lag |   CCF | Interpretation  |
|:-----------------------|------------:|------:|:----------------|
| Alpha-gal              |           0 | 0.380 | Contemporaneous |
| Mammalian meat allergy |           0 | 0.385 | Contemporaneous |
| Meat allergy           |           0 | 0.438 | Contemporaneous |
| Tick allergy           |           0 | 0.263 | Contemporaneous |

Optimal lag between media coverage and search interest

# 7. Granger Causality Testing

## 7.1 Stationarity Tests

``` r
# ADF test (H0: unit root) and KPSS test (H0: stationary) for each series
all_series <- c(ccf_terms, "articles")
series_labels <- c(term_labels[ccf_terms], "articles" = "Media articles")

stationarity_results <- map_dfr(all_series, function(s) {
  ts_data <- correlation_data[[s]] |> na.omit()

  adf <- adf.test(ts_data, alternative = "stationary")
  kpss <- kpss.test(ts_data, null = "Level")

  tibble(
    series = series_labels[s],
    series_id = s,
    adf_statistic = round(adf$statistic, 3),
    adf_p = round(adf$p.value, 4),
    kpss_statistic = round(kpss$statistic, 3),
    kpss_p = round(kpss$p.value, 4),
    adf_stationary = adf$p.value < 0.05,
    kpss_stationary = kpss$p.value >= 0.05,  # fail to reject H0 of stationarity
    conclusion = case_when(
      adf$p.value < 0.05 & kpss$p.value >= 0.05 ~ "Stationary",
      adf$p.value >= 0.05 & kpss$p.value < 0.05 ~ "Non-stationary",
      TRUE ~ "Inconclusive"
    )
  )
})

# Store which series need differencing (for Granger causality)
needs_differencing <- stationarity_results |>
  filter(conclusion != "Stationary") |>
  pull(series_id)

knitr::kable(
  stationarity_results |>
    dplyr::select(series, adf_statistic, adf_p, kpss_statistic, kpss_p, conclusion),
  col.names = c("Series", "ADF Stat", "ADF p", "KPSS Stat", "KPSS p", "Conclusion"),
  digits = c(0, 3, 4, 3, 4, 0),
  caption = "Stationarity tests: ADF (H0: unit root) and KPSS (H0: stationary)"
)
```

| Series                 | ADF Stat |  ADF p | KPSS Stat | KPSS p | Conclusion     |
|:-----------------------|---------:|-------:|----------:|-------:|:---------------|
| Alpha-gal              |   -0.811 | 0.9585 |     2.086 | 0.0100 | Non-stationary |
| Mammalian meat allergy |   -3.877 | 0.0173 |     0.612 | 0.0216 | Inconclusive   |
| Meat allergy           |   -3.304 | 0.0734 |     1.083 | 0.0100 | Non-stationary |
| Tick allergy           |   -4.060 | 0.0100 |     0.929 | 0.0100 | Inconclusive   |
| Media articles         |   -4.810 | 0.0100 |     0.173 | 0.1000 | Stationary     |

Stationarity tests: ADF (H0: unit root) and KPSS (H0: stationary)

## 7.2 VAR Model and Granger Causality

``` r
granger_results <- map_dfr(ccf_terms, function(term) {
  # Create bivariate data frame
  bivar_data <- correlation_data |>
    dplyr::select(date, search = all_of(term), media = articles) |>
    drop_na()

  # Only difference non-stationary series (based on ADF + KPSS results)
  search_vec <- bivar_data$search
  media_vec <- bivar_data$media
  diff_search <- term %in% needs_differencing
  diff_media <- "articles" %in% needs_differencing

  if (diff_search) search_vec <- diff(search_vec)
  if (diff_media) media_vec <- diff(media_vec)

  # Align lengths if only one was differenced
  min_len <- min(length(search_vec), length(media_vec))
  search_vec <- tail(search_vec, min_len)
  media_vec <- tail(media_vec, min_len)

  var_data <- cbind(search_ts = search_vec, media_ts = media_vec)

  tryCatch({
    # Select optimal lag order
    lag_select <- VARselect(var_data, lag.max = 6, type = "const")
    optimal_p <- lag_select$selection["AIC(n)"]
    optimal_p <- max(1, min(optimal_p, 4))  # bound between 1 and 4

    # Fit VAR model
    var_model <- VAR(var_data, p = optimal_p, type = "const")

    # Granger causality tests (both directions)
    gc_media_to_search <- causality(var_model, cause = "media_ts")
    gc_search_to_media <- causality(var_model, cause = "search_ts")

    tibble(
      search_term = term_labels[term],
      differenced = {
        d <- c(if (diff_search) "search", if (diff_media) "media")
        if (length(d) == 0) "none" else paste(d, collapse = "+")
      },
      var_lag = optimal_p,
      media_causes_search_F = round(gc_media_to_search$Granger$statistic, 3),
      media_causes_search_p = gc_media_to_search$Granger$p.value,
      search_causes_media_F = round(gc_search_to_media$Granger$statistic, 3),
      search_causes_media_p = gc_search_to_media$Granger$p.value
    )
  }, error = function(e) {
    tibble(
      search_term = term_labels[term],
      differenced = NA_character_,
      var_lag = NA_integer_,
      media_causes_search_F = NA_real_,
      media_causes_search_p = NA_real_,
      search_causes_media_F = NA_real_,
      search_causes_media_p = NA_real_
    )
  })
})

# Apply BH correction
granger_results <- granger_results |>
  mutate(
    media_to_search_bh = p.adjust(media_causes_search_p, method = "BH"),
    search_to_media_bh = p.adjust(search_causes_media_p, method = "BH")
  )

knitr::kable(
  granger_results |>
    dplyr::select(search_term, differenced, var_lag, media_causes_search_F,
           media_causes_search_p, media_to_search_bh,
           search_causes_media_F, search_causes_media_p, search_to_media_bh),
  col.names = c("Search Term", "Differenced", "VAR Lag", "F (Media->Search)", "p",
                 "BH adj. p", "F (Search->Media)", "p", "BH adj. p"),
  digits = c(0, 0, 0, 2, 4, 4, 2, 4, 4),
  caption = "Granger causality tests: bidirectional media-search relationships (differencing conditioned on stationarity)"
)
```

| Search Term | Differenced | VAR Lag | F (Media-\>Search) | p | BH adj. p | F (Search-\>Media) | p | BH adj. p |
|:---|:---|---:|---:|---:|---:|---:|---:|---:|
| Alpha-gal | search | 3 | 0.396 | 0.7558521 | 0.995 | 1.648 | 0.1785921 | 0.7144 |
| Mammalian meat allergy | search | 2 | 0.664 | 0.5155502 | 0.995 | 0.293 | 0.7462522 | 0.7776 |
| Meat allergy | search | 3 | 0.024 | 0.9950242 | 0.995 | 0.366 | 0.7776173 | 0.7776 |
| Tick allergy | search | 4 | 0.601 | 0.6623864 | 0.995 | 1.042 | 0.3861173 | 0.7722 |

Granger causality tests: bidirectional media-search relationships
(differencing conditioned on stationarity)

# 8. Interrupted Time Series Analysis

## 8.1 Identify Key Media Events

``` r
# Identify months with media article clusters
media_event_months <- media_monthly |>
  filter(articles > 0) |>
  arrange(desc(articles))

cat("Months with media coverage:\n")
print(media_event_months, n = 20)

# Key events based on content analysis:
# 1. Aug 2023: Major cluster - ticks thriving, meat allergy, US 450K cases
# 2. Nov 2025: Coroner inquest into teen death from MMA
# 3. Jun 2016: Early coverage - thousands allergic to red meat
key_events <- tibble(
  date = as.Date(c("2023-08-01", "2025-11-01", "2018-08-01")),
  event = c(
    "Aug 2023: Tick boom / US 450K cases / SBS & ABC coverage",
    "Nov 2025: NSW coroner inquest into teen MMA death",
    "Aug-Sep 2018: Regional media - tick health risks"
  )
)

knitr::kable(key_events, col.names = c("Date", "Event"),
             caption = "Key identified media events for ITS analysis")
```

    Months with media coverage:
    # A tibble: 29 × 3
       date       total_articles articles
       <date>              <dbl>    <int>
     1 2023-08-01         113942       11
     2 2018-09-01          63586       10
     3 2025-11-01          62957        9
     4 2015-10-01          61208        4
     5 2025-05-01          72186        4
     6 2025-08-01          73798        4
     7 2014-08-01          40161        3
     8 2016-10-01          50611        3
     9 2018-08-01         142421        3
    10 2018-06-01         159079        2
    11 2018-07-01         137330        2
    12 2019-08-01         117403        2
    13 2020-01-01         107590        2
    14 2020-11-01          90906        2
    15 2022-09-01          98011        2
    16 2022-11-01          99525        2
    17 2016-06-01          53121        1
    18 2016-09-01          64627        1
    19 2019-01-01         102986        1
    20 2019-06-01         121785        1
    # ℹ 9 more rows

| Date       | Event                                                    |
|:-----------|:---------------------------------------------------------|
| 2023-08-01 | Aug 2023: Tick boom / US 450K cases / SBS & ABC coverage |
| 2025-11-01 | Nov 2025: NSW coroner inquest into teen MMA death        |
| 2018-08-01 | Aug-Sep 2018: Regional media - tick health risks         |

Key identified media events for ITS analysis

## 8.2 ITS Analysis for Aug 2023 Media Event

``` r
# Focus on alpha_gal - the term with most clear trend
its_data <- trends_avg |>
  filter(search_term == "alpha_gal") |>
  mutate(
    time = row_number(),
    post_aug2023 = as.integer(date >= as.Date("2023-08-01")),
    time_after = ifelse(post_aug2023 == 1, time - min(time[post_aug2023 == 1]) + 1, 0),
    month_num = month(date),
    warm_season = as.integer(month_num %in% c(10, 11, 12, 1, 2, 3)),
    rsv_count = round(mean_rsv) + 1
  )

# Segmented quasi-Poisson regression
its_model <- glm(
  rsv_count ~ time + post_aug2023 + time_after + warm_season,
  family = quasipoisson(),
  data = its_data
)

its_summary <- summary(its_model)

# Autocorrelation diagnostic
dw_test <- dwtest(its_model)
cat("Durbin-Watson test for residual autocorrelation: DW =",
    round(dw_test$statistic, 3), ", p =", round(dw_test$p.value, 4), "\n")
if (dw_test$p.value < 0.05) {
  cat("  -> Significant autocorrelation detected. Using Newey-West robust SEs.\n\n")
  nw_vcov <- NeweyWest(its_model, lag = 3, prewhite = FALSE)
  its_coeftest <- coeftest(its_model, vcov. = nw_vcov)
} else {
  cat("  -> No significant autocorrelation. Using model-based SEs.\n\n")
  its_coeftest <- coeftest(its_model)
}

# Report with 95% CIs for IRR
its_params <- c("post_aug2023", "time_after", "warm_season")
its_param_labels <- c("Level change", "Slope change", "Warm season")

cat("ITS Model for Alpha-Gal (Aug 2023 intervention):\n")
cat("=========================================\n")
for (i in seq_along(its_params)) {
  param <- its_params[i]
  est <- its_coeftest[param, "Estimate"]
  se <- its_coeftest[param, "Std. Error"]
  p <- its_coeftest[param, 4]
  irr <- exp(est)
  irr_lower <- exp(est - 1.96 * se)
  irr_upper <- exp(est + 1.96 * se)

  cat(sprintf("  %s: coef = %.3f | IRR = %.2f (95%% CI: %.2f-%.2f) | p = %.4f %s\n",
              its_param_labels[i], est, irr, irr_lower, irr_upper, p,
              ifelse(p < 0.05, "*", "")))
}
cat("Dispersion:", round(its_summary$dispersion, 2), "\n")
n_post_aug2023 <- sum(its_data$post_aug2023)
cat("Post-intervention observations:", n_post_aug2023, "\n")
cat("\nNote: No parameters are statistically significant at alpha = 0.05.",
    "\nThe Aug 2023 media cluster did not produce a detectable step change",
    "in search interest\nbeyond the pre-existing upward trend.\n")

# Visualise
its_data$fitted <- predict(its_model, type = "response") - 1

ggplot(its_data, aes(x = date)) +
  geom_line(aes(y = mean_rsv), colour = "#2c7fb8", alpha = 0.5) +
  geom_point(aes(y = mean_rsv), colour = "#2c7fb8", size = 1, alpha = 0.5) +
  geom_line(aes(y = fitted), colour = "#e41a1c", linewidth = 0.8) +
  geom_vline(xintercept = as.Date("2023-08-01"),
             linetype = "dashed", colour = "red", linewidth = 0.6) +
  annotate("text", x = as.Date("2023-08-01"), y = max(its_data$mean_rsv) * 0.95,
           label = "Aug 2023\nMedia cluster", hjust = -0.1, size = 3,
           colour = "red", fontface = "italic") +
  labs(
    title = "Interrupted Time Series: Alpha-Gal Search Interest",
    subtitle = "Intervention point: August 2023 media coverage cluster",
    x = NULL, y = "RSV",
    caption = "Blue = observed | Red = ITS model fit"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(colour = "grey40"),
    plot.caption = element_text(hjust = 0, face = "italic")
  )
```

![Interrupted time series analysis for the August 2023 media event
cluster (alpha-gal search term). Red dashed line indicates the
intervention
point.](ags_awareness_analysis_files/figure-commonmark/its-aug2023-1.png)

``` r
ggsave(file.path(fig_dir, "fig10_its_aug2023.png"),
       width = 25, height = 15, units = "cm", dpi = 300)
```

    Durbin-Watson test for residual autocorrelation: DW = 0.889 , p = 0 
      -> Significant autocorrelation detected. Using Newey-West robust SEs.

    ITS Model for Alpha-Gal (Aug 2023 intervention):
    =========================================
      Level change: coef = 0.275 | IRR = 1.32 (95% CI: 0.84-2.06) | p = 0.2293 
      Slope change: coef = -0.006 | IRR = 0.99 (95% CI: 0.97-1.02) | p = 0.6140 
      Warm season: coef = 0.036 | IRR = 1.04 (95% CI: 0.84-1.28) | p = 0.7360 
    Dispersion: 3.17 
    Post-intervention observations: 31 

    Note: No parameters are statistically significant at alpha = 0.05. 
    The Aug 2023 media cluster did not produce a detectable step change in search interest
    beyond the pre-existing upward trend.

## 8.3 ITS Analysis for Nov 2025 Coroner Inquest

``` r
its_data2 <- trends_avg |>
  filter(search_term == "alpha_gal") |>
  mutate(
    time = row_number(),
    post_nov2025 = as.integer(date >= as.Date("2025-11-01")),
    time_after = ifelse(post_nov2025 == 1, time - min(time[post_nov2025 == 1]) + 1, 0),
    month_num = month(date),
    warm_season = as.integer(month_num %in% c(10, 11, 12, 1, 2, 3)),
    rsv_count = round(mean_rsv) + 1
  )

its_model2 <- glm(
  rsv_count ~ time + post_nov2025 + time_after + warm_season,
  family = quasipoisson(),
  data = its_data2
)

its_summary2 <- summary(its_model2)

# Autocorrelation diagnostic
dw_test2 <- dwtest(its_model2)
cat("Durbin-Watson test: DW =", round(dw_test2$statistic, 3),
    ", p =", round(dw_test2$p.value, 4), "\n")
if (dw_test2$p.value < 0.05) {
  cat("  -> Significant autocorrelation. Using Newey-West robust SEs.\n\n")
  nw_vcov2 <- NeweyWest(its_model2, lag = 3, prewhite = FALSE)
  its_coeftest2 <- coeftest(its_model2, vcov. = nw_vcov2)
} else {
  cat("  -> No significant autocorrelation. Using model-based SEs.\n\n")
  its_coeftest2 <- coeftest(its_model2)
}

# Report with 95% CIs
its_params2 <- c("post_nov2025", "time_after", "warm_season")
its_param_labels2 <- c("Level change", "Slope change", "Warm season")

cat("ITS Model for Alpha-Gal (Nov 2025 intervention):\n")
cat("=========================================\n")
for (i in seq_along(its_params2)) {
  param <- its_params2[i]
  est <- its_coeftest2[param, "Estimate"]
  se <- its_coeftest2[param, "Std. Error"]
  p <- its_coeftest2[param, 4]
  irr <- exp(est)
  irr_lower <- exp(est - 1.96 * se)
  irr_upper <- exp(est + 1.96 * se)

  cat(sprintf("  %s: coef = %.3f | IRR = %.2f (95%% CI: %.2f-%.2f) | p = %.4f %s\n",
              its_param_labels2[i], est, irr, irr_lower, irr_upper, p,
              ifelse(p < 0.05, "*", "")))
}
cat("Dispersion:", round(its_summary2$dispersion, 2), "\n")
n_post_nov2025 <- sum(its_data2$post_nov2025)
cat("Post-intervention observations:", n_post_nov2025, "\n")
cat("\nCAUTION: Only", n_post_nov2025, "post-intervention months are available.",
    "\nBernal et al. (2017) recommend a minimum of 8-12 post-intervention",
    "observations\nfor reliable ITS estimation. These results should be",
    "considered preliminary/exploratory\nand will need to be reassessed",
    "as more post-event data accumulate.\n")

its_data2$fitted <- predict(its_model2, type = "response") - 1

ggplot(its_data2, aes(x = date)) +
  geom_line(aes(y = mean_rsv), colour = "#2c7fb8", alpha = 0.5) +
  geom_point(aes(y = mean_rsv), colour = "#2c7fb8", size = 1, alpha = 0.5) +
  geom_line(aes(y = fitted), colour = "#e41a1c", linewidth = 0.8) +
  geom_vline(xintercept = as.Date("2025-11-01"),
             linetype = "dashed", colour = "red", linewidth = 0.6) +
  annotate("text", x = as.Date("2025-11-01"), y = max(its_data2$mean_rsv) * 0.95,
           label = "Nov 2025\nCoroner inquest", hjust = -0.1, size = 3,
           colour = "red", fontface = "italic") +
  labs(
    title = "Interrupted Time Series: Alpha-Gal Search Interest",
    subtitle = "Intervention point: November 2025 NSW coroner inquest into teen MMA death",
    x = NULL, y = "RSV",
    caption = "Blue = observed | Red = ITS model fit"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(colour = "grey40"),
    plot.caption = element_text(hjust = 0, face = "italic")
  )
```

![Interrupted time series analysis for the November 2025 coroner inquest
event.](ags_awareness_analysis_files/figure-commonmark/its-nov2025-1.png)

``` r
ggsave(file.path(fig_dir, "fig11_its_nov2025.png"),
       width = 25, height = 15, units = "cm", dpi = 300)
```

    Durbin-Watson test: DW = 0.743 , p = 0 
      -> Significant autocorrelation. Using Newey-West robust SEs.

    ITS Model for Alpha-Gal (Nov 2025 intervention):
    =========================================
      Level change: coef = 0.763 | IRR = 2.15 (95% CI: 1.80-2.56) | p = 0.0000 *
      Slope change: coef = -0.226 | IRR = 0.80 (95% CI: 0.78-0.81) | p = 0.0000 *
      Warm season: coef = -0.023 | IRR = 0.98 (95% CI: 0.79-1.21) | p = 0.8313 
    Dispersion: 3.07 
    Post-intervention observations: 4 

    CAUTION: Only 4 post-intervention months are available. 
    Bernal et al. (2017) recommend a minimum of 8-12 post-intervention observations
    for reliable ITS estimation. These results should be considered preliminary/exploratory
    and will need to be reassessed as more post-event data accumulate.

# 9. Summary of Findings

``` r
# Dynamically extract key findings
ag_peak <- term_summary |> filter(search_term_label == "Alpha-gal")
ag_peak_month <- format(ag_peak$peak_month, "%B %Y")
ag_peak_rsv <- round(ag_peak$peak_rsv, 1)

cat("=" |> strrep(70), "\n")
cat("SUMMARY OF KEY FINDINGS\n")
cat("=" |> strrep(70), "\n\n")

cat("1. SEARCH INTEREST TRENDS\n")
cat("-" |> strrep(40), "\n")
cat("  - Data:", n_distinct(trends_avg$search_term), "search terms, monthly RSV",
    format(min(trends_avg$date), "%Y"), "-", format(max(trends_avg$date), "%Y"),
    "\n    averaged across", max(trends_avg$n_downloads), "daily downloads\n")
cat("  - Alpha-gal search interest peaked at RSV =", ag_peak_rsv, "in", ag_peak_month, "\n")
cat("  - Strong upward trend from ~2020 onwards across AGS-specific terms\n")
cat("  -", n_excluded, "off-topic media articles (xenotransplantation, Lyme)",
    "were excluded\n\n")

cat("2. SAMPLING RELIABILITY\n")
cat("-" |> strrep(40), "\n")
cat("  - Low-volume terms (", paste(term_labels[unreliable_terms], collapse = ", "),
    ")\n    have median CV >100% and results should be interpreted cautiously\n")
cat("  - High-volume terms (food allergy, paralysis tick) have CV <5%\n\n")

cat("3. SEASONALITY\n")
cat("-" |> strrep(40), "\n")
cat("  - Paralysis tick and tick allergy show significant seasonality",
    "(KW p < 0.05)\n    in both raw and detrended analyses\n")
cat("  - Alpha-gal does not show significant seasonality after detrending,\n")
cat("    despite biological plausibility (tick exposure -> awareness)\n\n")

cat("4. MEDIA-AWARENESS RELATIONSHIP\n")
cat("-" |> strrep(40), "\n")
cat("  - Raw Spearman correlations are moderate (rho 0.18-0.32 for AGS terms)\n")
cat("    but may be confounded by shared temporal trends\n")
cat("  - Trend-adjusted (differenced) correlations provide a more conservative estimate\n")
cat("  - Cross-correlation analysis shows contemporaneous (lag 0) association\n\n")

cat("5. GRANGER CAUSALITY\n")
cat("-" |> strrep(40), "\n")
cat("  - No significant Granger causality in either direction after BH correction\n")
cat("  - Differencing was conditioned on stationarity test results (ADF + KPSS)\n\n")

cat("6. KEY MEDIA EVENTS (ITS)\n")
cat("-" |> strrep(40), "\n")
cat("  - Aug 2023 media cluster: NO significant level or slope change (p > 0.05)\n")
cat("    The pre-existing upward trend appears sufficient to explain post-event RSV\n")
cat("  - Nov 2025 coroner inquest: Significant level change (IRR ~2),",
    "but only\n   ", n_post_nov2025, "post-intervention months available",
    "(minimum 8-12 recommended;\n    Bernal et al. 2017). Results are preliminary.\n")
```

    ====================================================================== 
    SUMMARY OF KEY FINDINGS
    ====================================================================== 

    1. SEARCH INTEREST TRENDS
    ---------------------------------------- 
      - Data: 8 search terms, monthly RSV 2014 - 2026 
        averaged across 16 daily downloads
      - Alpha-gal search interest peaked at RSV = 99.8 in November 2025 
      - Strong upward trend from ~2020 onwards across AGS-specific terms
      - 17 off-topic media articles (xenotransplantation, Lyme) were excluded

    2. SAMPLING RELIABILITY
    ---------------------------------------- 
      - Low-volume terms ( Mammalian meat allergy, Red meat allergy, Alpha-gal syndrome )
        have median CV >100% and results should be interpreted cautiously
      - High-volume terms (food allergy, paralysis tick) have CV <5%

    3. SEASONALITY
    ---------------------------------------- 
      - Paralysis tick and tick allergy show significant seasonality (KW p < 0.05)
        in both raw and detrended analyses
      - Alpha-gal does not show significant seasonality after detrending,
        despite biological plausibility (tick exposure -> awareness)

    4. MEDIA-AWARENESS RELATIONSHIP
    ---------------------------------------- 
      - Raw Spearman correlations are moderate (rho 0.18-0.32 for AGS terms)
        but may be confounded by shared temporal trends
      - Trend-adjusted (differenced) correlations provide a more conservative estimate
      - Cross-correlation analysis shows contemporaneous (lag 0) association

    5. GRANGER CAUSALITY
    ---------------------------------------- 
      - No significant Granger causality in either direction after BH correction
      - Differencing was conditioned on stationarity test results (ADF + KPSS)

    6. KEY MEDIA EVENTS (ITS)
    ---------------------------------------- 
      - Aug 2023 media cluster: NO significant level or slope change (p > 0.05)
        The pre-existing upward trend appears sufficient to explain post-event RSV
      - Nov 2025 coroner inquest: Significant level change (IRR ~2), but only
        4 post-intervention months available (minimum 8-12 recommended;
        Bernal et al. 2017). Results are preliminary.

``` r
sessionInfo()
```

    R version 4.4.1 (2024-06-14)
    Platform: aarch64-apple-darwin20
    Running under: macOS 26.2

    Matrix products: default
    BLAS:   /Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/lib/libRblas.0.dylib 
    LAPACK: /Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/lib/libRlapack.dylib;  LAPACK version 3.12.0

    locale:
    [1] en_AU.UTF-8/en_AU.UTF-8/en_AU.UTF-8/C/en_AU.UTF-8/en_AU.UTF-8

    time zone: Australia/Brisbane
    tzcode source: internal

    attached base packages:
    [1] stats     graphics  grDevices utils     datasets  methods   base     

    other attached packages:
     [1] vars_1.6-1        urca_1.3-4        strucchange_1.5-4 scales_1.4.0     
     [5] segmented_2.1-4   MASS_7.3-65       sandwich_3.1-1    lmtest_0.9-40    
     [9] zoo_1.8-15        tseries_0.10-58   forecast_8.24.0   mgcv_1.9-3       
    [13] nlme_3.1-168      patchwork_1.3.2   lubridate_1.9.4   forcats_1.0.0    
    [17] stringr_1.6.0     dplyr_1.1.4       purrr_1.1.0       readr_2.1.6      
    [21] tidyr_1.3.1       tibble_3.3.1      ggplot2_4.0.0     tidyverse_2.0.0  

    loaded via a namespace (and not attached):
     [1] gtable_0.3.6       xfun_0.53          lattice_0.22-7     tzdb_0.5.0        
     [5] quadprog_1.5-8     vctrs_0.7.1        tools_4.4.1        generics_0.1.4    
     [9] curl_7.0.0         parallel_4.4.1     xts_0.14.1         pkgconfig_2.0.3   
    [13] Matrix_1.7-4       RColorBrewer_1.1-3 S7_0.2.0           lifecycle_1.0.5   
    [17] compiler_4.4.1     farver_2.1.2       textshaping_1.0.3  htmltools_0.5.8.1 
    [21] yaml_2.3.10        crayon_1.5.3       pillar_1.11.1      fracdiff_1.5-3    
    [25] tidyselect_1.2.1   digest_0.6.37      stringi_1.8.7      labeling_0.4.3    
    [29] splines_4.4.1      fastmap_1.2.0      grid_4.4.1         colorspace_2.1-1  
    [33] cli_3.6.5          magrittr_2.0.4     utf8_1.2.6         withr_3.0.2       
    [37] bit64_4.6.0-1      timechange_0.3.0   TTR_0.24.4         rmarkdown_2.29    
    [41] quantmod_0.4.28    bit_4.6.0          nnet_7.3-20        timeDate_4041.110 
    [45] ragg_1.5.0         hms_1.1.4          evaluate_1.0.5     knitr_1.50        
    [49] viridisLite_0.4.2  rlang_1.1.7        Rcpp_1.1.1         glue_1.8.0        
    [53] vroom_1.7.0        jsonlite_2.0.0     R6_2.6.1           systemfonts_1.2.3 
