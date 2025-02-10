import json
from instagram_parser import parse_instagram_profile, save_profile_data  # Fixed the import path

def process_tonysharrk():
    # Input and output paths
    raw_file = '/Users/mohammadkhan/punkhazard2/instagramapi/raw_data/profile/tonysharrk.json'
    
    print(f"Processing tonysharrk profile...")
    print(f"Reading from: {raw_file}")
    
    # Parse the profile
    try:
        result = parse_instagram_profile(raw_file)
        
        # Save the processed data
        output_file = save_profile_data(result)
        
        # Print summary
        print("\n=== Processing Summary ===")
        print(f"Username: {result['profile']['username']}")
        print(f"Followers: {result['profile']['followers']:,}")
        print(f"Following: {result['profile']['following']:,}")
        print(f"Total posts processed: {len(result['image_posts'])}")
        print(f"\nOutput saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing profile: {str(e)}")

if __name__ == "__main__":
    process_tonysharrk()