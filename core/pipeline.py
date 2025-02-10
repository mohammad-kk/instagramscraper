import os
import json
from datetime import datetime
from dotenv import load_dotenv
from .api_call import InstagramAPI
from .instagram_parser import parse_instagram_profile, save_profile_data

# Load environment variables
load_dotenv()

class InstagramPipeline:
    def __init__(self, api_key=None, max_requests=10):
        self.api_key = api_key or os.getenv('INSTAGRAM_API_KEY')
        if not self.api_key:
            raise ValueError("No API key provided. Set INSTAGRAM_API_KEY in .env file")
        
        self.api = InstagramAPI(self.api_key, max_requests=max_requests)
        
    def fetch_raw_data(self, username, api_version='profile'):
        """Fetch raw data from Instagram API and save to raw_data directory"""
        # Update the raw_data directory path
        base_raw_dir = '/Users/mohammadkhan/punkhazard2/instagramapi/instagramscraper/raw_data'
        api_dir = os.path.join(base_raw_dir, api_version)
        user_file = os.path.join(api_dir, f"{username}.json")

        if os.path.exists(user_file):
            print(f"\nData already exists for {username} in {api_version} API")
            return user_file

        print(f"\n=== Fetching {api_version} data for {username} ===")
        
        data = self.api.fetch_profile(username, max_depth=0) if api_version == 'profile' else self.api.fetch_posts(username)
            
        if not data:
            print(f"Failed to fetch {api_version} data for {username}")
            return None
            
        os.makedirs(api_dir, exist_ok=True)
        
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print(f"Saved {api_version} data for {username} to: {user_file}")
        return user_file

    def analyze_profile(self, username):
        """Analyze raw data for a given username"""
        # Check if processed data already exists
        profile_path = os.path.join('/Users/mohammadkhan/punkhazard2/instagramapi/profiles', f"{username}.json")
        # if os.path.exists(profile_path):
        #     print(f"\nProcessed data already exists for {username}")
        #     with open(profile_path, 'r', encoding='utf-8') as f:
        #         parsed_data = json.load(f)
        #         return {
        #             'username': parsed_data['profile']['username'],
        #             'output_file': profile_path,
        #             'profile_data': parsed_data['profile'],
        #             'related_profiles': parsed_data.get('related_profiles', [])
        #         }

        # If no processed data exists, continue with fetching and processing
        raw_file = self.fetch_raw_data(username)
        if not raw_file:
            print(f"No raw data available for {username}")
            return None

        try:
            parsed_data = parse_instagram_profile(raw_file)
            output_file = save_profile_data(parsed_data)
            
            result = {
                'username': parsed_data['profile']['username'],
                'output_file': output_file,
                'profile_data': parsed_data['profile'],
                'related_profiles': parsed_data.get('related_profiles', [])
            }
            
            print(f"\n=== Profile Analysis for {username} ===")
            print(f"Profile saved to: {output_file}")
            print(f"Followers: {result['profile_data']['followers']}")
            print(f"Following: {result['profile_data']['following']}")
            print(f"Related profiles found: {len(result['related_profiles'])}")
            
            return result
            
        except Exception as e:
            print(f"Error analyzing profile for {username}: {str(e)}")
            return None