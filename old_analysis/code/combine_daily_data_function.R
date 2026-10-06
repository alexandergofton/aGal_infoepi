# A function to aggregate daily google trend results into a single daily dataset
# and plot them.

# Alexander W. Gofton 13/02/2026

# Load libraries
library(tidyverse)
library(patchwork)

#################################
# FUNCTION
#################################
combine_daily_data <- function(date_str, save_plot = TRUE) {
  # Set file directory
  files_dir <- "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi/data/"

  # Define search terms
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

  # Create a list to store data frames
  trend_data <- list()
  trend_data[[date_str]] <- list()

  # Load all files into a nested list
  for (term in search_terms) {
    file_path <- paste0(
      files_dir,
      "google_trends_monthly_au_",
      term,
      "_",
      date_str,
      ".csv"
    )

    # Check if file exists before trying to read it
    if (file.exists(file_path)) {
      # Read the file and store in list with the term name
      df <- read_csv(file_path, show_col_types = FALSE)

      # Check if date column is character format (like "1/2/2014")
      if (is.character(df$date)) {
        # Try to parse the date - first check format
        if (grepl("^\\d{1,2}/\\d{1,2}/\\d{4}$", df$date[1])) {
          # Format is D/M/YYYY
          df$date <- as.Date(df$date, format = "%d/%m/%Y")
        } else {
          # Try other common formats
          df$date <- as.Date(df$date)
        }
      }

      # Store the data with consistent date format
      trend_data[[date_str]][[term]] <- df
      cat("Loaded:", term, "\n")
    } else {
      warning(paste("File not found:", file_path))
    }
  }

  # Combine datasets using reduce and join
  # Start with the first dataset
  first_term <- search_terms[1]
  combined_data <- trend_data[[date_str]][[first_term]]

  # Join with remaining datasets
  for (term in search_terms[-1]) {
    if (!is.null(trend_data[[date_str]][[term]])) {
      combined_data <- left_join(
        combined_data,
        trend_data[[date_str]][[term]],
        by = "date"
      )
    }
  }

  # Create mapping for renaming columns
  col_names <- search_terms |>
    gsub(pattern = "_", replacement = " ", x = _) |>
    gsub(pattern = "-", replacement = "-", x = _)

  new_col_names <- search_terms |>
    gsub(pattern = "_", replacement = ".", x = _) |>
    gsub(pattern = "-", replacement = ".", x = _)

  # Create named vector for rename
  rename_mapping <- setNames(col_names, new_col_names)

  # Rename columns
  combined_data <- combined_data |>
    rename(!!!rename_mapping)

  # Save combined data
  processed_data_dir <- "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi/processed_data/"

  write.csv(
    combined_data,
    paste0(processed_data_dir, "google_trends_combined_", date_str, ".csv")
  )

  # Transform to long format for plotting
  data_long <- combined_data |>
    pivot_longer(
      cols = -date,
      names_to = "search_term",
      values_to = "interest"
    )

  # Create the faceted plot
  plot <- ggplot(data_long, aes(x = date, y = interest)) +
    geom_line(color = "#2c7fb8", linewidth = 0.8) +
    facet_wrap(~search_term, scales = "free_y", ncol = 2) +
    labs(
      title = "Google Trends Search Interest (2014-2026)",
      subtitle = paste0(
        "Monthly data for Australia (extracted ",
        date_str,
        ")"
      ),
      x = "Year",
      y = "Relative Interest"
    ) +
    theme_minimal() +
    theme(
      strip.text = element_text(face = "bold"),
      panel.grid.minor = element_blank(),
      panel.spacing = unit(1, "lines"),
      plot.title = element_text(face = "bold", size = 14),
      plot.subtitle = element_text(color = "gray30", size = 11)
    ) +
    scale_x_date(date_breaks = "2 years", date_labels = "%Y")

  # Save plot if requested
  if (save_plot) {
    # Save plot
    output_dir <- "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi/figures/"
    filename <- paste0(
      output_dir,
      "/google_trends_",
      date_str,
      ".png"
    )

    ggsave(
      filename,
      plot = plot,
      height = 15,
      width = 24,
      dpi = 300,
      units = "cm"
    )

    cat("Plot saved to:", filename, "\n")
  }

  return(plot)
}
