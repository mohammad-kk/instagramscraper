from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from core.pipeline import InstagramPipeline
import os
import json
import requests
from urllib.parse import urlparse

app = Flask(__name__)
pipeline = InstagramPipeline()

# Add configuration for profiles directory
# Update the PROFILES_DIR path
PROFILES_DIR = '/Users/mohammadkhan/punkhazard2/instagramapi/instagramscraper/profiles'

@app.route('/')
def index():
    # Get list of processed profiles
    profiles = []
    if os.path.exists(PROFILES_DIR):
        for filename in os.listdir(PROFILES_DIR):
            if filename.endswith('.json'):
                profile_path = os.path.join(PROFILES_DIR, filename)
                with open(profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profiles.append({
                        'username': data['profile']['username'],
                        'followers': data['profile']['followers'],
                        'last_updated': data.get('last_updated', 'Unknown')
                    })
    
    # Sort profiles by follower count
    profiles.sort(key=lambda x: x['followers'], reverse=True)
    return render_template('index.html', saved_profiles=profiles)

@app.route('/profile/<username>')
def view_profile(username):
    profile_path = os.path.join(PROFILES_DIR, f"{username}.json")
    
    if not os.path.exists(profile_path):
        return render_template('index.html', error=f'Profile not found: {username}')
        
    with open(profile_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get list of all profiles for the sidebar
    profiles = []
    if os.path.exists(PROFILES_DIR):
        for filename in os.listdir(PROFILES_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(PROFILES_DIR, filename), 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    profiles.append({
                        'username': profile_data['profile']['username'],
                        'followers': profile_data['profile']['followers'],
                        'last_updated': profile_data.get('last_updated', 'Unknown')
                    })
    
    profiles.sort(key=lambda x: x['followers'], reverse=True)
    
    return render_template('profile.html', 
                         profile=data['profile'],
                         related_profiles=data['related_profiles'],
                         image_posts=data.get('image_posts', []),
                         last_updated=data.get('last_updated', 'Unknown'),
                         saved_profiles=profiles)

@app.route('/process', methods=['POST'])
def process_profile():
    username = request.form.get('username')
    if not username:
        return render_template('index.html', error='Username is required')
    
    try:
        # Clean up username (remove @ if present and whitespace)
        username = username.strip().lstrip('@')
        
        print(f"Processing profile for: {username}")
        result = pipeline.analyze_profile(username)
        
        if result:
            print(f"Successfully processed profile: {username}")
            return redirect(url_for('view_profile', username=username))
        else:
            print(f"Failed to process profile: {username}")
            return render_template('index.html', 
                                error='Failed to fetch profile data. Please check the username and try again.')
    except Exception as e:
        print(f"Error processing profile {username}: {str(e)}")
        return render_template('index.html', 
                             error=f'An error occurred: {str(e)}')

@app.route('/proxy_image')
def proxy_image():
    """Proxy route to handle Instagram image requests"""
    image_url = request.args.get('url')
    if not image_url:
        return 'No URL provided', 400
    
    try:
        # Forward the request to Instagram's servers
        response = requests.get(image_url)
        return response.content, 200, {
            'Content-Type': response.headers['Content-Type'],
            'Cache-Control': 'public, max-age=31536000'  # Cache for 1 year
        }
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')