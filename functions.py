import requests
import datetime
from datetime import datetime as dt
import numpy as np

# Set variables 
base_url = 'https://www.buda.com/api/v2'
now = datetime.datetime.now()
unixtime_now = int(datetime.datetime.timestamp(now)*1000)
last_24_hours =  unixtime_now - (24*60*60*1000)
# last_hour =  unixtime_now - (60*60*1000)


# Get list of market ids
def get_markets():
    response = requests.get(f"{base_url}/markets")
    result = response.json()['markets']
    markets_ids = [d['id'].lower() for d in result]
    return markets_ids

# Get first entries and timestampt to evaluate by market
def get_first_latest_timestamp(market_id):
    response = requests.get(f"{base_url}/markets/{market_id}/trades", params={
    'limit': 100,
    })
    return (int(response.json()['trades']['last_timestamp']), response.json()['trades']['entries'])


# Get array of the last 24hrs transactions by market
def get_last_24_hours_transactions(market_id):

    timestamp, entries = get_first_latest_timestamp(market_id)

    while timestamp > last_24_hours:
        response = requests.get(f"{base_url}/markets/{market_id}/trades", params={
        'timestamp': timestamp, 
        'limit': 100,
        })
        new_entries = response.json()['trades']['entries']
        entries.extend(new_entries)
        timestamp = int(response.json()['trades']['last_timestamp'])

    return entries


def get_bigger_transaction(entries):
    filtered_entries = [x for x in entries if int(x[0]) >= last_24_hours]
    
    if len(filtered_entries) > 0:
        transaction_values = [float(x[1]) * float(x[2]) for x in filtered_entries]

        max_index = transaction_values.index(max(transaction_values, default=0))
        max_transaction = filtered_entries[max_index]

        return max_transaction
    return []


def main():
    markets = get_markets()
    transactions_by_market = []

    for market_id in markets:

        entries = get_last_24_hours_transactions(market_id)
        biggest_transaction = get_bigger_transaction(entries)

        if (len(biggest_transaction) > 0):
            transactions_by_market.append({
                "time": dt.fromtimestamp(int(biggest_transaction[0])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                "market": market_id,
                "amount":biggest_transaction[1],
                "price": biggest_transaction[2],
                "value": float(biggest_transaction[1]) * float(biggest_transaction[2]),
                "direction": biggest_transaction[3]
            })
        else: 
             transactions_by_market.append({
                "time": None,
                "market": market_id,
                "amount":None,
                "price": None,
                "value": None,
                "direction": None
            })

    return transactions_by_market
