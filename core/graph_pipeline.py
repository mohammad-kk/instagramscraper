from collections import deque
from datetime import datetime
import os
from .pipeline import InstagramPipeline

class InstagramGraphPipeline(InstagramPipeline):
    def __init__(self, api_key=None, max_requests=10, max_depth=2):
        super().__init__(api_key, max_requests)
        self.processed_nodes = set()
        self.max_depth = max_depth
        
    def process_profile_graph(self, root_username):
        """Process profiles in a graph structure using BFS"""
        queue = deque([(root_username, 0)])  # (username, depth)
        results = {}
        
        while queue:
            username, depth = queue.popleft()
            
            # Skip if already processed or exceeded max depth
            if username in self.processed_nodes or depth > self.max_depth:
                continue
                
            print(f"\n=== Processing {username} at depth {depth} ===")
            
            # Process current profile
            result = self.analyze_profile(username)
            if not result:
                continue
                
            self.processed_nodes.add(username)
            results[username] = result
            
            # Add related profiles to queue if within depth limit
            if depth < self.max_depth:
                for related in result['related_profiles']:
                    related_username = related['username']
                    if related_username not in self.processed_nodes:
                        queue.append((related_username, depth + 1))
                        
            # Print progress
            print(f"Processed nodes: {len(self.processed_nodes)}")
            print(f"Remaining in queue: {len(queue)}")
            
        return results

    def get_graph_stats(self):
        """Get statistics about the processed graph"""
        return {
            "total_profiles_processed": len(self.processed_nodes),
            "processed_usernames": list(self.processed_nodes),
            "api_stats": self.api.get_stats()
        }