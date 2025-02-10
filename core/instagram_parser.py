import json
import os
from datetime import datetime

# Update the output_dir default value
def save_profile_data(result, output_dir='/Users/mohammadkhan/punkhazard2/instagramapi/instagramscraper/profiles'):
    os.makedirs(output_dir, exist_ok=True)
    
    username = result['profile']['username']
    filename = f"{username}.json"
    output_path = os.path.join(output_dir, filename)
    
    # Add timestamp to the data instead of filename
    result['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Profile saved to: {output_path}")
    return output_path

def parse_instagram_profile(raw_file):
    """Parse raw Instagram data into our profile format"""
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    if 'data' not in raw_data or 'user' not in raw_data['data']:
        raise ValueError(f"Invalid data format in {raw_file}")
        
    user_data = raw_data['data']['user']
    
    print(f"\nParsing profile data:")
    print(f"Username: {user_data.get('username')}")
    
    # Extract image posts and GraphSidecar with images
    image_posts = []
    if 'edge_owner_to_timeline_media' in user_data:
        edges = user_data['edge_owner_to_timeline_media'].get('edges', [])
        print(f"Found {len(edges)} total posts")
        
        for edge in edges:
            node = edge.get('node', {})
            typename = node.get('__typename')
            
            # Process both GraphImage and GraphSidecar types
            if typename in ['GraphImage', 'GraphSidecar']:
                caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                caption = caption_edges[0]['node']['text'] if caption_edges else ''
                
                post = {
                    'type': typename,
                    'shortcode': node.get('shortcode', ''),
                    'display_url': node.get('display_url', ''),
                    'timestamp': node.get('taken_at_timestamp', 0),
                    'caption': caption,
                    'likes': node.get('edge_liked_by', {}).get('count', 0),
                    'location': node.get('location', {}).get('name') if node.get('location') else None
                }
                
                # For GraphSidecar, include children images
                if typename == 'GraphSidecar' and 'edge_sidecar_to_children' in node:
                    post['children'] = [
                        {
                            'type': child['node'].get('__typename'),
                            'display_url': child['node'].get('display_url')
                        }
                        for child in node['edge_sidecar_to_children']['edges']
                        if child['node'].get('__typename') == 'GraphImage'
                    ]
                
                image_posts.append(post)
        
        # Sort posts by likes in descending order
        image_posts.sort(key=lambda x: x['likes'], reverse=True)
        print(f"Processed {len(image_posts)} image posts")

    # Extract related profiles
    related_profiles = []
    if 'edge_related_profiles' in user_data:
        edges = user_data['edge_related_profiles'].get('edges', [])
        print(f"Found {len(edges)} related profiles")
        related_profiles = [
            {
                'username': edge['node'].get('username', ''),
                'full_name': edge['node'].get('full_name', ''),
                'is_private': edge['node'].get('is_private', False),
                'is_verified': edge['node'].get('is_verified', False),
                'profile_pic_url': edge['node'].get('profile_pic_url', '')
            }
            for edge in edges
        ]

    # Create profile structure
    profile = {
        'profile': {
            'username': user_data.get('username', ''),
            'full_name': user_data.get('full_name', ''),
            'biography': user_data.get('biography', ''),
            'followers': user_data.get('edge_followed_by', {}).get('count', 0),
            'following': user_data.get('edge_follow', {}).get('count', 0),
            'is_private': user_data.get('is_private', False),
            'is_verified': user_data.get('is_verified', False)
        },
        'related_profiles': related_profiles,
        'image_posts': image_posts
    }
    
    return profile

# Update the print section to show likes count more prominently
if __name__ == "__main__":
    json_file = '/Users/mohammadkhan/punkhazard2/instagramapi/yifd3s.json'
    result = parse_instagram_profile(json_file)
    
    # Save to file
    output_file = save_profile_data(result)
    print(f"\nData saved to: {output_file}")
    
    # Print profile info
    print("\n=== Profile Info ===")
    print(f"Username: {result['profile']['username']}")
    print(f"Full Name: {result['profile']['full_name']}")
    print(f"Bio: {result['profile']['biography']}")
    print(f"Followers: {result['profile']['followers']}")
    print(f"Following: {result['profile']['following']}")
    print(f"Private: {result['profile']['is_private']}")
    print(f"Verified: {result['profile']['is_verified']}")
    
    print("\n=== Related Profiles ===")
    for profile in result['related_profiles']:
        print(f"\nUsername: {profile['username']}")
        print(f"Full Name: {profile['full_name']}")
        print(f"Private: {profile['is_private']}")
        print(f"Verified: {profile['is_verified']}")
    
    print("\n=== Image Posts (Sorted by Likes) ===")
    for post in result['image_posts']:
        print("\nPost:")
        print(f"Likes: {post['likes']:,}")  # Added comma formatting for readability
        print(f"Type: {post['type']}")
        print(f"Caption: {post['caption'][:100]}...")