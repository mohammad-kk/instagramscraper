import requests
import json
from datetime import datetime, timedelta
from time import sleep

class InstagramAPI:
    def __init__(self, api_key, max_requests=10):
        self.api_key = api_key
        self.base_url = "https://api.scrapecreators.com/v1/instagram/profile"
        self.headers = {
            "x-api-key": api_key,
            "Accept": "application/json"
        }
        self.processed_users = set()
        self.request_count = 0
        self.max_requests = max_requests
        self.start_time = datetime.now()

    def _check_rate_limit(self):
        if self.request_count >= self.max_requests:
            time_elapsed = datetime.now() - self.start_time
            if time_elapsed < timedelta(hours=1):
                sleep_time = 3600 - time_elapsed.total_seconds()
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                sleep(sleep_time)
                self.request_count = 0
                self.start_time = datetime.now()

    def fetch_profile(self, username, depth=0, max_depth=0):  # Changed default max_depth to 0
        """Fetch a single profile without recursive related profile fetching"""
        if username in self.processed_users:
            print(f"Skipping {username} - already processed")
            return None

        self._check_rate_limit()
        
        try:
            params = {"handle": username}
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            self.request_count += 1
            self.processed_users.add(username)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching profile for {username}: {str(e)}")
            return None

    def fetch_posts(self, username):
        """Fetch user's posts from Instagram"""
        if username in self.processed_users:
            print(f"Skipping posts for {username} - already processed")
            return None

        self._check_rate_limit()
        
        try:
            params = {"handle": username}
            response = requests.get(
                "https://api.scrapecreators.com/v1/instagram/user/posts",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            self.request_count += 1
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching posts for {username}: {str(e)}")
            return None

    def get_stats(self):
        return {
            "processed_users": len(self.processed_users),
            "requests_made": self.request_count,
            "requests_remaining": self.max_requests - self.request_count
        }

def main():
    api = InstagramAPI()  # Will use environment variable
    username = "lightningvette"
    print(f"Starting profile crawl from: {username}")
    profile_data = api.fetch_profile(username, max_depth=2)
    
    if profile_data:
        print(f"\nAPI Stats:")
        stats = api.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print(f"Failed to fetch profile for {username}")

if __name__ == "__main__":
    main()