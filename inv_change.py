import requests
import json
from sys import exit

CSGOEMPIRE_API_KEY = ""
PRICEMPIRE_API_KEY = ""


def main():
    #get inv from csgoempire
    inv = get_inventory()
    #get pricing data from pricempire
    pricing_data = get_pricing_data()
    #check if user wants to display all items or just negative percentage items
    display_all_data = input("Display just negative percentage items? (y/n): ").lower() == "n"
    #check if user wants to generate a json file
    generate_json = input("Generate JSON? (y/n): ").lower() == "y"
    # used to store data in case of json generation
    data = {}
    #loop through inventory
    for item in inv:
        #check if item is in pricing data and if it has the buff163_quick and buff163_quick_avg7 keys
        if item not in pricing_data or "buff163_quick" not in pricing_data[item] or "buff163_quick_avg7" not in pricing_data[item]:
            continue
        price = pricing_data[item]['buff163_quick']
        avg7 = pricing_data[item]['buff163_quick_avg7']
        #check if price and avg7 are not None (antal pls)
        if price is None or avg7 is None:
            continue
        #calculate percentage change
        percent_change = (price - avg7) / avg7 * 100
        #check if percentage change is negative or if user wants to display all items
        if percent_change < 0 or display_all_data:
            #print data
            print(f"{item} : delta: {avg7-price} : {percent_change:.2f}%")
            #add data to json dict
            if generate_json:
                data[item] = {"price": price, "avg7": avg7, "percent_change": percent_change}
    #write json file
    if generate_json and len(data) > 0:
        with open("inv_change.json", "w") as f:
            json.dump(data, f, indent=4)


def get_inventory():
    #get inventory from csgoempire
    r = requests.get("https://csgoempire.com/api/v2/trading/user/inventory?update=false", headers={'Authorization': f'Bearer {CSGOEMPIRE_API_KEY}', 'Content-Type': 'application/json'})
    status = r.status_code
    #check if status code is not 200, if so exit
    if status != 200:
        print(f"Error: {status}")
        exit(1)
    else:
        #parse json and return list of market names where market value is greater than 0 (used to filter out items not tradeable)
        response = r.json()
        return [item['market_name'] for item in response['data'] if item['market_value'] > 0]


def get_pricing_data():
    #get pricing data from pricempire
    r = requests.get(f"https://api.pricempire.com/v2/getAllItems?token={PRICEMPIRE_API_KEY}&source=buff163_quick,buff163_quick_avg7&currency=USD")
    status = r.status_code
    if status != 200:
        print(f"Error: {status}")
        exit(1)
    else:
        return r.json()


if __name__ == "__main__":
    main()
