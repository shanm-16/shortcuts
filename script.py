import argparse
import requests
import random
import json
from datetime import datetime
import time

# Create the argument parser
parser = argparse.ArgumentParser(description='Simple Command-Line App with Arguments')

baseUrl_app = 'http://localhost:8013/v2'
baseURL_namma_P = 'http://localhost:8016/ui'

# Add required arguments
parser.add_argument('-nd', type=int, help='Phone number',default="6666666666")
parser.add_argument('-nc', type=int, help='Phone number',default="7777777778")
parser.add_argument('-slat', type=float, help='Source latitute',default="12.846907")
parser.add_argument('-slon', type=float, help='Source longitude',default="77.556936")
parser.add_argument('-dlat', type=float, help='Destination latitude',default="12.846907")
parser.add_argument('-dlon', type=float, help='Destination longitude',default="77.566936")

parser.add_argument('--operation', choices=['make-driver','ride-flow'], help='Operation to perform')
parser.add_argument('--flow',type=int,help='upto what level you want to see output')

# Add optional argument
parser.add_argument('-v', action='store_true', help='Display verbose output', default=False)

# Parse the arguments
args = parser.parse_args()

def search_request_for_driver(driver_token):
    nearby_ride_request = requests.get(f'{baseURL_namma_P}/driver/nearbyRideRequest',headers={'token':driver_token})
    print()
    print("nearby ride request ",json.dumps(nearby_ride_request.json(),indent=4))
    return nearby_ride_request.json()

def auth_driver(driver_phone_number):
    auth_body = {
        "mobileNumber": str(driver_phone_number),
        "mobileCountryCode": "+91",
        "merchantId": "favorit0-0000-0000-0000-00000favorit"
        }
    auth_driver_response = requests.post(baseURL_namma_P + "/auth",json=auth_body)
    print()
    print("authenticating driver",json.dumps(auth_driver_response.json(),indent=4))
    return auth_driver_response
    

def ride_flow(driver_phone_number,customer_phone_number,source_address,destination_address):
    
    auth_driver_response = auth_driver(driver_phone_number)
    verify_body = {
            "otp": "7891",
            "deviceToken": "8e83b5dc-99a0-4306-b90d-2345f3050972"
        }
    
    verify_driver_response = requests.post(f'{baseURL_namma_P}/auth/{auth_driver_response.json()["authId"]}/verify',json=verify_body)
    print()
    print("verifying driver",json.dumps(verify_driver_response.json(),indent=4))
    driver_token = verify_driver_response.json()["token"]

    activity_driver_response = requests.post(f'{baseURL_namma_P}/driver/setActivity?active=true',headers={'token' : driver_token})

    print()
    print("setting activity driver",json.dumps(activity_driver_response.json(),indent=4))
    now_utc = datetime.utcnow()
    formatted_datetime = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    set_driver_location = [
    {
        "pt": {
            "lat": source_address["lat"],
            "lon": source_address["lon"]
        },
        "ts": formatted_datetime
    }
    ]

    location_driver_response = requests.post(f'{baseURL_namma_P}/driver/location',headers={'token' : driver_token},json=set_driver_location)
    print()
    print("driver location ",json.dumps(location_driver_response.json(),indent=4))

    customer_auth_body = {
        "mobileNumber": str(customer_phone_number),
        "mobileCountryCode": "+91",
        "merchantId": "YATRI"
        }
    customer_auth = requests.post(f'{baseUrl_app}/auth',json=customer_auth_body)
    customer_auth_id = customer_auth.json()["authId"]
    print()
    print("customer auth ",json.dumps(customer_auth.json(),indent=4))

    customer_verify_body = {
        "otp": "7891",
        "deviceToken": "5497873d-10ca-42f3-8a32-22de4c916026"
    }

    customer_verify = requests.post(f'{baseUrl_app}/auth/{customer_auth_id}/verify',json=customer_verify_body)

    customer_token = customer_verify.json()["token"]

    print()
    print("customer verify ",json.dumps(customer_verify.json(),indent=4))

    ridesearch_body = {
    "fareProductType": "ONE_WAY",
    "contents": {
        "origin": {
            "address": {
                "area": "8th Block Koramangala",
                "areaCode": "560047",
                "building": "Juspay Buildings",
                "city": "Bangalore",
                "country": "India",
                "door": "#444",
                "street": "18th Main",
                "state": "Karnataka"
            },
            "gps": {
                "lat": source_address["lat"],
                "lon": source_address["lon"]
            }
        },
        "destination": {
            "address": {
                "area": "6th Block Koramangala",
                "areaCode": "560047",
                "building": "Juspay Apartments",
                "city": "Bangalore",
                "country": "India",
                "door": "#444",
                "street": "18th Main",
                "state": "Karnataka"
            },
            "gps": {
                "lat": destination_address["lat"],
                "lon": destination_address["lon"]
            }
        }
    }
}

    ridesearch = requests.post(f'{baseUrl_app}/rideSearch',json=ridesearch_body,headers={'token':customer_token})

    print()
    print("customer ridesearch ",json.dumps(ridesearch.json(),indent=4))

    searchId = ridesearch.json()["searchId"]
    time.sleep(3);
    ridesearch_results = requests.get(f'{baseUrl_app}/rideSearch/{searchId}/results',headers={'token':customer_token})

    print()
    print("search id results ",json.dumps(ridesearch_results.json(),indent=4))

    estimate_body = {
    "autoAssignEnabledV2": False,
    "autoAssignEnabled": False,
    "customerExtraFee": 1
    }
    estimateId = ridesearch_results.json()["estimates"][0]["id"]
    estimate_select = requests.post(f'{baseUrl_app}/estimate/{estimateId}/select2',json=estimate_body,headers={'token':customer_token})

    print()
    print("estimate select ",json.dumps(estimate_select.json(),indent=4))
    search_request_for_driver_response = search_request_for_driver(driver_token)

    driver_search_request_id =  search_request_for_driver_response["searchRequestsForDriver"][0]["searchRequestId"];
    quote_offer_body = {
        "searchRequestId": f"{driver_search_request_id}"
    }
    quote_offer = requests.post(f'{baseURL_namma_P}/driver/searchRequest/quote/offer',headers={'token':driver_token},json=quote_offer_body)
    print()
    print("quote offer ",json.dumps(quote_offer.json(),indent=4))

    quote_accept = requests.get(f'{baseUrl_app}/estimate/{estimateId}/quotes',headers={'token':customer_token})

    print()
    print("quote accept ",json.dumps(quote_accept.json(),indent=4))

    customer_quote_id =  quote_accept["selectedQuotes"][0]["id"]

    confirm_quote = requests.post(f'{baseUrl_app}/rideSearch/quotes/{customer_quote_id}/confirm',headers={'token':customer_token})
    customer_bookingId =  confirm_quote.bookingId

    ride_booking_list = requests.get(f'{baseUrl_app}/rideBooking/list?limit=20&onlyActive=true',headers={'token':customer_token})

    # to be continued

    # ride_otp =  bookings.rideList[0].rideOtp;
    # customer_ride_id = bookings.rideList[0].id;

