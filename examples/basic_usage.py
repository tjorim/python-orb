"""
Example usage of the Orb Python client.

This example demonstrates how to use the OrbClient to interact with
the Orb Local API for accessing datasets.

Based on the official Orb Local Analytics API specification:
https://orb.net/docs/deploy-and-configure/local-analytics
https://orb.net/docs/deploy-and-configure/datasets-configuration#local-api
"""

import asyncio
from orb import OrbClient, OrbError


async def main():
    """Example usage of the Orb client."""
    # Initialize the client with default port 7080 and a caller ID
    async with OrbClient(
        base_url="http://localhost:7080",
        caller_id="example-client"
    ) as client:
        try:
            print("Orb Local API Client Example")
            print("=" * 40)
            
            # Get scores (1-minute aggregated data)
            print("\nFetching scores_1m dataset...")
            scores = await client.get_scores_1m()
            print(f"Retrieved {len(scores)} score records")
            if scores:
                latest = scores[-1]  # Most recent record
                print(f"Latest Orb Score: {latest.get('orb_score', 'N/A')}")
                print(f"Responsiveness Score: {latest.get('responsiveness_score', 'N/A')}")
                print(f"Speed Score: {latest.get('speed_score', 'N/A')}")
            
            # Get responsiveness data (1-second granularity)
            print("\nFetching responsiveness_1s dataset...")
            responsiveness = await client.get_responsiveness_1s()
            print(f"Retrieved {len(responsiveness)} responsiveness records")
            if responsiveness:
                latest = responsiveness[-1]
                print(f"Latest Lag: {latest.get('lag_avg_us', 'N/A')} μs")
                print(f"Packet Loss: {latest.get('packet_loss_pct', 'N/A')}%")
            
            # Get speed test results
            print("\nFetching speed_results dataset...")
            speed_tests = await client.get_speed_results()
            print(f"Retrieved {len(speed_tests)} speed test records")
            if speed_tests:
                latest = speed_tests[-1]
                print(f"Latest Download: {latest.get('download_kbps', 'N/A')} Kbps")
                print(f"Latest Upload: {latest.get('upload_kbps', 'N/A')} Kbps")
            
            # Get web responsiveness data
            print("\nFetching web_responsiveness_results dataset...")
            web_resp = await client.get_web_responsiveness_results()
            print(f"Retrieved {len(web_resp)} web responsiveness records")
            if web_resp:
                latest = web_resp[-1]
                print(f"Latest TTFB: {latest.get('ttfb_us', 'N/A')} μs")
                print(f"Latest DNS: {latest.get('dns_us', 'N/A')} μs")
            
            # Example of using generic method with different formats
            print("\nFetching dataset in JSONL format...")
            jsonl_data = await client.get_dataset("scores_1m", format="jsonl")
            print(f"Retrieved {len(jsonl_data)} records in JSONL format")
            
        except OrbError as e:
            print(f"Error: {e}")
            if hasattr(e, 'status_code') and e.status_code:
                print(f"Status code: {e.status_code}")


if __name__ == "__main__":
    asyncio.run(main())