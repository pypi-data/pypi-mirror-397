import requests
import logging
from typing import Optional, List, Dict, Any, Union
from .exceptions import (
    RideScanError, AuthenticationError, ValidationError, 
    ResourceNotFoundError, ConflictError, ServerError
)

# Set up a library-specific logger
logger = logging.getLogger("ridescanapi")

class RideScanClient:
    """
    Official Python SDK for the RideScan Safety Layer API.
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api", timeout: int = 30):
        """
        Initialize the RideScan client.

        Args:
            api_key (str): The 'rsk_...' key generated from the dashboard.
            base_url (str): The API endpoint. Defaults to localhost.
            timeout (int): Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # Pre-configure headers (Optimized for reuse)
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "User-Agent": "ridescan-python-sdk/1.0.0"
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parses the response and raises specific exceptions based on backend error codes.
        """
        try:
            # Raise HTTPError for 4xx/5xx first to catch generic connection issues
            response.raise_for_status()
            
            # If successful (200-299), return JSON
            if response.status_code != 204: # 204 No Content has no JSON
                return response.json()
            return {}

        except requests.exceptions.HTTPError:
            # Attempt to parse the structured backend error
            try:
                payload = response.json()
                error_body = payload.get("error", {})
                
                # Handle simplified error strings if they exist
                if isinstance(error_body, str):
                    msg = error_body
                    code = "UNKNOWN"
                    details = None
                else:
                    code = error_body.get("code", "UNKNOWN")
                    msg = error_body.get("message", str(response.reason))
                    details = error_body.get("details")

                # Map specific Backend Error Codes to Python Exceptions
                if code.startswith("RS-AUTH"):
                    raise AuthenticationError(msg, code, details)
                elif code.startswith("RS-VAL"):
                    raise ValidationError(msg, code, details)
                elif "002" in code and ("ROBOT" in code or "MSN" in code):
                    # RS-ROBOT-002 or equivalent checks
                    raise ResourceNotFoundError(msg, code, details)
                elif code in ["RS-ROBOT-001", "RS-MSN-001"]:
                    raise ConflictError(msg, code, details)
                elif code.startswith("RS-SYS"):
                    raise ServerError(msg, code, details)
                else:
                    # Fallback for unmapped errors
                    raise RideScanError(msg, code, details)

            except ValueError:
                # Response wasn't JSON (e.g. 502 Bad Gateway HTML)
                raise RideScanError(f"HTTP {response.status_code}: {response.text[:100]}")

    def _request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Request: {method} {url} | Payload: {payload}")
        
        try:
            # Note: We send 'json' even for GET requests per RideScan backend design
            response = self.session.request(method, url, json=payload, timeout=self.timeout)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            raise RideScanError("Failed to connect to RideScan API. Is the server running?")
        except requests.exceptions.Timeout:
            raise RideScanError(f"Request timed out after {self.timeout}s")

    # ==========================
    # ROBOT RESOURCES
    # ==========================

    def create_robot(self, name: str, robot_type: str) -> Dict[str, Any]:
        """
        Register a new robot in the organization.

        Args:
            name (str): Unique name for the robot (e.g., 'Spot-Alpha').
            robot_type (str): The model type. Allowed: 'spot', 'ur6'.
        """
        payload = {
            "params": {
                "robot_name": name,
                "robot_type": robot_type
            }
        }
        return self._request("POST", "/robot/create", payload)

    def get_robots(self, 
                   robot_id: Optional[str] = None, 
                   name: Optional[str] = None, 
                   robot_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for robots. Returns a list of matches.
        
        Args:
            robot_id (str): Filter by the public UUID of the robot.
            name (str): Filter by exact robot name.
            robot_type (str): Filter by type ('spot', 'ur6').
        """
        criteria = {}
        if robot_id: criteria["robot_id"] = robot_id
        if name: criteria["robot_name"] = name
        if robot_type: criteria["robot_type"] = robot_type

        # Backend expects 'criteria' object even for GET
        response = self._request("GET", "/getrobot", payload={"criteria": criteria})
        return response.get("robot_list", [])

    def edit_robot(self, robot_id: str, 
                   new_name: Optional[str] = None, 
                   new_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a robot's details.
        
        Args:
            robot_id (str): The unique UUID of the robot to edit.
            new_name (str, optional): New name to assign.
            new_type (str, optional): New type to assign.
        """
        params = {}
        if new_name: params["robot_name"] = new_name
        if new_type: params["robot_type"] = new_type

        if not params:
            raise ValidationError("Must provide at least new_name or new_type")

        payload = {
            "criteria": {"robot_id": robot_id},
            "params": params
        }
        return self._request("PATCH", "/editrobot", payload)

    def delete_robot(self, robot_id: str) -> Dict[str, Any]:
        """
        Permanently delete a robot.
        """
        payload = {
            "criteria": {"robot_id": robot_id}
        }
        return self._request("DELETE", "/deleterobot", payload)

    # ==========================
    # MISSION RESOURCES
    # ==========================

    def create_mission(self, robot_id: str, mission_name: str) -> Dict[str, Any]:
        """
        Create a new mission for a specific robot.
        """
        payload = {
            "params": {
                "robot_id": robot_id,
                "mission_name": mission_name
            }
        }
        return self._request("POST", "/createmission", payload)

    def get_missions(self, 
                     robot_id: Optional[str] = None, 
                     mission_id: Optional[str] = None,
                     mission_name: Optional[str] = None,
                     start_time: Optional[str] = None, 
                     end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for missions.

        Args:
            robot_id (str, optional): Filter by parent robot UUID.
            mission_id (str, optional): Filter by mission UUID.
            start_time (str, optional): Filter missions created after this ISO timestamp.
            end_time (str, optional): Filter missions created before this ISO timestamp.
        """
        criteria = {}
        if robot_id: criteria["robot_id"] = robot_id
        if mission_id: criteria["mission_id"] = mission_id
        if mission_name: criteria["mission_name"] = mission_name
        if start_time: criteria["start_time"] = start_time
        if end_time: criteria["end_time"] = end_time

        response = self._request("GET", "/getmission", payload={"criteria": criteria})
        return response.get("mission_list", [])

    def edit_mission(self, robot_id: str, mission_id: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a mission. 
        
        Note: Requires BOTH robot_id and mission_id for security targeting.
        """
        payload = {
            "criteria": {
                "robot_id": robot_id,
                "mission_id": mission_id
            },
            "params": {
                "mission_name": new_name
            }
        }
        return self._request("PATCH", "/editmission", payload)

    def delete_mission(self, robot_id: str, mission_id: str) -> Dict[str, Any]:
        """
        Delete a mission.
        
        Note: Requires BOTH robot_id and mission_id.
        """
        payload = {
            "criteria": {
                "robot_id": robot_id,
                "mission_id": mission_id
            }
        }
        return self._request("DELETE", "/deletemission", payload)