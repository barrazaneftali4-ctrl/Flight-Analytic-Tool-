import os
import requests
from datetime import datetime 
from dotenv import load_dotenv 

load_dotenv()

apiCode = os.getenv("DUFFEL_TOKEN")
url = "https://api.duffel.com/air/offer_requests"

a_head = {"Content-type": "application/json", 'Authorization': f"Bearer {apiCode}", 'Duffel-Version': 'v2',
}

def flytime(dur):
    t = dur.replace("PT", "").replace("P", "").replace("T", "")
    days = 0
    if "D" in t: 
        pts = t.split("D")
        days = int(pts[0])
        t = pts[1]

    hours = 0

    if "H" in t: 
        pts = t.split("H")
        hours = int(pts[0])
        t = pts[1]
    
    minut = 0

    if "M" in t: 
        minut = int(t.replace("M", ""))

    total_hours = (days * 24) + hours
    return f"{total_hours}h {minut}m" 

print("Welcome to your Flight Tracker")
flyout = input("From? (Use the airport 3 letter code ORD) ").upper().strip()
flyto = input("To?  (airport 3 letter code, ex: JFK): ").upper().strip()
dep_date = input("What's your Departure Date? (YYYY-MM-DD): ").strip()
ret_date = input("What's your Return Date? (YYYY-MM-DD) press Enter for One-Way: ").strip() 

print("\nAvailable classes: (economy, premium_economy, business, first)")
choice = input("Choose Class Seat (default: economy): ").lower().strip().replace(" ", "_")
if choice == "": 
    seat = "economy"
else: 
    seat = choice 

budget = float(input("How much do you want to pay (ex:, 500): "))


routes = [{"departure": flyout, "destination": flyto, "departure_date": dep_date}]
if ret_date: 
    routes.append({"departure": flyto, "destination": flyout, "departure_date": ret_date})

payload = {
    "data": {
        "slices": [
            {
                "origin": r["departure"],
                "destination": r["destination"],
                "departure_date":r["departure_date"]
                }
            for r in routes 
        ],
        "passengers": [{"type": "adult"}], 
        "cabin_class": seat
    }
}

print(f"\nSearching for flights from {flyout} to {flyto}...")

response = requests.post(url, headers=a_head, json=payload, params={"return_offers": "true"})
result = response.json()

if response.status_code == 201:
    offers = result.get("data", {}).get("offers", [])
    offers.sort(key=lambda x: float(x['total_amount']))
    
    print(f"\nFound {len(offers)} offers. Filtering for budget: ${budget}\n")


    same_flights = {} 

    for offer in offers:
        leaving = offer['slices'][0]['segments'][0]['departing_at'] 
        takeoff = datetime.fromisoformat(leaving).strftime("%I:%M %p")

        if len(offer['slices']) > 1: 
            home_trip = offer['slices'][1]['segments'][0]['departing_at']
            home_time = datetime.fromisoformat(home_trip).strftime("%I:%M %p")
            grp_key = f" Out: {takeoff} |  Return: {home_time}"
        else: 
            grp_key = f" One Way: {takeoff}"

        if grp_key not in same_flights: 
            same_flights[grp_key] = []
        same_flights[grp_key].append(offer)

    found_budget = False 

    for label, offers in same_flights.items(): 

        offers.sort(key=lambda x: float(x["total_amount"]))
        cheapest = float(offers[0]["total_amount"]) 

        if cheapest <= budget:
            found_budget = True
            best = offers[0]

            print(f"\n{label}")

            out = best['slices'][0]
            dep = datetime.fromisoformat(out['segments'][0]['departing_at']).strftime("%I:%M %p")
            arr = datetime.fromisoformat(out['segments'][-1]['arriving_at']).strftime("%I:%M %p")
            dur = flytime(out ['duration']) 
            print( f"DEPART: {dep} -> {arr} ({flyout} to {flyto}) | Duration: {dur}") 

            if len(best['slices']) > 1:
                back = best['slices'][1]
                start = back['segments'][0] 
                end = back['segments'][-1]
                ret_dep = datetime.fromisoformat(start['departing_at']).strftime("%I:%M %p")
                ret_arr = datetime.fromisoformat(end['arriving_at']).strftime("%I:%M %p")
                ret_dur = flytime(back['duration']) 
                print(f"RETURN: {ret_dep} -> {ret_arr} ({flyto} to {flyout}) | Duration: {ret_dur} ")

            for o in offers:
                p = float(o['total_amount'])
                if p <= budget:
                    marketing = o['owner']['name']
                    airline  = o['slices'][0]['segments'][0].get('operating_carrier',{}).get('name',marketing)

                    name = f"{marketing}"
                    if marketing != airline:
                        name += f" (Opertated by {airline})"

                    print(f"      FOUND:   Total: ${p:.2f} via {name}")

            print("-" * 50)

        if not found_budget:
            print(f"\n No flights under  ${budget}. Try a higher budget or different dates." )
else: 
    print(f"\n Error: {response.status_code}")

    if isinstance(result, dict) and 'errors' in result: 
        messg = result['errors'][0]['message']
        print(f" Error: {messg}") 
    else: 
        print(result)
