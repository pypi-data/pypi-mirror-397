import os
import sys
import json
from .client import PrintablesClient


def main():
    user_id = os.environ.get("PRINTABLES_USER_ID")
    if not user_id:
        print("Error: PRINTABLES_USER_ID environment variable not set.")
        sys.exit(1)

    print(f"Fetching stats for user: {user_id}")
    client = PrintablesClient()
    stats = client.get_user_stats(user_id)

    if stats:
        print(json.dumps(stats, indent=2))
    else:
        print("Failed to retrieve stats.")
        sys.exit(1)


if __name__ == "__main__":
    main()