def make_driver(phone_number,verbose):
    # getting admin token 
    print('making driver with phone number',phone_number)
    dashboard_token = "1460d294-8c69-44b9-811a-c370949d056e"
    auth_body = {
        "mobileNumber": "9999999999",
        "mobileCountryCode": "+91",
        "merchantId": "favorit0-0000-0000-0000-00000favorit"
        }
    
    x_admin = requests.post('http://localhost:8016/ui/auth',json=auth_body)

    if(verbose):
        print()
        print("authenticating admin",json.dumps(x_admin.json(),indent=4))

    auth_id_admin = x_admin.json()["authId"]

    verify_body = {
            "otp": "7891",
            "deviceToken": "8e83b5dc-99a0-4306-b90d-2345f3050972"
        }
    
    y_admin = requests.post(f'http://localhost:8016/ui/auth/{auth_id_admin}/verify',json=verify_body)
    
    if(verbose):
        print()
        print("verifying admin",json.dumps(y_admin.json(),indent=4))
    admin_token = y_admin.json()["token"]

    
    auth_body = {
        "mobileNumber": str(phone_number),
        "mobileCountryCode": "+91",
        "merchantId": "favorit0-0000-0000-0000-00000favorit"
        }
    x = requests.post('http://localhost:8016/ui/auth',json=auth_body)
    
    if(verbose):
        print()
        print("authenticating driver",json.dumps(x.json(),indent=4))
    auth_id = x.json()["authId"]
    verify_body = {
        "otp": "7891",
        "deviceToken": "8e83b5dc-99a0-4306-b90d-2345f3050972"
    }
    y = requests.post(f'http://localhost:8016/ui/auth/{auth_id}/verify',json=verify_body)
    # print(y.json())
    driverId = y.json()["person"]["id"]
    driver_token = y.json()["token"]
    token = admin_token
    # print(driver_id)
    if(verbose):
        print()
        print("verifying driver",json.dumps(y.json(),indent=4))
    
    z = requests.post(f'http://localhost:8016/ui/org/driver/{driverId}?enabled=true',headers={'token' : token})
    if(verbose):
        print()
        print("enabling driver",json.dumps(z.json(),indent=4))
    vehicle = {
        "variant": "AUTO_RICKSHAW",
        "color": "string",
        "size": "string",
        "vehicleClass": "3WT",
        "category": "CAR",
        "capacity": 5,
        "model": "string",
        "registrationNo": str(random.randint(1000,9999)),
        "registrationCategory": "COMMERCIAL",
        "make": "string",
        "colour": "ipsum",
        "energyType": "string",
        "driverName": "",
    }

    a = requests.post(f'http://localhost:8018/bpp/driver-offer/NAMMA_YATRI_PARTNER/driver/{driverId}/addVehicle',json=vehicle,headers={'token' : dashboard_token})
    if(verbose):
        print()
        print("addding vehicle",json.dumps(a.json(),indent=4))
    print("driver auth token is",driver_token)


    

# Perform operation based on input arguments
if args.operation == 'make-driver':
    result = make_driver(args.nd,args.v)
elif args.operation == 'ride-flow':
    ride_flow(args.nd,args.nc,{"lat" : args.slat,"lon": args.slon},{"lat" : args.dlat,"lon": args.dlon})

# Display the result
