"""
Example usage of the Orb Python client.

This example demonstrates how to use the OrbClient to interact with
the Orb local API for datasets and status monitoring.
"""

import asyncio
from orb import OrbClient, OrbError


async def main():
    """Example usage of the Orb client."""
    # Initialize the client
    async with OrbClient(base_url="http://localhost:8080") as client:
        try:
            # Get system status
            print("Getting system status...")
            status = await client.get_status()
            print(f"Status: {status.status}")
            if status.version:
                print(f"Version: {status.version}")
            if status.uptime:
                print(f"Uptime: {status.uptime}")
            
            # List available datasets
            print("\nListing datasets...")
            datasets = await client.list_datasets()
            print(f"Found {len(datasets)} datasets:")
            for dataset in datasets:
                print(f"  - {dataset.name}: {dataset.description or 'No description'}")
                if dataset.row_count:
                    print(f"    Rows: {dataset.row_count}")
                if dataset.size:
                    print(f"    Size: {dataset.size} bytes")
            
            # Get details for the first dataset (if any)
            if datasets:
                dataset_name = datasets[0].name
                print(f"\nGetting details for dataset '{dataset_name}'...")
                details = await client.get_dataset(dataset_name)
                print(f"Description: {details.description or 'No description'}")
                if details.columns:
                    print(f"Columns: {len(details.columns)}")
                    for col in details.columns[:3]:  # Show first 3 columns
                        print(f"  - {col.get('name', 'unknown')}: {col.get('type', 'unknown')}")
                    if len(details.columns) > 3:
                        print(f"  ... and {len(details.columns) - 3} more")
                
                # Query the dataset
                print(f"\nQuerying dataset '{dataset_name}'...")
                try:
                    result = await client.query_dataset(
                        dataset_name,
                        "SELECT * FROM " + dataset_name + " LIMIT 5",
                        limit=5
                    )
                    print(f"Query returned {result.row_count} rows")
                    print(f"Columns: {', '.join(result.columns)}")
                    if result.execution_time_ms:
                        print(f"Execution time: {result.execution_time_ms}ms")
                    
                    # Show first few rows
                    if result.data:
                        print("Sample data:")
                        for i, row in enumerate(result.data[:2]):
                            print(f"  Row {i+1}: {row}")
                            
                except OrbError as e:
                    print(f"Query failed: {e}")
            
        except OrbError as e:
            print(f"Error: {e}")
            if hasattr(e, 'status_code') and e.status_code:
                print(f"Status code: {e.status_code}")


if __name__ == "__main__":
    asyncio.run(main())