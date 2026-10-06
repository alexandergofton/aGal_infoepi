# Function to analyze and visualize average Google Trends data across multiple dates
plot_average_trends <- function(
  date_list,
  processed_data_dir = "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi/processed_data/",
  output_dir = "/Users/gof005/Library/CloudStorage/OneDrive-CSIRO/OneDrive - Docs/01_Projects/alpha_gal/aGal_infoepi/figures/"
) {
  # Initialize empty list to store dataframes
  all_data_long <- list()

  # Load and process each date's data
  for (i in seq_along(date_list)) {
    date_str <- date_list[i]
    file_path <- paste0(
      processed_data_dir,
      "google_trends_combined_",
      date_str,
      ".csv"
    )

    if (file.exists(file_path)) {
      # Read data
      df <- read_csv(file_path, show_col_types = FALSE)

      # Remove any automatically generated column names like ...1
      # First check if there are columns starting with '...'
      cols_to_remove <- grep("^\\.\\.\\.", names(df))
      if (length(cols_to_remove) > 0) {
        df <- df[, -cols_to_remove]
      }

      # Also check for X1 column from write.csv
      if ("X1" %in% names(df)) {
        df <- df |> select(-X1)
      }

      # Convert to long format and add date of extraction
      df_long <- df |>
        pivot_longer(
          cols = -date,
          names_to = "search_term",
          values_to = "interest"
        ) |>
        mutate(extraction_date = date_str)

      all_data_long[[i]] <- df_long
      cat("Processed data from:", date_str, "\n")
    } else {
      warning(paste("File not found:", file_path))
    }
  }

  # Combine all data
  combined_long <- bind_rows(all_data_long)

  # Calculate summary statistics by date and search term
  summary_stats <- combined_long |>
    group_by(date, search_term) |>
    summarise(
      mean_interest = mean(interest, na.rm = TRUE),
      sd_interest = sd(interest, na.rm = TRUE),
      se_interest = sd_interest / sqrt(n()),
      lower_ci = mean_interest - 1.96 * se_interest, # 95% confidence interval
      upper_ci = mean_interest + 1.96 * se_interest,
      n_obs = n(),
      .groups = "drop"
    )

  # Create faceted plot with mean and variability bands
  plot <- ggplot(summary_stats, aes(x = date, y = mean_interest)) +
    geom_ribbon(
      aes(ymin = lower_ci, ymax = upper_ci),
      fill = "#2c7fb8",
      alpha = 0.2
    ) + # 95% CI band
    geom_line(color = "#2c7fb8", linewidth = 0.8) +
    facet_wrap(~search_term, scales = "free_y", ncol = 2) +
    labs(
      title = "Average Google Trends Search Interest (2014-2026)",
      subtitle = paste0(
        "Mean of data collected between ",
        min(date_list),
        " and ",
        max(date_list),
        " (n = ",
        length(date_list),
        " days)"
      ),
      x = "Year",
      y = "Mean Relative Interest",
      caption = "Ribbon shows 95% confidence interval"
    ) +
    theme_minimal() +
    theme(
      strip.text = element_text(face = "bold"),
      panel.grid.minor = element_blank(),
      panel.spacing = unit(1, "lines"),
      plot.title = element_text(face = "bold", size = 14),
      plot.subtitle = element_text(color = "gray30", size = 11),
      plot.caption = element_text(hjust = 0, face = "italic", size = 9)
    ) +
    scale_x_date(date_breaks = "2 years", date_labels = "%Y")

  # Save plot
  filename <- paste0(
    output_dir,
    "google_trends_average_",
    min(date_list),
    "_to_",
    max(date_list),
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

  # Return both the plot and the summary data
  return(list(
    plot = plot,
    summary_stats = summary_stats,
    combined_data = combined_long
  ))
}
