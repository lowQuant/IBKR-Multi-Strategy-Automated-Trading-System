# helper_functions.py
from dotenv import load_dotenv
load_dotenv()

import configparser, os
from supabase import create_client

def get_strategy_details_from_ini(strategy_id):
        config = configparser.ConfigParser()
        config.read('settings.ini')

        strategy_section = f"Strategy{strategy_id}"
        if strategy_section in config:
            strategy_name = config[strategy_section].get('name', '')
            strategy_symbol = config[strategy_section].get('symbol', '')
            strategy_description = config[strategy_section].get('description', '')
            strategy_allocation = config[strategy_section].get('allocation', '')

            # Create a dictionary with strategy details
            strategy_details = {
                "id": strategy_id,
                "name": strategy_name,
                "description": strategy_description,
                "target_weight": float(strategy_allocation),
                "min_weight": float(strategy_allocation)*0.8,
                "max_weight":float(strategy_allocation)*1.2,
                # Add more fields as necessary
            }
            return strategy_details
        else:
            # Handle the case where the strategy does not exist in settings.ini
            print(f"Strategy with ID {strategy_id} not found in settings.ini.")
            return None
        
def initialize_strategy_in_supabase(strategy_id):
    '''This function creates a supabase entry for the strategy created'''
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    # Load strategy details from settings.ini
    strategy_details = get_strategy_details_from_ini(strategy_id)

    # Check if the strategy exists in Supabase
    strategies_table = supabase.table("strategies")
    strategy_data = strategies_table.select("*").eq("id", strategy_id).execute()

    if not strategy_data.data:
        # If strategy does not exist, insert it into Supabase
        response = strategies_table.insert(strategy_details).execute()
        print(f"Strategy {strategy_details['name']} added to Supabase.")
    else:
        strategies_table.update(strategy_details).eq("id", strategy_id).execute()
        print(f"Strategy {strategy_details['name']} parameters updated in Supabase.")

def delete_strategy_from_supabase(strategy_id):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)

    # Delete the strategy from the 'strategies' table
    supabase.table("strategies").delete().eq("id", strategy_id).execute()
    print(f"Strategy with ID {strategy_id} deleted successfully from Supabase.")

