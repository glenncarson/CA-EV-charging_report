import requests
import pandas as pd
from io import StringIO

todays_supply_url = 'https://www.caiso.com/outlook/SP/fuelsource.csv'


def get_todays_caiso_fuelsource_data(url):
    supply_response = requests.get(url)
    supply_data = supply_response.text
    return supply_data


def get_latest_energy_mix_from_todays_caiso_data(IOdata):
    try:
        todays_supply_df = pd.read_csv(IOdata).drop(columns=['Time'])
        assert len(todays_supply_df) > 0
        # to do. use a different method to pick the latest time rather than taking the last row
        latest_supply_df = todays_supply_df.tail(1)
    except AssertionError:
        print('An issue was detected with today\'s CAISO fuelsource data. No data was found.')
        raise RuntimeError("""An issue was detected with today\'s CAISO fuelsource data.
        No data was found. Is data being pulled correctly?""") from None
    latest_supply_dict = latest_supply_df.to_dict('records')[0]
    return latest_supply_dict




def calculate_clean_energy_percentage(energies_on_grid):
    clean_energies = ['Solar', 'Wind', 'Geothermal', 'Biomass', 'Biogas', 'Small hydro', 'Nuclear', 'Large Hydro', 'Batteries']
    # Nuclear, batteries, and large hydro are not necessarily renewable, but are forms of clean energy, so we include them.
    total_energy = 0
    clean_energy = 0
    for energy_type, value in energies_on_grid.items():
        total_energy += value
        if energy_type in clean_energies:
            clean_energy += value
    if total_energy <= 0:
        print(f'Total energy: {total_energy}')
        raise ValueError('Total energy on grid is not a positive number. Check input data.')
    pct_clean_energy: float = round(float(clean_energy)/total_energy, 3)*100
    return pct_clean_energy


def interpret_clean_energy_percentage(clean_energy_percentage):
    # report on whether user should charge their car
    try:
        assert isinstance(clean_energy_percentage, int) or isinstance(clean_energy_percentage, float)
    except AssertionError:
        raise TypeError("interpret_clean_energy_percentage function expects a number as input. A non-number was provided.") from None
    if clean_energy_percentage > 70:
        return "It's a perfect time to charge. The grid is very clean right now."
    elif clean_energy_percentage > 50:
        return "It's a decent time to charge."
    else:
        return("It's not an ideal time to charge. The grid is using dirty energy right now.")

def main():
    # grab today's energy mix in CA from CAISO
    todays_fuelsource_data = get_todays_caiso_fuelsource_data(todays_supply_url)
    # format text to stringIO for pandas input
    todays_fuelsource_csv_stringIO = StringIO(todays_fuelsource_data)
    # parse most recent energy type contributions
    live_energy_type_grid_contributions = get_latest_energy_mix_from_todays_caiso_data(todays_fuelsource_csv_stringIO)
    # determine percent of energy that is coming from clean and renewable sources
    clean_energy = calculate_clean_energy_percentage(live_energy_type_grid_contributions)
    print(f'The CA grid is currently comprised of {clean_energy}% clean energy.')
    grid_interpretation = interpret_clean_energy_percentage(clean_energy)
    print(grid_interpretation)


if __name__ == '__main__':
    main()


# to do: log which dependencies are needed in a readme (pandas, requests, pytest, responses, etc.)


