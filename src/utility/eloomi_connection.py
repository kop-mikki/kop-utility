import requests
import time
from utility.name_changes import split_name
from utility.eloomi_utility import get_department_by_name
import json

class EloomiConnection(object):
    """This class is used to connect to the eloomi api

    Args:
        object (object): Extends the Class Object 
    """
    def __init__(self, logger, client_id, client_secret):
        """Initializes the class. creates the class varibales, including the access_token which it generates.
        
        CLASS VARIABLES
            endpoint:               String containing the value of the base url 
            client_id:              is the id of the client that's stored in the .env file and is used when calling the api
            client_secret:          is the secret given by eloomi. stored in the .env file and is used when generating the access_token
            access_token:           generated throught the api using client_id and client secret. 
            headers:                basic header for api calls, contains the client_id and authorization token(BEARER TOKEN) 
            ratelimit_remaining:    is the remaining ratelimit that the eloomi has
        """
        self.logger = logger
        self.endpoint = 'https://api.eloomi.com/'
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.create_access_token()
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'ClientId': self.client_id,
            'Authorization': self.access_token,
        }
        self.ratelimit_remaining = 600
    
    def set_ratelimit_remaining(self, headers):
        """
        Takes in the heders from the response and checks if the rate limit is low, 
        if the rate limit is low, the program halts for 30 seconds to allow the rate limit to reset

        Args:
            headers (Dict): headers recieved from eloomi api
        """
        limit = int(headers._store['x-ratelimit-remaining'][1])
        if(limit < 100):
            self.logger.warning("Ratelimit is low, halting for 30 sec") 
            time.sleep(30)
        self.ratelimit_remaining = limit


    def create_access_token(self):
        """This method generates the API token (BEARER TOKEN)

        Returns:
            String: Bearer Token for the Eloomi API
        """
        url = self.endpoint + 'oauth/token'

        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': '*',
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully created Access token")
            return response.json()['access_token']
        else:
            self.logger.error('Creating access token did not work with status code {}'.format(response.status_code))
            self.logger.error(response)
            return False

    def get_users(self):
        """
        This method fetches a list of all the users in eloomi
        and returns a list of them.
        

        Returns:
            List[EloomiUser]: List of Eloomi Users 
        """
        url = self.endpoint + 'v3/users'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            # setting the rate limit
            self.set_ratelimit_remaining(response.headers)
            
            self.logger.info("Successfully fetched a list of all the users in eloomi")
            return response.json()['data']
        else:
            self.logger.error('Getting eloomi user list failed with code {}'.format(response.status_code))
            self.logger.error(response)
            return False
    
    def update_user(self, user):
        """This method partially updates the user by it's employee_id (kennitala)

        Args:
            user (EloomiUser): Eloomi user object containing the new information. 

        Returns:
            EloomiUser: Updated User
        """
        url = self.endpoint + 'v3/users-employee_id/{}'.format(user['employee_id'].strip())
        first_name, last_name = split_name(user['name'])
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'username': user['username'].strip(),
            'title': user['title'].strip(),
            'email': user['email'].strip(),
            'department_id': [str(user['department_id'])],
            'direct_manager_ids': [user['manager_id']],
            'user_permission': 'user'
        }

        # for some reason this request has to be manually made. 
        sess = requests.Session()

        req = requests.Request('Patch', url, data=json.dumps(data), headers=self.headers)
        prep = req.prepare()
        prep.headers['Content-Type'] = "application/json"
        prep.headers['Content-Length'] = len(json.dumps(data).encode('utf-8'))
        
        response = sess.send(prep)
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully Updated user: {}".format(user['email']))
            return response.json()['data']
        else:
            self.logger.error("Updating eloomi user failed with code {}: {}".format(response.status_code, response._content))
            self.logger.error(response)
            return False

    def disable_user(self, email):
        """This method disables the user by it's email

        Args:
            email (Str): Email of the user, that is being disabled

        Returns:
            EloomiUser: Updated User (Disabled User)
        """
        url = self.endpoint + 'v3/users-email/{}'.format(email)

        data = {
            'activate': 'deactivate'
        }

        response = requests.patch(url, headers=self.headers, data=data)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully Updated user: {}".format(email))
            return response.json()['data']
        else:
            self.logger.error("Disabling eloomi user failed with code {}: {}".format(response.status_code, response._content))
            self.logger.error(response)
            return False
            
    def enable_user(self, email):
        """This method enables the user by it's email

        Args:
            email (Str): Email of the user, that is being enabled

        Returns:
            EloomiUser: Updated User (Enabled User)
        """
        url = self.endpoint + 'v3/users-email/{}'.format(email)

        data = {
            'activate': 'instant'
        }

        response = requests.patch(url, headers=self.headers, data=data)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully Updated user: {}".format(email))
            return response.json()['data']
        else:
            self.logger.error("Enabling eloomi user failed with code {}: {}".format(response.status_code, response._content))
            self.logger.error(response)
            return False

    def create_user(self, user):
        """This method creates a eloomi user.

        Args:
            user (EloomiUser): User object of the User being created

        Returns:
            EloomiUser: Returns the new EloomiUser object 
        """
        url = self.endpoint + 'v3/users'
        first_name, last_name = split_name(user['name'])
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'employee_id': user['employee_id'].strip(),
            'email': user['email'].strip(),
            'username': user['username'].strip(),
            'title': user['title'].strip(),
            'activate': 'instant',
            'user_permission': 'user'
        }

        response = requests.post(url, headers=self.headers, data=data)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully created user {}".format(user['email']))
            return response.json()['data']
        else:
            self.logger.error("{}".format(response._content))
            self.logger.error(response)
            return False

    def get_departments(self):
        """
        This method fetches a list of all the departments in eloomi.
        And returns a list of them.

        Returns:
            List[EloomiDepartment]: List of Eloomi Departments
        """
        url = self.endpoint + 'v3/units'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            # setting the rate limit
            self.set_ratelimit_remaining(response.headers)
            
            self.logger.info("Successfully Fetched all departments from eloomi")
            return response.json()['data']
        else:
            self.logger.error("Getting eloomi department list failed with code {}".format(response.status_code))
            self.logger.error(response)
            return False
    
    def create_department(self, user, departments):
        """This method creates an dapartment

        Args:
            user (EloomiUser): User with a department that does not exists and is being created
            departments (List[EloomiDepartment]): List of currently created department, used to get the ID of the parent department

        Returns:
            Int: Returns the ID of the newly created eloomi department
        """
        url = self.endpoint + 'v3/units'
        parent_id = get_department_by_name(departments, user['division'])
        data = {
            "name": user['department'].strip(),
            "parent_id": parent_id,
            "code": "{}-{}".format(user['mfld'].strip(), user['department'].strip())
        }

        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            self.logger.info("Successfully Created department: {}".format(user['department']))
            return response.json()['data']['id']
        else:
            self.logger.warning('Creating eloomi department failed with code {}'.format(response.status_code))
            self.logger.error(response)
            return False
    
    def delete_department(self, departmentid):
        """This method deletes an department

        Args:
            departmentid (Int): ID of the department being deleted
        """
        url = self.endpoint + 'v3/units/{}'.format(departmentid)
        requests.delete(url, headers=self.headers)

    def get_courses(self):
        """
        This method fetches a list of all the courses in eloomi.
        And returns a list of them.

        Returns:
            List[EloomiCourses]: List of Eloomi Courses
        """
        url = self.endpoint + 'v3/courses'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            # setting the rate limit
            self.set_ratelimit_remaining(response.headers)
            
            self.logger.info("Successfully Fetched all courses from eloomi")
            mapped_data = { "COURSE{}".format(str(x['id']).zfill(5)): x for x in response.json()['data'] }
            return mapped_data
        else:
            self.logger.error("Getting eloomi courses list failed with code {}".format(response.status_code))
            self.logger.error(response)
            return False
        
    def get_participants(self, courseID):
        """
        This method fetches a list of all the participants for a specific course, using the ID
        And returns a list of them

        Args:
            courseID (Int): ID of the course in Eloomi

        Returns:
            List[EloomiUser]: List of Eloomi Users that are a part of this particular course
        """
        url = "{}v3/courses/{}/participants".format(self.endpoint, courseID)

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            # setting the rate limit
            self.set_ratelimit_remaining(response.headers)

            self.logger.info("Successfully Fetched all participants for {} from eloomi".format(courseID))
            return response.json()['data']
        else:
            self.logger.error("Getting eloomi participants list failed with code {}".format(response.status_code))
            self.logger.error(response)
            return False