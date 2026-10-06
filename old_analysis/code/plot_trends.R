#!/usr/bin/env Rscript

# Plot Google Trends data over time
# Usage: Rscript plot_trends.R <input_csv> <output_image>

library(tidyverse)
library(lubridate)

#' Plot Google Trends data
#'
#' Reads a CSV file containing Google Trends data and plots a line graph
#' of each search phrase's trend over time.
#'
#' @param csv_file_path Path to the input CSV file
#' @param output_image_path Path to save the generated plot image (e.g., PNG)
plot_google_trends <- function(csv_file_path, output_image_path) {
  # Check if input file exists

  if (!file.exists(csv_file_path)) {
    stop(paste("Error: CSV file not found at", csv_file_path))
  }

  # Read the CSV file
  df <- tryCatch(
    {
      read_csv(csv_file_path, show_col_types = FALSE)
    },
    error = function(e) {
      stop(paste("Error reading CSV file:", e$message))
    }
  )

  # Check if the data frame has data beyond the date column
  if (nrow(df) == 0 || ncol(df) <= 1) {
    stop(
      "No data to plot. The data frame is empty or contains no keyword columns."
    )
  }

  # Parse the date column
  df <- df %>%
    mutate(date = ymd(date))

  # Pivot to long format for ggplot
  df_long <- df %>%
    pivot_longer(
      cols = -date,
      names_to = "search_term",
      values_to = "interest"
    )

  # Create the plot
  p <- ggplot(df_long, aes(x = date, y = interest, colour = search_term)) +
    geom_line(linewidth = 0.8) +
    labs(
      title = "Google Search Interest Over Time (Monthly - Australia)",
      x = "Date",
      y = "Relative Search Interest",
      colour = "Search Terms"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      legend.position = "right",
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(linetype = "dashed", alpha = 0.7)
    )

  # Ensure the output directory exists
  output_dir <- dirname(output_image_path)
  if (output_dir != "" && !dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }

  # Save the plot
  tryCatch(
    {
      ggsave(
        output_image_path,
        plot = p,
        width = 12,
        height = 7,
        dpi = 300
      )
      message(paste("Plot saved successfully to", output_image_path))
    },
    error = function(e) {
      stop(paste("Error saving plot to", output_image_path, ":", e$message))
    }
  )
}

# Main execution
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  cat("Usage: Rscript plot_trends.R <input_csv> <output_image>\n")
  cat(
    "Example: Rscript plot_trends.R ../data/google_trends_monthly_au.csv ../figures/google_trends_monthly_plot.png\n"
  )
  quit(status = 1)
}

input_csv <- args[1]
output_image <- args[2]

plot_google_trends(input_csv, output_image)
