from datetime import datetime, timedelta, timezone
import time
import hmac
import hashlib
import requests
import json
from typing import TypeVar, Type, Optional, List, Dict, Any, Union, overload
from pydantic import ValidationError

from wyld_api.schemas import BasePayload

# Generic type variable for payload schemas
T = TypeVar('T', bound=BasePayload)


# --- Generate HMAC-SHA256 Signature ---
def get_message_signature(message: str, secret: str) -> str:
    """
    Create an HMAC-SHA256 signature.
    
    Args:
        message (str): The message to sign.
        secret (str): The API token/secret for signing.
    
    Returns:
        str: The hexadecimal representation of the signature.
    """
    hmac_obj = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return hmac_obj.hexdigest()


class WyldAPIClient:
    """
    A client to interact with Wyld Network's Fusion API.
    
    This client supports generic payload schemas for different device types.
    Users can specify their expected payload schema when fetching data.
    """
    def __init__(self, org_id: str, api_token: str):
        self.org_id = org_id
        self.api_token = api_token
   

    def generate_headers(self, dev_id: str, start_timestamp: int, end_timestamp: int) -> dict:
        """
        Generate headers for the API request.
        
        Returns:
            dict: A dictionary containing the headers.
        """
        # The "credential" value as used in your headers.
        credential = f"{self.org_id}/get"

        # Get the current time in milliseconds.
        timestamp = int(time.time() * 1000)

        # Construct the header string exactly as in the pre-request script.
        header_string = f"'credential': '{credential}', 'x-wtl-ts': '{timestamp}'"

        # For this GET request, the body is empty.
        body = "{}"

        # Construct the message digest string.
        msg_digest = (
            f"GET /\n"
            f"host: https://api.wyldnetworks.net /\n"
            f"uri: '/api/v1/devicedata/{self.org_id}/device/{dev_id}/from/{start_timestamp}/to/{end_timestamp}'/\n"
            f"headers: {header_string}/\n"
            f"body: {body}"
        )

        # Generate HMAC-SHA256 signature
        signature = get_message_signature(msg_digest, self.api_token)

        # Build request headers
        headers = {
            'authorization': 'WTL1-HMAC-SHA256',
            'credential': credential,
            'signature': signature,
            'signedheaders': 'credential;x-wtl-ts',
            'x-wtl-ts': str(timestamp)
        }

        return headers
        
    def do_get(self, url: str, headers: dict) -> requests.Response:
        """
        Perform a GET request to the specified URL with the given headers.
        
        Args:
            url (str): The URL for the GET request.
            headers (dict): The headers for the GET request.
        
        Returns:
            requests.Response: The response object from the GET request.
        """
        response = requests.get(url, headers=headers)
        return response


    def generate_url(self, dev_id: str, start_ts: int, end_ts: int) -> str:
        """
        Generate the URL for the GET request.
        
        Args:
            org_id (str): The organization ID.
            dev_id (str): The device ID.
            start_ts (int): The start timestamp.
            end_ts (int): The end timestamp.
        
        Returns:
            str: The generated URL.
        """
        return f"https://groundlink.wyldnetworks.com/api/devicedata/{self.org_id}/device/{dev_id}/from/{start_ts}/to/{end_ts}"


    def extract_payload_from_record(self, record: dict, measurement: int, force_datetime: bool = False) -> Union[datetime, str, None]:
        """
        Extract payload from record
        :param record: The record to extract from.
        :param measurement: The measurement index to extract.
        :param force_datetime: If True, always return a datetime object.
        :return: The extracted payload.
        """
        try:
            timestamp = record["objectJSON"]['data']['data_array'][-1]['measurements'][measurement]['date']

            if force_datetime:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") if isinstance(timestamp, str) else timestamp

            return timestamp
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error extracting payload: {e}")
            return None
    
    @overload
    def get_device_data(
        self, 
        dev_id: str, 
        start_ts: int, 
        end_ts: int,
        payload_schema: None = None,
        validate: bool = True
    ) -> Dict[str, Any]: ...
    
    @overload
    def get_device_data(
        self, 
        dev_id: str, 
        start_ts: int, 
        end_ts: int,
        payload_schema: Type[T],
        validate: bool = True
    ) -> List[T]: ...
        
    def get_device_data(
        self, 
        dev_id: str, 
        start_ts: int, 
        end_ts: int,
        payload_schema: Optional[Type[T]] = None,
        validate: bool = True
    ) -> Union[Dict[str, Any], List[T]]:
        """
        Fetch device data with optional schema validation.
        
        Args:
            dev_id: The device ID.
            start_ts: The start timestamp (milliseconds since epoch).
            end_ts: The end timestamp (milliseconds since epoch).
            payload_schema: Optional Pydantic model class for payload validation.
                           Should inherit from BasePayload.
            validate: If True and payload_schema is provided, validate and parse
                     the response data according to the schema.
        
        Returns:
            If payload_schema is None: Raw dict response from API
            If payload_schema is provided and validate=True: List of validated payload objects
            If payload_schema is provided and validate=False: Raw dict with schema attached
        
        Example:
            # Without schema (raw response)
            client = WyldAPIClient(org_id, token)
            data = client.get_device_data(dev_id, start_ts, end_ts)
            
            # With schema validation
            data = client.get_device_data(
                dev_id, start_ts, end_ts, 
                payload_schema=TemperatureSensorPayload
            )
            for item in data:
                print(f"Temperature: {item.temperature}°C")
        """
        url = self.generate_url(dev_id, start_ts, end_ts)
        headers = self.generate_headers(dev_id, start_ts, end_ts)
        response = self.do_get(url, headers)
        
        response.raise_for_status()  # Raise exception for bad status codes
        raw_data = response.json()
        
        # If no schema provided, return the records list (or raw data if no 'records' key)
        if payload_schema is None:
            # Extract records list if present, otherwise return raw data
            if isinstance(raw_data, dict) and 'records' in raw_data:
                return raw_data['records']
            return raw_data
        
        # If schema provided but validation disabled, return raw data
        if not validate:
            return raw_data
        
        # Parse and validate data according to schema
        return self._parse_with_schema(raw_data, payload_schema)
    
    
    def _parse_with_schema(self, raw_data: Dict[str, Any], schema: Type[T]) -> List[T]:
        """
        Parse raw API response data with the provided schema.
        
        Args:
            raw_data: The raw response data from the API.
            schema: The Pydantic model class to use for parsing.
        
        Returns:
            List of validated payload objects.
        
        Raises:
            ValidationError: If the data doesn't match the schema.
        """
        parsed_items = []
        
        # Handle different response structures
        if isinstance(raw_data, list):
            records = raw_data
        elif isinstance(raw_data, dict) and 'records' in raw_data:
            records = raw_data['records']
        elif isinstance(raw_data, dict) and 'data' in raw_data:
            records = raw_data['data']
        else:
            records = [raw_data]
        
        for record in records:
            try:
                # Extract the payload from the nested structure
                # Adjust this based on your actual API response structure
                if isinstance(record, dict):
                    # Try to find the actual payload data
                    payload_data = self._extract_payload_data(record)
                    validated_item = schema.model_validate(payload_data)
                    parsed_items.append(validated_item)
            except ValidationError as e:
                print(f"Validation error for record: {e}")
                # Optionally re-raise or continue
                raise
        
        return parsed_items
    
    
    def _extract_payload_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract the actual payload data from a nested record structure.
        
        This method handles the codec-decoded payload that varies per device type.
        Override this method if your API has a different structure.
        
        Args:
            record: A single record from the API response.
        
        Returns:
            The extracted payload data as a dict.
        """
        # Common patterns - adjust based on your API structure
        if 'objectJSON' in record:
            obj_json = record['objectJSON']
            if 'payload' in obj_json:
                return obj_json['payload']
            elif 'decoded_payload' in obj_json:
                return obj_json['decoded_payload']
            elif 'data' in obj_json:
                # If data contains the actual measurements
                return obj_json['data']
        
        # If payload is at root level
        if 'payload' in record:
            return record['payload']
        
        # Return the whole record if we can't find a specific payload
        return record
