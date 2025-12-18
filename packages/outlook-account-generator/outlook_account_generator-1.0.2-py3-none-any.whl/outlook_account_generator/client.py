import requests
import time

class OutlookGen:
    def __init__(self, api_key):
        self.base_url = "https://temp-outlook-api.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "temp-outlook-api.p.rapidapi.com",
            "Content-Type": "application/json"
        }

    def create_account(self, mail_type="outlook"):
        """
        Creates a new email account.
        Args:
            mail_type (str): 'outlook' or 'hotmail'
        """
        if mail_type not in ["outlook", "hotmail"]:
            raise ValueError("mail_type must be 'outlook' or 'hotmail'")

        endpoint = f"/get/{mail_type}"
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            if response.status_code == 403 or response.status_code == 401:
                raise PermissionError("❌ Invalid API Key! Get a key here: https://rapidapi.com/EymenTakak/api/temp-outlook-api")
            else:
                raise Exception(f"API Error: {response.text}")

    def get_inbox(self, email, enc_token):
        """
        Fetches inbox messages.
        """
        url = f"{self.base_url}/get/inbox"
        payload = {"email": email, "token": enc_token}

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json().get("emails", [])
        except Exception as e:
             raise Exception(f"Inbox Error: {str(e)}")

    def wait_for_otp(self, email, enc_token, timeout=60, check_interval=5):
        """
        Helper: Waits for an email to arrive.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            inbox = self.get_inbox(email, enc_token)
            if inbox:
                return inbox[0] # Return latest email
            time.sleep(check_interval)
        return None
