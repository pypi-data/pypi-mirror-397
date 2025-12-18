import requests
from requests.auth import HTTPBasicAuth

class PiDataMetrics:
    def __init__(self, client_id, client_secret, account_id=1505):
        self.auth_url = "https://app.pi-datametrics.com/api/auth"
        self.base_url = f"https://app.pi-datametrics.com/api/accounts/{account_id}"
        self.access_token = self._get_access_token(client_id, client_secret)
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _get_access_token(self, client_id, client_secret):
        data = {"grant_type": "client_credentials"}
        auth = HTTPBasicAuth(client_id, client_secret)
        try:
            response = requests.post(self.auth_url, data=data, auth=auth)
            response.raise_for_status()
            return response.json()['access_token']
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Authentication Failed: {e}")

    # --- Generic Request Handler ---
    def fetch_endpoint(self, endpoint_path, params=None):
        """Generic method to fetch any endpoint"""
        url = f"{self.base_url}/{endpoint_path}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get('data', [])

    # --- Specific Endpoint Wrappers ---
    def get_workspaces(self):
        return self.fetch_endpoint("workspaces")

    def get_stgs(self, workspace_id):
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-term-groups")

    def get_search_terms(self, workspace_id, stg_id):
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-term-groups/{stg_id}/search-terms")

    def get_bulk_serp_data(self, workspace_id, search_engine_id, period, **kwargs):
        """
        Fetches data based on the documentation provided.
        kwargs can include: number-of-results, ranking-mode, site-id, etc.
        """
        params = {
            "search-engine-id": search_engine_id,
            "period": period
        }
        # Add optional parameters from kwargs
        params.update(kwargs)
        
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-data/bulk-search-results", params=params)

    # --- Existing Methods ---
    def get_workspaces(self):
        return self.fetch_endpoint("workspaces")

    def get_stgs(self, workspace_id):
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-term-groups")

    def get_search_terms(self, workspace_id, stg_id):
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-term-groups/{stg_id}/search-terms")

    def get_bulk_serp_data(self, workspace_id, search_engine_id, period, **kwargs):
        params = {"search-engine-id": search_engine_id, "period": period}
        params.update(kwargs)
        return self.fetch_endpoint(f"workspaces/{workspace_id}/search-data/bulk-search-results", params=params)

    # --- NEW: Search Volume Method ---
    def get_bulk_volume(self, workspace_id, start_date=None, end_date=None):
        params = {}
        if start_date and end_date:
            params = {'start-period': start_date, 'end-period': end_date}
        return self.fetch_endpoint(f"workspaces/{workspace_id}/volume-data/bulk-search-volume", params=params)