import json
from backend.node.genvm.icontract import IContract
from backend.node.genvm.equivalence_principle import EquivalencePrinciple

# Flight Insurance Intelligent Contract is a contract that allows passengers to buy insurance for their flights.
# The contract is created by the insurance manager for specific flight 
# and the passengers can buy insurance for this specific flight.
# The contract has a method to check the flight status from an independent source of information
# and a method to claim the insurance in case the flight is delayed.
# The payment is done by the insurance manager to the passengers in case the flight is delayed.
# Passenger does not need to trust on the insurance manager to get the payment.
class FlightInsurance(IContract):

    def __init__(self, _flight_number: str, _flight_date: str, _flight_time: str, _flight_from: str, _flight_to: str, _num_passengers_paid_insurance: int, _insurance_value_per_passenger: int):
        self.flight_number = _flight_number
        self.num_passengers_paid_insurance = _num_passengers_paid_insurance
        self.flight_arrival_delayed = False
        self.flight_date = _flight_date
        self.flight_time = _flight_time
        self.flight_from = _flight_from
        self.flight_to = _flight_to
        self.resolution_url = "https://flightaware.com/live/flight/" + self.flight_number  + "/history/" 
        self.resolution_url = self.resolution_url + self.flight_date + "/" + self.flight_time + "/" 
        self.resolution_url = self.resolution_url + self.flight_from + "/" + self.flight_to
        self.loss_payment_value_per_passenger = _insurance_value_per_passenger
        self.balances = {}
        self.balances[contract_runner.from_address] = _num_passengers_paid_insurance*_insurance_value_per_passenger
        self.insurance_manager = contract_runner.from_address
    
    # Example of constructor with hardcoded values to save time in the testing
    # def __init__(self):
    #     self.flight_number = "TAP457"
    #     self.num_passengers_paid_insurance = 35
    #     self.flight_arrival_delayed = False
    #     self.flight_date = "20240818"
    #     self.flight_time = "0510Z"
    #     self.flight_from = "LFPO"
    #     self.flight_to = "LPPR"
    #     self.resolution_url = "https://flightaware.com/live/flight/" + self.flight_number  + "/history/" 
    #     self.resolution_url = self.resolution_url + self.flight_date + "/" + self.flight_time + "/" 
    #     self.resolution_url = self.resolution_url + self.flight_from + "/" + self.flight_to
    #     self.loss_payment_value_per_passenger = 30
    #     self.balances = {}
    #     self.balances[contract_runner.from_address] = self.loss_payment_value_per_passenger*self.loss_payment_value_per_passenger
    #     self.insurance_manager = contract_runner.from_address

    async def ask_for_flight_status(self) -> None:
        print("calling the page: " + self.resolution_url)
        final_result = {}
        async with EquivalencePrinciple(
            result=final_result,
            principle="The arrivalstatus should be the similar",
            comparative=True,
        ) as eq:
            web_data = await eq.get_webpage(self.resolution_url)
            print(" ")
            print("web_data: ")
            print(web_data)
            print(" ")
            print(" ")
            prompt = f"""
In the following web page, find if the flight arrival was late or not:
Web page content:
{web_data} 
End of web page data.
Respond using ONLY the following format:
{{
"arrivalstatus": bool // True if the flight arrival was delayed or False if it was on time
}}
It is mandatory that you respond only using the JSON format above,
nothing else. Don't include any other words or characters,
your output must be only JSON without any formatting prefix or suffix.
This result should be perfectly parseable by a JSON parser without errors.
"""
            result = await eq.call_llm(prompt)
            print("********************************")
            print("result: ")
            print(result)     
            print("================================")   
            result_clean = result.replace("True", "true").replace("False", "false")
            print("********************************")
            print("result_clean: ")
            print(result_clean)
            print("================================")   
            eq.set(result_clean)
            output = json.loads(result_clean)
            print("********************************")
            print("output: ")
            print(output["arrivalstatus"])
            print("================================")   
            if output["arrivalstatus"] is True:
                self.flight_arrival_delayed = True
                print("********************************")
                print("flight_arrival_delayed: ")
                print(self.flight_arrival_delayed)
                print("================================")
    
    def add_passenger(self, _passenger_address:str) ->None:
        self.balances[_passenger_address] = 0

    def insurance_claim(self, _passenger_address:str) ->None:
        if self.flight_arrival_delayed is True:
            if _passenger_address in self.balances:
              if self.balances[_passenger_address] == 0:
                self.balances[_passenger_address] = self.loss_payment_value_per_passenger
                self.balances[self.insurance_manager] = (self.balances[self.insurance_manager]-self.loss_payment_value_per_passenger)

    def get_flight_status(self) ->bool:
        return self.flight_arrival_delayed
    
    def get_insurance_balance(self, _passenger_address:str) ->int:
        if _passenger_address in self.balances:
            return self.balances[_passenger_address]
        else:
            return 0

    def get_insurance_manager_balance(self) ->int:
        return self.balances[self.insurance_manager]
      
    def get_insurance_manager(self) ->str:
        return self.insurance_manager
      
    def get_flight_number(self) ->str:
        return self.flight_number
    
    def get_flight_date(self) ->str:
        return self.flight_date
    
    def get_flight_time(self) ->str:
        return self.flight_time
      
    def get_flight_from(self) ->str:
        return self.flight_from
      
    def get_flight_to(self) ->str:
        return self.flight_to
      
    def get_resolution_url(self) ->str:
        return self.resolution_url
      
    def get_loss_payment_value_per_passenger(self) ->int:
        return self.loss_payment_value_per_passenger
      
    def get_num_passengers_paid_insurance(self) ->int:
        return self.num_passengers_paid_insurance