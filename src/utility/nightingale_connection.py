from os import getenv
from requests import post, get
from datetime import datetime
import json
class NightingaleConnection(): 
    """
        This class is used to connect to the Nightingale API
    """
    def __init__(self):
        """Intilaizes the class, generating header, bearer token and fetching the endpoint from the env file
           
        Instance Variables
            endpoint:           String containing the value of the base url
            token:              String containing the Bearer token
            headers:            Object containing Content-Type, and authorization
        """
        self.endpoint = getenv("NIGHTINGALE_ENDPOINT")
        self.token = self.generate_token()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer {}".format(self.token)
        }
    
    def generate_token(self):
        """
            Calls the Nightingale API with the username and password 
            to get a Bearer token. 
        """
        url = "{}/{}/".format(self.endpoint, "token")
        data = {
            "email": getenv("NIGHTINGALE_USERNAME"),
            "password": getenv("NIGHTINGALE_PASSWORD")
        }

        response = post(url=url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        response.encoding = "utf-8"

        # status code 200 means the token got created
        if response.status_code == 200:
            data = response.json()['results'][0]
            return data['access']
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else:
            print("Something Went Wrong Generating Token: {}".format(response.json()['response_message']))


    def create_course_index(self, course, index_code):
        """
            Creates a index for the particular course, through the Nightingale API
        """
        url = "{}/{}/".format(self.endpoint, "indices")
        data = {
            "index_code": index_code,
            "name": course["name"],
            "name_local": course["name"],
            "description": course["description"],
            "description_local": course["description"],
            "visibility_id": 4
        }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        
        # statuscode 201 means Created
        if response.status_code == 201: 
            data = response.json()['results'][0]
            print("Successfully Created index for course: {}".format(data['name']))
            return data['id']
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
            raise ValueError("500 server error")
        else:
            raise ValueError("Something Went Wrong Creating index {}".format(response.json()['response_message']))

    def create_company_index(self, name, description, index_code, parent_id):
        """
            Creates a index for the particular company under a specific course, through the Nightingale API
        """ 
        url = "{}/{}/".format(self.endpoint, "indices")
        data = {
            "index_code": index_code,
            "name": name,
            "name_local": name,
            "description": description,
            "description_local": description,
            "visibility_id": 4,
            "parent_index_connections": [{
                "parent_index_id": parent_id,
                "percentage": None
            }]
        }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        
        # statuscode 201 means Created
        if response.status_code == 201: 
            data = response.json()['results'][0]
            print("Successfully Created index for company: {}".format(data['name']))
            return data['id']
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else: 
            print("Something Went Wrong Creating index {}".format(response.json()['response_message']))

    def create_measurement(self, name, description, index_code, parent_id, assigned, finished):
        """
            Creates a measurement for the particular departmend under a specific company that is 
            under a specific course, through the Nightingale API
        """ 
        url = "{}/{}/".format(self.endpoint, "measurements")
        data = {
            "measurement_code": index_code,
            "name": name,
            "name_local": name,
            "description": description,
            "description_local": description,
            "min_value": 0,
            "max_value": 100,
            "min_better_value": False,
            "visibility_id": 4,
            "index_connections": [{
                "index_id": parent_id,
                "percentage": None
            }],
            "measurement_values": [{
                "date": datetime.today().strftime('%Y-%m-%dT%H:%M:%S'),
                "value": (finished/assigned)*100,
                "comment": "min: {} max(Fjöldi starfsmanna skráð á námskeiðið): {} Fjöldi klárað: {}".format(0, assigned, finished)
            }]
        }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        
        # statuscode 201 means Created
        if response.status_code == 201: 
            data = response.json()['results'][0]
            print("Successfully Created measurement for department: {}".format(data['name']))
            return data['id']
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else: 
            print("Something Went Wrong Creating department measurement {}".format(response.json()['response_message']))

    def create_measurement_value(self, measurement_id, assigned, finished):
        """
            This is used when a measurement already exists. 
            This method creates a new measurement value for a specific measurement
        """
        url = "{}/{}/".format(self.endpoint, "measurement-values")
        data = {
            "date": datetime.today().strftime('%Y-%m-%dT%H:%M:%S'),
            "value": (finished/assigned)*100,
            "measurement_id": measurement_id,
            "comment": "min: {} max(Fjöldi starfsmanna skráð á námskeiðið): {} Fjöldi klárað: {}".format(0, assigned, finished)
            }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        
        # statuscode 201 means Created
        if response.status_code == 201: 
            data = response.json()['results'][0]
            print("Successfully Created measurement value: {}".format(data['id']))
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else: 
            print("Something Went Wrong Creating measurement value {}".format(response.json()['response_message']))

    def create_measurement_index_connection(self, measurement_id, index_id):
        """
            This method creates a connection between a measurement and index
        """
        url = "{}/{}/".format(self.endpoint, "index-measurement-connections")
        data = {
                "percentage": None,
                "index_id": index_id,
                "measurement_id": measurement_id
            }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        
        # statuscode 201 means Created
        if response.status_code == 201: 
            data = response.json()['results'][0]
            print("Successfully Created Connection Betweeon {} and {}".format(measurement_id, index_id))
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else:
            print(response.text)
            print("Something Went Wrong Creating A Connection Between {} and {}".format(measurement_id, index_id))

    def get_indices(self):
        """
            Fetches all the indices from the Nightingale API
        """
        url = "{}/{}/?page_size=0".format(self.endpoint, "indices")

        response = get(url=url, headers=self.headers)
        response.encoding = "utf-8"

        # statuscode 200 means the query was successful
        if response.status_code == 200: 
            data = response.json()['results']
            mapped_data = { x['index_code']: x for x in data }
            return mapped_data
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
            raise ValueError(response.text)
        else:
            raise ValueError("Something Went Wrong Fetching The Indices {}".format(response.json()['response_message']))

    def get_measurements(self):
        """
            Fetches all the measurements from the Nightingale API
        """
        url = "{}/{}/?page_size=0".format(self.endpoint, "measurements")

        response = get(url=url, headers=self.headers)
        response.encoding = "utf-8"

        # statuscode 200 means the query was successful
        if response.status_code == 200: 
            data = response.json()['results']
            mapped_data = { x['measurement_code']: x for x in data }
            return mapped_data
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
        else:
            print("Something Went Wrong Fetching The Measurements {}".format(response.json()['response_message']))

    def get_measurement_by_code(self, code): 
        """Gets all the measurements that have the code included in them

        Args:
            code (Str): index_code in NightinGale
        """
        url = "{}/{}/?code={}".format(self.endpoint, "measurements", code)
        response = get(url=url, headers=self.headers)
        response.encoding = "utf-8"

        # statuscode 200 means the query was successful
        if response.status_code == 200: 
            data = response.json()['results']
            return data
        # 500, server error, and it has a different format than other responses
        elif response.status_code == 500:
            print(response.text)
            raise ValueError(response.text)
        else:
            raise ValueError("Something Went Wrong Fetching The Measurements by code {}".format(response.json()['response_message']))