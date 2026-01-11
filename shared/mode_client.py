"""
Mode Analytics API Client - Updated for specific dashboard metrics
Handles fetching performance data from the finance forecast dashboard.
"""

import os
import requests
from typing import Dict, Optional, Any, List
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

    def get_finance_forecast_performance(self, report_id: str) -> Dict[str, Any]:
        """
        Get MTD performance vs finance forecast from the Mode dashboard.

        Based on dashboard structure:
        - FINANCE FORECAST (monthly target)
        - MTD % vs FORECAST (percentage beat)
        - MTD $ vs FORECAST (dollar amount beat)

        Args:
            report_id: Mode report ID

        Returns:
            Dictionary with performance metrics
        """
        logger.info("Fetching finance forecast performance data")

        data = self.fetch_report_data(report_id)

        # Look for the finance forecast query
        # Adjust these query names based on your actual Mode report structure
        forecast_query = None
        for query_name, query_data in data['queries'].items():
            if 'forecast' in query_name.lower() or 'finance' in query_name.lower():
                forecast_query = query_data
                break

        if not forecast_query:
            # Use the first query if we can't find a specific one
            forecast_query = list(data['queries'].values())[0]

        rows = forecast_query['rows']
        if not rows:
            raise ValueError("No data rows found in report")

        # Get the most recent row (assumes data is ordered by date)
        latest_row = rows[-1]

        # Try to extract the key metrics
        # Adjust these field names based on your actual Mode report columns
        try:
            # Try common field name patterns
            finance_forecast = self._extract_field(latest_row,
                ['FINANCE FORECAST', 'finance_forecast', 'forecast', 'target'])

            mtd_pct_vs_forecast = self._extract_field(latest_row,
                ['MTD % vs FORECAST', 'mtd_pct_vs_forecast', 'pct_vs_forecast', 'variance_pct'])

            mtd_dollar_vs_forecast = self._extract_field(latest_row,
                ['MTD $ vs FORECAST', 'mtd_dollar_vs_forecast', 'dollar_vs_forecast', 'variance'])

            # Extract actual MTD if available
            mtd_actual = self._extract_field(latest_row,
                ['MTD Actual', 'mtd_actual', 'actual', 'mtd'], required=False)

            if mtd_actual is None and finance_forecast and mtd_dollar_vs_forecast:
                # Calculate actual if not provided
                mtd_actual = finance_forecast + mtd_dollar_vs_forecast

        except (ValueError, KeyError) as e:
            # If we can't find the expected fields, log available fields
            logger.error(f"Could not parse expected fields. Available fields: {list(latest_row.keys())}")
            raise ValueError(f"Could not parse performance data: {e}")

        result = {
            'finance_forecast': finance_forecast,
            'mtd_actual': mtd_actual,
            'mtd_pct_vs_forecast': mtd_pct_vs_forecast,
            'mtd_dollar_vs_forecast': mtd_dollar_vs_forecast,
            'beat_forecast': mtd_pct_vs_forecast > 0,
            'timestamp': data['timestamp'],
            'raw_data': latest_row  # Include for debugging
        }

        logger.info(
            f"Performance: Actual={mtd_actual}, Forecast={finance_forecast}, "
            f"Beat by {mtd_pct_vs_forecast}% (${mtd_dollar_vs_forecast}K)"
        )

        return result

    def _extract_field(self, row: Dict[str, str], possible_names: List[str],
                      required: bool = True) -> Optional[float]:
        """
        Extract a field value trying multiple possible field names.

        Args:
            row: Data row dictionary
            possible_names: List of possible field names to try
            required: Whether this field is required

        Returns:
            Float value or None
        """
        for name in possible_names:
            if name in row:
                try:
                    value = row[name]
                    # Remove common formatting characters
                    if isinstance(value, str):
                        value = value.replace(',', '').replace('$', '').replace('%', '').strip()
                    return float(value)
                except (ValueError, AttributeError):
                    continue

        if required:
            raise ValueError(f"Could not find field with any of these names: {possible_names}")
        return None

    def get_daily_tracking_data(self, report_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent daily tracking data.

        Args:
            report_id: Mode report ID
            days: Number of recent days to fetch

        Returns:
            List of daily performance dictionaries
        """
        logger.info(f"Fetching daily tracking data for last {days} days")

        data = self.fetch_report_data(report_id)

        # Find the daily tracking query
        tracking_query = None
        for query_name, query_data in data['queries'].items():
            if 'daily' in query_name.lower() or 'tracking' in query_name.lower():
                tracking_query = query_data
                break

        if not tracking_query:
            logger.warning("Could not find daily tracking query")
            return []

        # Return the last N days
        rows = tracking_query['rows']
        return rows[-days:] if len(rows) > days else rows
