# coding: utf-8

"""
    Graphiant APIs
    Testing DefaultAPIService
    
    Sanity test for basic API functionality including authentication and edge summary retrieval.
"""

import os
import unittest

import graphiant_sdk
from graphiant_sdk.api.default_api import DefaultApi


class TestSanity(unittest.TestCase):
    """Sanity test for DefaultAPIService"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        # Skip test if credentials are not configured
        self.username = os.getenv("GRAPHIANT_USERNAME")
        self.password = os.getenv("GRAPHIANT_PASSWORD")
        
        if not self.username or not self.password:
            self.skipTest(
                "Skipping test - GRAPHIANT_USERNAME and GRAPHIANT_PASSWORD "
                "environment variables are required"
            )
        
        # Set up configuration
        host = os.getenv("GRAPHIANT_HOST", "https://api.graphiant.io")
        
        # Remove any protocol prefix (e.g., "gcs:https://" -> "https://")
        if host.startswith("gcs:"):
            host = host[4:]
        
        # Ensure it starts with https:// if no scheme is present
        if not host.startswith("http://") and not host.startswith("https://"):
            host = "https://" + host.lstrip("/")
        
        self.config = graphiant_sdk.Configuration(host=host)
        self.api_client = graphiant_sdk.ApiClient(self.config)
        self.api = DefaultApi(self.api_client)

    def tearDown(self) -> None:
        """Clean up after test"""
        pass

    def test_edge_summary(self) -> None:
        """Test DefaultAPIService V1AuthLoginPost and V1EdgesSummaryGet"""
        
        # =================== Get Auth Token ==================
        
        auth_request = graphiant_sdk.V1AuthLoginPostRequest(
            username=self.username,
            password=self.password
        )
        
        print("Calling V1AuthLoginPost")
        
        try:
            auth_response = self.api.v1_auth_login_post(
                v1_auth_login_post_request=auth_request
            )
            self.assertIsNotNone(auth_response, "V1AuthLoginPost API response is None")
            self.assertIsNotNone(auth_response.token, "Auth token is None")
            
            bearer_token = f"Bearer {auth_response.token}"
            print(f"Auth token: {auth_response.token[:20] if len(auth_response.token) > 20 else auth_response.token}...")
        except Exception as e:
            self.fail(f"http call returned error: {e}")
        
        # =================== Get Edges Summary ==================
        
        print("Calling V1EdgesSummaryGet")
        
        try:
            edges_summary = self.api.v1_edges_summary_get(authorization=bearer_token)
            self.assertIsNotNone(
                edges_summary, "Get edges summary API response is None"
            )
            self.assertIsNotNone(
                edges_summary.edges_summary,
                "Edges summary data is None"
            )
            
            import json
            summary_json = json.dumps(
                [edge.to_dict() for edge in edges_summary.edges_summary],
                indent=2,
                default=str
            )
            print(f"Edge summary response: {len(edges_summary.edges_summary)} devices found")
            print(f"Edge summary details: {summary_json}")
        except Exception as e:
            self.fail(f"Get edges summary API request failed: {e}")


if __name__ == "__main__":
    unittest.main()
