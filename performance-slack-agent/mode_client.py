"""
Mode Analytics API Client
Handles fetching performance data from Mode Analytics dashboards.
"""

import os
import requests
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ModeClient:
    """Client for interacting with Mode Analytics API."""

    def __init__(self, api_token: Optional[str] = None, api_secret: Optional[str] = None,
                 workspace: Optional[str] = None):
        """
        Initialize Mode client.

        Args:
            api_token: Mode API token (defaults to MODE_API_TOKEN env var)
            api_secret: Mode API secret (defaults to MODE_API_SECRET env var)
            workspace: Mode workspace name (defaults to MODE_WORKSPACE env var)
        """
        self.api_token = api_token or os.getenv('MODE_API_TOKEN')
        self.api_secret = api_secret or os.getenv('MODE_API_SECRET')
        self.workspace = workspace or os.getenv('MODE_WORKSPACE')

        if not all([self.api_token, self.api_secret, self.workspace]):
            raise ValueError("MODE_API_TOKEN, MODE_API_SECRET, and MODE_WORKSPACE must be set")

        self.base_url = f"https://app.mode.com/api/{self.workspace}"
        self.auth = (self.api_token, self.api_secret)

    def fetch_report_data(self, report_id: str, query_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch the latest data from a Mode report.

        Args:
            report_id: The Mode report ID
            query_name: Optional specific query name to fetch

        Returns:
            Dictionary containing the report data
        """
        logger.info(f"Fetching report data for report {report_id}")

        # Get the latest run for the report
        runs_url = f"{self.base_url}/reports/{report_id}/runs"
        response = requests.get(runs_url, auth=self.auth)
        response.raise_for_status()

        runs = response.json().get('_embedded', {}).get('report_runs', [])
        if not runs:
            raise ValueError(f"No runs found for report {report_id}")

        latest_run = runs[0]
        run_token = latest_run['token']

        logger.info(f"Found latest run: {run_token}")

        # Get the queries from this run
        queries_url = f"{self.base_url}/reports/{report_id}/runs/{run_token}/queries"
        response = requests.get(queries_url, auth=self.auth)
        response.raise_for_status()

        queries = response.json().get('_embedded', {}).get('queries', [])

        result = {
            'report_id': report_id,
            'run_token': run_token,
            'timestamp': latest_run.get('created_at'),
            'queries': {}
        }

        # Fetch data for each query
        for query in queries:
            query_token = query['token']
            query_name_actual = query.get('name', query_token)

            # Skip if we're looking for a specific query and this isn't it
            if query_name and query_name_actual != query_name:
                continue

            # Get query results
            results_url = f"{self.base_url}/reports/{report_id}/runs/{run_token}/queries/{query_token}/results/content"
            response = requests.get(results_url, auth=self.auth)
            response.raise_for_status()

            # Parse the CSV-like response
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                continue

            headers = lines[0].split(',')
            rows = []
            for line in lines[1:]:
                values = line.split(',')
                rows.append(dict(zip(headers, values)))

            result['queries'][query_name_actual] = {
                'headers': headers,
                'rows': rows
            }

            logger.info(f"Fetched query '{query_name_actual}' with {len(rows)} rows")

        return result

    def get_yesterday_performance(self, report_id: str,
                                  performance_field: str = 'actual',
                                  forecast_field: str = 'forecast') -> Dict[str, float]:
        """
        Get yesterday's performance vs forecast from a Mode report.

        Args:
            report_id: Mode report ID
            performance_field: Name of the field containing actual performance
            forecast_field: Name of the field containing forecast

        Returns:
            Dictionary with 'actual', 'forecast', and 'beat_forecast' keys
        """
        logger.info("Fetching yesterday's performance data")

        data = self.fetch_report_data(report_id)

        # Assume the first query contains the data
        if not data['queries']:
            raise ValueError("No query data found in report")

        first_query = list(data['queries'].values())[0]
        rows = first_query['rows']

        if not rows:
            raise ValueError("No data rows found in report")

        # Get the most recent row (assumes data is ordered by date)
        latest_row = rows[-1]

        try:
            actual = float(latest_row.get(performance_field, 0))
            forecast = float(latest_row.get(forecast_field, 0))
        except (ValueError, KeyError) as e:
            raise ValueError(f"Could not parse performance data: {e}")

        result = {
            'actual': actual,
            'forecast': forecast,
            'beat_forecast': actual > forecast,
            'beat_percentage': ((actual - forecast) / forecast * 100) if forecast > 0 else 0
        }

        logger.info(f"Performance: Actual={actual}, Forecast={forecast}, Beat={result['beat_forecast']}")

        return result
