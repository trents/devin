# Analysis of States

This repository contains a Python script that processes state-level data from various CSV files and produces an output CSV file that matches the OUTPUT tab in the [Analysis of States Google Sheet](https://docs.google.com/spreadsheets/d/17A-cyV7phkYCC0raTWt11iHNJJq17l4tgkb3o4xHTHs/edit?gid=367797968).

## Files

- `analysis_of_states.py`: Python script that processes the input CSV files and generates the output
- `KEYS.csv`: Contains state identifiers and mappings
- `CENSUS_MHI_STATE.csv`: Contains median household income data by state
- `CENSUS_POPULATION_STATE.csv`: Contains population data by state
- `REDFIN_MEDIAN_SALE_PRICE.csv`: Contains monthly median home sale prices by state
- `output.csv`: Generated output file that matches the OUTPUT tab in the Google Sheet

## How It Works

The script performs the following operations:

1. **Data Loading**: Reads the four input CSV files, handling different delimiters for each file.
2. **Population Data**: Extracts total population for each state from the census data.
3. **Median Household Income**: Extracts median household income for each state.
4. **Median Sale Price**: Extracts median sale prices for each state from the Redfin data.
5. **Ranking**: Calculates rankings for population, median household income, and median sale price.
6. **House Affordability Ratio**: Calculates the ratio of median household income to median sale price.
7. **Descriptive Blurbs**: Generates descriptive text for each state based on the calculated metrics.
8. **Output Generation**: Formats the data and saves it to `output.csv`.

## Metrics Calculated

- **Census Population**: Total population for each state
- **Population Rank**: Ranking of states by population (1st = highest population)
- **Median Household Income**: Median household income for each state
- **Median Household Income Rank**: Ranking of states by median household income (1st = highest income)
- **Median Sale Price**: Median home sale price for each state
- **Median Sale Price Rank**: Ranking of states by median sale price (1st = highest price)
- **House Affordability Ratio**: Ratio of median household income to median sale price
- **House Affordability Rank**: Ranking of states by house affordability (1st = most affordable)

## Running the Script

To run the script, ensure you have Python installed with the pandas and numpy libraries, then execute:

```bash
python analysis_of_states.py
```

The script will process the input CSV files and generate `output.csv` in the same directory.
