# from src.LLM.llama import load_model
# from src.login import logger
import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd






class EIN_LOOKUP:
    def __init__(self,ein:int):
        self._ein = ein
        self._FFILIST = os.path.join('artifacts','FFIListFull.csv')
        self._sdn = os.path.join('artifacts','sdn.csv')


    def einlookup(self):
        try:
            # Define the request URL and headers
            url = "https://eintaxid.com/search-ajax.php"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }

            # Payload with EIN query
            data = {
                "query": str(self._ein)
            }

            # Make a POST request
            response = requests.post(url, data=data, headers=headers)

            # Parse the response HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            panel_body = soup.find('div', class_='panel-body fixed-panel')

            # Check if panel_body exists
            if not panel_body:
                return None

            # Extract required fields safely
            returndata = {
                "company_name": (panel_body.find('a').text.strip() 
                                if panel_body.find('a') else "N/A"),
                "ein_number": (panel_body.find('strong').text.strip().split(":")[-1].strip() 
                            if panel_body.find('strong') else "N/A"),
                "Doing_Business_As": (panel_body.find('strong', text='Doing Business As: ').find_next_sibling().text.strip()
                                    if panel_body.find('strong', text='Doing Business As: ') else "N/A"),
                "address": (panel_body.find('strong', text='Address: ').next_sibling.strip()
                            if panel_body.find('strong', text='Address: ') else "N/A"),
                "phone": (panel_body.find('strong', text='Phone: ').next_sibling.strip()
                        if panel_body.find('strong', text='Phone: ') else "N/A")
            }

            # Return the JSON-encoded result
            return json.dumps(returndata, indent=4)

        # except requests.exceptions.RequestException as req_err:
        #     # Handle network-related errors
        #     return json.dumps({"error": f"Request error occurred: {req_err}"})

        except Exception as e:
            # Catch all other exceptions
            print(f"error in einlookup function and error is {e}")
            return None
            # return json.dumps({"error": f"An error occurred: {str(e)}"})
           








    # def einlookup(self):

    #     try:


    #         url = "https://eintaxid.com/search-ajax.php" 
    #         headers = {
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    #         }

            
    #         data = {
    #             "query": str(self._ein)
    #         }

    #         logger.info(f"Checking ein details")

    #         # Send POST request
    #         response = requests.post(url, data=data, headers=headers)
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         panel_body = soup.find('div', class_='panel-body fixed-panel')
    #         returndata = {
    #         "company_name" : panel_body.find('a').text.strip(),
    #         "ein_number" : panel_body.find('strong').text.strip().split(":")[-1].strip(),
    #         "Doing_Business_As" : panel_body.find('strong', text='Doing Business As: ').find_next_sibling().text.strip(),
    #         "address" : panel_body.find('strong', text='Address: ').next_sibling.strip(),
    #         "phone" : panel_body.find('strong', text='Phone: ').next_sibling.strip()

    #             }
            
    #         return json.dumps(returndata)   

    #     except Exception as e:
    #         logger.error(f"Error in function einlookup and error is : {e} ")




    def fatcacheck(self,business_name) -> str:
        """ 
        
        
        """
        try:
          print("fatca chechecking")

          df_ffi= pd.read_csv(self._FFILIST)
          exists = business_name in df_ffi['FINm'].values
          if exists:
              print(f"fatca is Compliant")
              return "Compliant"
              
          else:
              print(f"fatca is Not Compliant")
              return "Not Compliant"

        except Exception as e:
            print(f"Error in function fatcacheck and error is {e}")  




    def Sanctions_Blacklist_Check(self,business_name):   

        try:
            print("Sanctions Blacklist chechecking")

            df_sdn= pd.read_csv(self._sdn,header=None)
            exists = business_name in df_sdn[1].values
            if exists:
                print(f"Blacklist")
                return "Blacklist"
            else:
                print(f"Not Blacklist")
                return "Not Blacklist"

        except Exception as e:
            print(f"Error in function Sanctions_Blacklist_Check and error is {e}")  



    def return_validation_json(self):
        try:

            ein_details_json = self.einlookup()
            if ein_details_json is not None:
                business = json.loads(ein_details_json) 
                print(business)
            
                fatca= self.fatcacheck(business['company_name'])   
                blacklist = self.Sanctions_Blacklist_Check(fatca)   

                business['fatca_comliant'] = fatca  # Compliant or not Compliant
                business['blacklist'] = blacklist # Blacklist or not Blacklist

                data = json.dumps(business,indent=4)
                return data
            else:
                return None

        except Exception as e:
            print(f"Error is {e}")    





    



        
        
