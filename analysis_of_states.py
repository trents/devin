"""
Analysis of States

This script processes four CSV files containing state-level data and produces an output CSV
that matches the OUTPUT tab in the Google Sheet.

Input files:
- CENSUS_MHI_STATE.csv: Median household income data by state
- CENSUS_POPULATION_STATE.csv: Population data by state
- KEYS.csv: State identifiers and mappings
- REDFIN_MEDIAN_SALE_PRICE.csv: Monthly median home sale prices by state

Output file:
- output.csv: Processed data matching the OUTPUT tab in the Google Sheet
"""

import pandas as pd
import numpy as np
import re

def clean_dollar_amount(value):
    """Convert dollar amounts like $131K to numeric values."""
    if pd.isna(value) or value == '':
        return np.nan
    
    value = str(value).replace('$', '')
    if 'K' in value:
        value = float(value.replace('K', '')) * 1000
    else:
        value = float(value)
    
    return value

def extract_rank_suffix(value):
    """Extract the rank suffix (e.g., '1st', '2nd', '3rd', '4th') from a string."""
    if pd.isna(value) or value == '':
        return np.nan
    
    match = re.search(r'(\d+)(st|nd|rd|th)', str(value))
    if match:
        return match.group(0)
    return value

def main():
    keys_df = pd.read_csv('KEYS.csv', sep=',', header=0)
    census_mhi_df = pd.read_csv('CENSUS_MHI_STATE.csv', sep=',', header=0)
    census_pop_df = pd.read_csv('CENSUS_POPULATION_STATE.csv', sep='\t', header=0)
    redfin_df = pd.read_csv('REDFIN_MEDIAN_SALE_PRICE.csv', sep=',', header=1)
    
    keys_df.columns = [col.strip() for col in keys_df.columns]
    
    state_keys = keys_df[keys_df['key_row'] != 'united_states'].copy()
    
    output_df = pd.DataFrame()
    output_df['key_row'] = state_keys['key_row']
    
    pop_data = {}
    
    for _, row in state_keys.iterrows():
        state_name = row['alternative_name']
        key_row = row['key_row']
        
        if pd.isna(state_name):
            continue
            
        state_name = str(state_name)
        pop_col = f"{state_name}!!Estimate"
        
        if pop_col in census_pop_df.columns:
            total_pop = census_pop_df.loc[1, pop_col]  # Row 1 (index 1) contains Total population
            if pd.notna(total_pop) and total_pop != '':
                try:
                    if total_pop == '*****':  # Special case for census data
                        continue
                    pop_data[key_row] = float(str(total_pop).replace(',', ''))
                except (ValueError, TypeError):
                    continue
    
    output_df['census_population'] = output_df['key_row'].map(pop_data)
    
    output_df = output_df[output_df['census_population'].notna()]
    
    output_df['population_rank'] = output_df['census_population'].rank(ascending=False, method='min')
    output_df['population_rank'] = output_df['population_rank'].fillna(0).astype(int).astype(str)
    output_df['population_rank'] = output_df['population_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['population_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['population_rank']} in the nation in population among states, DC, and Puerto Rico.", axis=1
    )
    
    mhi_data = {}
    
    for col in census_mhi_df.columns[1:]:
        if '!!Median income (dollars)!!Estimate' in col:
            state_name = col.split('!!')[0]
            if state_name in state_keys['alternative_name'].values:
                median_income = census_mhi_df.loc[1, col]  # Row 2 (index 1) contains Households median income
                if pd.notna(median_income) and median_income != '':
                    key_row = state_keys[state_keys['alternative_name'] == state_name]['key_row'].values[0]
                    try:
                        mhi_data[key_row] = float(median_income)
                    except (ValueError, TypeError):
                        mhi_data[key_row] = float(str(median_income).replace(',', ''))
    
    output_df['median_household_income_numeric'] = output_df['key_row'].map(mhi_data)
    
    output_df['median_household_income'] = output_df['median_household_income_numeric'].apply(
        lambda x: f"${int(x):,}" if pd.notna(x) else ""
    )
    
    output_df['median_household_income_rank'] = output_df['median_household_income_numeric'].rank(ascending=False, method='min')
    output_df['median_household_income_rank'] = output_df['median_household_income_rank'].fillna(0).astype(int).astype(str)
    output_df['median_household_income_rank'] = output_df['median_household_income_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['median_household_income_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['median_household_income_rank']}", axis=1
    )
    
    redfin_df.columns = [col.strip() for col in redfin_df.columns]
    
    latest_month = 'July 2013'
    
    state_name_to_key = {}
    for _, row in state_keys.iterrows():
        state_name = row['alternative_name']
        key_row = row['key_row']
        state_name_to_key[state_name] = key_row
    
    median_sale_price_data = {}
    
    for _, row in redfin_df.iterrows():
        region = row['Region']
        if region in state_keys['alternative_name'].values:
            key_row = state_keys[state_keys['alternative_name'] == region]['key_row'].values[0]
            if latest_month in redfin_df.columns and pd.notna(row[latest_month]) and row[latest_month] != '':
                median_sale_price_data[key_row] = clean_dollar_amount(row[latest_month])
    
    output_df['median_sale_price'] = output_df['key_row'].map(median_sale_price_data)
    
    output_df['median_sale_price_formatted'] = output_df['median_sale_price'].apply(
        lambda x: f"${int(x):,}" if pd.notna(x) else ""
    )
    
    output_df['median_sale_price_rank'] = output_df['median_sale_price'].rank(ascending=False, method='min')
    output_df['median_sale_price_rank'] = output_df['median_sale_price_rank'].fillna(0).astype(int).astype(str)
    output_df['median_sale_price_rank'] = output_df['median_sale_price_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['median_sale_price_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} has the {row['median_sale_price_rank']} highest median sale price on the list", axis=1
    )
    
    output_df['house_affordability_ratio'] = output_df['median_household_income_numeric'] / output_df['median_sale_price']
    
    output_df['house_affordability_ratio'] = output_df['house_affordability_ratio'].round(1)
    
    output_df['house_affordability_rank'] = output_df['house_affordability_ratio'].rank(ascending=False, method='min')
    output_df['house_affordability_rank'] = output_df['house_affordability_rank'].fillna(0).astype(int).astype(str)
    output_df['house_affordability_rank'] = output_df['house_affordability_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['house_affordability_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['house_affordability_rank']} most affordable", axis=1
    )
    
    output_df['census_population'] = output_df['census_population'].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else ""
    )
    
    final_columns = [
        'key_row',
        'census_population',
        'population_rank',
        'population_blurb',
        'median_household_income',
        'median_household_income_rank',
        'median_household_income_blurb',
        'median_sale_price_formatted',
        'median_sale_price_rank',
        'median_sale_price_blurb',
        'house_affordability_ratio',
        'house_affordability_rank',
        'house_affordability_blurb'
    ]
    
    
    output_df = output_df[output_df['census_population'].notna()]
    
    output_df['population_rank'] = output_df['census_population'].rank(ascending=False, method='min')
    output_df['population_rank'] = output_df['population_rank'].fillna(0).astype(int).astype(str)
    output_df['population_rank'] = output_df['population_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['population_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['population_rank']} in the nation in population among states, DC, and Puerto Rico.", axis=1
    )
    
    output_df['median_household_income_rank'] = output_df['median_household_income_numeric'].rank(ascending=False, method='min')
    output_df['median_household_income_rank'] = output_df['median_household_income_rank'].fillna(0).astype(int).astype(str)
    output_df['median_household_income_rank'] = output_df['median_household_income_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['median_household_income_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['median_household_income_rank']}", axis=1
    )
    
    output_df['median_sale_price_rank'] = output_df['median_sale_price'].rank(ascending=False, method='min')
    output_df['median_sale_price_rank'] = output_df['median_sale_price_rank'].fillna(0).astype(int).astype(str)
    output_df['median_sale_price_rank'] = output_df['median_sale_price_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['median_sale_price_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} has the {row['median_sale_price_rank']} highest median sale price on the list", axis=1
    )
    
    output_df['house_affordability_rank'] = output_df['house_affordability_ratio'].rank(ascending=False, method='min')
    output_df['house_affordability_rank'] = output_df['house_affordability_rank'].fillna(0).astype(int).astype(str)
    output_df['house_affordability_rank'] = output_df['house_affordability_rank'].apply(
        lambda x: x + ('st' if x.endswith('1') and not x.endswith('11') 
                      else 'nd' if x.endswith('2') and not x.endswith('12') 
                      else 'rd' if x.endswith('3') and not x.endswith('13') 
                      else 'th')
    )
    
    output_df['house_affordability_blurb'] = output_df.apply(
        lambda row: f"{row['key_row'].title().replace('_', ' ')} is {row['house_affordability_rank']} most affordable", axis=1
    )
    
    output_df = output_df[final_columns]
    
    output_df.to_csv('output.csv', index=False)
    
    print("Analysis complete. Output saved to output.csv")

if __name__ == "__main__":
    main()
