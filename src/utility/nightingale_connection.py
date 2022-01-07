import json
import logging
from os import getenv, truncate, uname_result
from requests import NullHandler, post, get
from datetime import datetime

from requests.api import head
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
        self.logger = logging.getLogger(__name__)
    
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
    
    def get_indices_by_code(self, code): 
        """Gets all the indices that have the code included in them

        Args:
            code (Str): index_code in NightinGale
        """
        url = "{}/{}/?page_size=0&code={}".format(self.endpoint, "indices", code)
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

    def get_measurements_by_code(self, code): 
        """Gets all the measurements that have the code included in them

        Args:
            code (Str): index_code in NightinGale
        """
        url = "{}/{}/?page_size=0&code={}".format(self.endpoint, "measurements", code)
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
    
    def create_combination_index(self, index_code, children, name, description):
        """
            creates a index, that combines multiple measures
        """
        url = "{}/{}/".format(self.endpoint, "indices")
        data = {
            "index_code": index_code,
            "name": name,
            "name_local": name,
            "description": description,
            "description_local": description,
            "visibility_id": 4,
            "measurement_connections": [{"measurement_id": x, "percentage": None} for x in children]
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
    
    def create_combination_index_index(self, index_code, children, name, description):
        """
            creates a index, that combines multiple indices
        """
        url = "{}/{}/".format(self.endpoint, "indices")
        data = {
            "index_code": index_code,
            "name": name,
            "name_local": name,
            "description": description,
            "description_local": description,
            "visibility_id": 4,
            "child_index_connections": [{"child_index_id": x, "percentage": None} for x in children]
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

    def get_departments(self):
        """Gets all the departments from Nightingale

        Raises:
            ValueError: [description]
            ValueError: [description]
        """
        url = "{}/{}/?page_size=0".format(self.endpoint, "departments")
        response = get(url=url, headers=self.headers)

        response.encoding = "utf-8"
        if response.status_code == 200:
            data = response.json()["results"]
            self.logger.info("Successfully fetched all departments {}".format(data))
            return data
        elif response.status_code == 500:
            self.logger.error("Server error 500, failed on getting departments")
            self.logger.error("Response: {}".format(response.text))
            raise ValueError("500 server error check logs for details")
        else:
            self.logger.error("Unknown error on getting departments")
            self.logger.error(response.text)
            raise ValueError("Unknown error check logs for details")

    def create_department(self, entity_id, name, general_ledger_number = None, head_department_id = None, 
                          head_department_name = None, head_department_name_local = None, name_local = None, 
                          number_of_employees = None, location_id = None, next_year_budget = None,
                          visibility_id = 4, user_id = None, department_admin_id = None, security_group_id = None,
                          project_connection_list = None):
        """Creates department

        Args:
            entity_id (Guid): Guid of the entity the department belongs to, doesn't really matter since the nightingale backend just ignores this and uses the 
            name (Str): Name of the department
            general_ledger_number (int, optional): integer number, used for mfld. Defaults to None.
            head_department_id (Guid, optional): Guid id of the parent department. Defaults to None.
            head_department_name (Str, optional): Name of the parent departmnent. Defaults to None.
            head_department_name_local (Str, optional): Local name of the parent department. Defaults to None.
            name_local (Str, optional): Local name of the department. Defaults to None.
            number_of_employees (int, optional): integer number for the amount of employees in the department. Defaults to None.
            location_id (Guid, optional): Guid if of the location of the department. Defaults to None.
            next_year_budget (number, optional): Next year budget. Defaults to None.
            visibility_id (int, optional): Visibility ID, most common is 4. Defaults to 4.
            user_id (Guid, optional): Guid of the User. Defaults to None.
            department_admin_id (Guid, optional): Guid of the admin. Defaults to None.
            security_group_id (Guid, optional): Guid of the security group. Defaults to None.
            project_connection_list (object(project_connection_list), optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]
            ValueError: [description]
        """
        url = "{}/{}/".format(self.endpoint, "departments")
        data = {
            "entity_id": entity_id,
            "name": name,
            "general_ledger_number": general_ledger_number,
            "head_department_id": head_department_id,
            "head_department_name": head_department_name,
            "head_department_name_local": head_department_name_local,
            "name_local": name_local,
            "number_of_employees": number_of_employees,
            "location_id": location_id,
            "next_year_budget": next_year_budget,
            "visibility_id": visibility_id,
            "user_id": user_id,
            "department_admin_id": department_admin_id,
            "security_group_id": security_group_id,
            "project_connection_list": project_connection_list
        }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        if response.status_code == 201:
            data = response.json()["results"][0]
            self.logger.info("Successfully created department {}".format(data))
        elif response.status_code == 500:
            self.logger.error("Server error 500, failed on {}".format(data))
            self.logger.error("Response: {}".format(response.text))
            raise ValueError("500 server error check logs for details")
        else:
            self.logger.error("Unknown error creating {}".format(data))
            self.logger.error(response.text)
            raise ValueError("Unknown error check logs for details")
        
    def get_users(self):
        """Gets all the users in Nightingale

        Raises:
            ValueError: [description]
            ValueError: [description]
        """

        url = "{}/{}/?page_size=0".format(self.endpoint, "accounts")
        response = get(url=url, headers=self.headers)

        response.encoding = "utf-8"
        if response.status_code == 200:
            data = response.json()["results"]
            self.logger.info("Successfully fetched all users {}".format(data))
            return data
        elif response.status_code == 500:
            self.logger.error("Server error 500, failed on getting users")
            self.logger.error("Response: {}".format(response.text))
            raise ValueError("500 server error check logs for details")
        else:
            self.logger.error("Unknown error on getting users")
            self.logger.error(response.text)
            raise ValueError("Unknown error check logs for details")
    
    def create_user(self, email, culture_id, first_name = None, last_name = None, department_id = None, entity_id = None, entity_role_id = None, is_active = True):
        """Creates a user in nightingale

        Args:
            email (Str): email of the user
            culture_id (Str): The culture ID of the user, e.g. for Icelandic people it is 'is-IS'
            first_name (Str, optional): First name of the user. Defaults to None.
            last_name (Str, optional): Last name of the user. Defaults to None.
            department_id (Str, optional): Guid of the department the user is suppose to belong to. Defaults to None.
            entity_id (Str optional): Guid of the entity the user is suppose to belong to, doesn't matter what you put here if the the user calling this endpoint isn't a super admin. Defaults to None.
            entity_role_id ([type], optional): [description]. Defaults to None.
            is_active (bool, optional): Tells if the user is active or not, make false if you want to "delete" user. Defaults to True.

        Raises:
            ValueError: [description]
            ValueError: [description]
        """
        url = "{}/{}/".format(self.endpoint, "departments")
        data = {
            "email": email,
            "culture_id": culture_id,
            "first_name": first_name,
            "last_name": last_name,
            "department_id": department_id,
            "entity_id": entity_id,
            "entity_role_id": entity_role_id,
            "is_active": is_active
        }

        response = post(url=url, data=json.dumps(data), headers=self.headers)
        response.encoding = "utf-8"
        if response.status_code == 201:
            data = response.json()["results"][0]
            self.logger.info("Successfully created user {}".format(data))
        elif response.status_code == 500:
            self.logger.error("Server error 500, failed on {}".format(data))
            self.logger.error("Response: {}".format(response.text))
            raise ValueError("500 server error check logs for details")
        else:
            self.logger.error("Unknown error creating {}".format(data))
            self.logger.error(response.text)
            raise ValueError("Unknown error check logs for details")

