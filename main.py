from core.pipeline import InstagramPipeline
from instagram_parser import parse_instagram_profile, save_profile_data
import os  # Add this line

def main():
    # Process tonysharrk profile directly from raw data
    raw_file = '/Users/mohammadkhan/punkhazard2/instagramapi/raw_data/profile/tonysharrk.json'
    print(f"Reading from raw file: {raw_file}")
    print(f"File exists: {os.path.exists(raw_file)}")  # Add this line
    
    result = parse_instagram_profile(raw_file)
    print(f"Parsed result has {len(result.get('image_posts', []))} posts")  # Add this line
    
    # Save processed data
    output_file = save_profile_data(result)
    print(f"Output saved to: {output_file}")
    print(f"Output file exists: {os.path.exists(output_file)}")  # Add this line
    
    # Print detailed results
    print("\n=== Profile Info ===")
    print(f"Username: {result['profile']['username']}")
    print(f"Full Name: {result['profile']['full_name']}")
    print(f"Bio: {result['profile']['biography']}")
    print(f"Followers: {result['profile']['followers']:,}")
    print(f"Following: {result['profile']['following']:,}")
    
    print("\n=== Posts Summary ===")
    post_types = {}
    for post in result['image_posts']:
        post_types[post['type']] = post_types.get(post['type'], 0) + 1
    
    print(f"Total Posts: {len(result['image_posts'])}")
    for type_name, count in post_types.items():
        print(f"{type_name}: {count}")
    
    print("\n=== Recent Posts ===")
    for post in result['image_posts'][:5]:  # Show first 5 posts
        print(f"\nType: {post['type']}")
        print(f"Likes: {post['likes']:,}")
        print(f"Comments: {post['comments']:,}")
        if post['location']:
            print(f"Location: {post['location']}")
        if 'children' in post:
            print(f"Number of images: {len(post['children'])}")
        print(f"Caption: {post['caption'][:100]}..." if post['caption'] else "No caption")

# Comment out the graph pipeline code for now
'''
import signal
import sys
from core.graph_pipeline import InstagramGraphPipeline

def signal_handler(signum, frame):
    print("\n\nReceived interrupt signal. Gracefully shutting down...")
    sys.exit(0)

def main():
    # Set up signal handler for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, signal_handler)
    
    pipeline = InstagramGraphPipeline(max_depth=2)  # Process up to 2 levels deep
    username = "noplansco"
    
    try:
        results = pipeline.process_profile_graph(username)
        
        print("\n=== Final Results ===")
        print(f"Total profiles processed: {len(results)}")
        
        # Print details for each processed profile
        for username, result in results.items():
            print(f"\nProfile: {username}")
            print(f"Followers: {result['profile_data']['followers']}")
            print(f"Following: {result['profile_data']['following']}")
            print(f"Related profiles: {len(result['related_profiles'])}")

        # Print final stats
        stats = pipeline.get_graph_stats()
        print("\n=== Graph Statistics ===")
        print(f"Total profiles processed: {stats['total_profiles_processed']}")
        print(f"API requests made: {stats['api_stats']['requests_made']}")
        print(f"API requests remaining: {stats['api_stats']['requests_remaining']}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Shutting down...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nExiting program.")

if __name__ == "__main__":
    main()
'''