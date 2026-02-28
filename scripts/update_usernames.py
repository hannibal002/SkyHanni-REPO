#!/usr/bin/env python3

import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional, Dict, List

API_URL = "https://api.mojang.com/user/profile/"
JSON_PATH = "constants/ContributorList.json"
MAX_THREADS = 5
TIMEOUT = 60

_username_cache: Dict[str, Optional[str]] = {}
_cache_lock = Lock()

_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "Contributors-Updater/1.0")]

def get_username_from_uuid(uuid_str: str) -> Optional[str]:
    with _cache_lock:
        if uuid_str in _username_cache:
            return _username_cache[uuid_str]

    try:
        with _opener.open(API_URL + uuid_str, timeout=TIMEOUT) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                username = data.get("name")

                with _cache_lock:
                    _username_cache[uuid_str] = username

                return username

    except urllib.error.HTTPError as e:
        print(f"Error {e.code} for {uuid_str}")
    except urllib.error.URLError as e:
        print(f"Error {e.reason} for {uuid_str}")
    except Exception as e:
        print(e)

    with _cache_lock:
        _username_cache[uuid_str] = None

    return None

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    try:
        data = load_json(JSON_PATH)
        contributors = data.get("contributors")

        if not isinstance(contributors, dict):
            print("Contributors data is not a dict")
            return

        changed_data_list: List[Dict[str, str]] = []

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_uuid = {
                executor.submit(get_username_from_uuid, uuid): uuid
                for uuid in contributors.keys()
            }

            for future in as_completed(future_to_uuid):
                uuid = future_to_uuid[future]

                try:
                    username = future.result()
                    contributor_data = contributors[uuid]
                    current_display_name = contributor_data.get("display_name")

                    if username and username != current_display_name:
                        contributor_data["display_name"] = username

                        action = (
                            "Created"
                            if current_display_name is None
                            else "Updated"
                        )

                        changed_data_list.append({
                            "uuid": uuid,
                            "display_name": username,
                            "action": action,
                        })

                        print(f"{action}: {uuid} -> {username}")

                    elif not username:
                        print(f"Failed to fetch username for UUID: {uuid}")

                except Exception as e:
                    print(f"Error processing UUID {uuid}: {e}")

        if changed_data_list:
            save_json(JSON_PATH, data)
            print(f"Updated {len(changed_data_list)} entries")
        else:
            print("Nothing updated")

    except FileNotFoundError:
        print(f"File not found: {JSON_PATH}")
    except json.JSONDecodeError:
        print(f"Invalid JSON file: {JSON_PATH}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
