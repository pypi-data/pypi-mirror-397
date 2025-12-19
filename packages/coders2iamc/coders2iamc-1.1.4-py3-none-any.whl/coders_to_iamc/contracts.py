import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'from_balancing_area': 'Contract|Start Node|',
    'to_balancing_area': 'Contract|End Node|',
    'start_year': 'Contract|Start Year|',
    'possible_renewal_year': 'Contract|End Year|',
    'contract_effective_capacity': 'Contract|Capacity|',
    'capacity_factor': 'Contract|Capacity Factor|',
    'contract_average_annual_energy': 'Contract|Annual Energy|',
}



def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/contracts?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['contract_name', 'from_balancing_area', 'to_balancing_area', 'start_year', 
         'possible_renewal_year', 'contract_effective_capacity', 'contract_average_annual_energy',
         'capacity_factor', 'from_country']]
    melted = modeled_attributes.melt(id_vars=['contract_name', 'from_country'], var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['contract_name'].astype(str)
    melted = melted.drop(columns=['contract_name'])
    melted.rename(columns={'from_country': 'region'}, inplace=True)
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)

