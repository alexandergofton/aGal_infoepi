
# %% ####################################
# Import modules
#########################################

import time  # Import time module
from datetime import date, timedelta
import pandas as pd
from pytrends import exceptions  # Import pytrends exceptions
from pytrends.request import TrendReq

#########################################
# Create function to get data
#########################################

def get_google_trends_data(keywords, geo='AU', category=0, timeframe='2014-02-01 2026-02-01',
                           gprop='', save_path=None):
    """
    Fetches Google Trends data for the specified keywords, geographic region, and timeframe.
    For timeframes longer than 5 years, data will be returned at a monthly granularity.

    Args:
        keywords (list): A list of search terms (e.g., ['alpha gal', 'mammalian meat allergy']).
        geo (str): Geographic region code (e.g., 'AU' for Australia). Defaults to 'AU'.
        category (int): Google Trends category ID. 0 is 'Health'. Defaults to 0.
        timeframe (str): Timeframe for the search (e.g., '2014-02-01 2026-02-01').
                         For monthly data, ensure the range is greater than 5 years.
        gprop (str): Google property to search (e.g., '', 'images', 'news', 'youtube').
                     Defaults to ''.
        save_path (str, optional): If provided, the data will be saved to this CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the Google Trends interest over time.
    """
    pytrends = TrendReq(hl='en-US', tz=360) # hl: host language, tz: timezone (360 for Australia/Sydney)

    print(f"Fetching data for keywords: {keywords}")
    print(f"Geo: {geo}, Category: {category}, Timeframe: {timeframe}")

    pytrends.build_payload(
        kw_list=keywords,
        cat=category,
        geo=geo,
        timeframe=timeframe,
        gprop=gprop
    )

    df = pd.DataFrame() # Initialize empty DataFrame

    max_retries = 5
    retry_delay = 5 # seconds
    for attempt in range(max_retries):
        try:
            df = pytrends.interest_over_time()
            if not df.empty:
                # Add a small delay after a successful request to be courteous to the API
                time.sleep(1)
            break # Break loop if successful
        except exceptions.TooManyRequestsError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Rate limit hit. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2 # Exponential backoff
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break # Exit on other errors

    if df.empty:
        print("No data returned for the specified parameters after multiple retries. Please check keywords, geo, or timeframe.")
        return pd.DataFrame()

    if 'isPartial' in df.columns:
        df = df.drop(columns=['isPartial'])

    if save_path:
        df.to_csv(save_path)
        print(f"Data saved to {save_path}")

    return df


#########################################
# Run the function for AUS
#########################################

if __name__ == "__main__":

    # Get today's date in YYYY-MM-DD format
    import datetime
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')

    # Define all keywords to search for
    keywords_list = [
        "alpha gal",
        "mammalian meat allergy",
        "red meat allergy",
        "meat allergy",
        "paralysis tick",
        "alpha-gal syndrome",
        "tick allergy",
        "food allergy", # Control term

    ]

    # Google Trends category for Health
    health_category_id = 0 # 0 = ALL

    # Delay between API calls (in seconds)
    delay_between_calls = 3

    # Loop through each keyword
    for i, keyword in enumerate(keywords_list):
        # Create a clean filename version of the keyword (replace spaces with underscores)
        keyword_filename = keyword.replace(" ", "_")

        # Create filename with today's date
        save_path = f'data/google_trends_monthly_au_{keyword_filename}_{today_str}.csv'

        print(f"\n{'-'*50}")
        print(f"Processing keyword {i+1}/{len(keywords_list)}: '{keyword}'")
        print(f"{'-'*50}")

        # --- Fetching monthly data for this keyword for all of Australia ---
        print(f"--- Fetching monthly Google Trends data for Australia ({'2014-02-01'} to {'2026-02-01'}) ---")
        print(f"Output will be saved to: {save_path}")

        monthly_au_df = get_google_trends_data(
            keywords=[keyword],  # Pass as a list with single element
            geo='AU',
            category=health_category_id,
            timeframe='2014-02-01 2026-02-01',
            save_path=save_path
        )

        print("\nMonthly Data Head:")
        print(monthly_au_df.head())
        print("\nMonthly Data Info:")
        monthly_au_df.info()

        print(f"\n--- Finished processing '{keyword}' ---")

        # Add delay before next API call
        time.sleep(delay_between_calls)

    print("\n=== All keywords processed successfully ===")
