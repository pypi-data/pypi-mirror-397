"""
Workflow LLM Response Cache
Caches LLM responses to improve workflow execution speed on repeated runs.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

import aiofiles


class WorkflowCache:
    """Cache for workflow LLM responses with TTL support."""
    
    def __init__(self, cache_dir: str = None, ttl_hours: int = 24):
        """
        Initialize workflow cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.lmapp/workflow_cache
            ttl_hours: Time-to-live for cache entries in hours. Default 24 hours.
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.lmapp/workflow_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        
    def _generate_key(self, workflow_name: str, step: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """
        Generate cache key from workflow name, step, and variables.
        
        Args:
            workflow_name: Name of the workflow
            step: Workflow step dictionary
            variables: Current workflow variables
            
        Returns:
            SHA256 hash as hex string
        """
        # Create deterministic representation
        cache_input = {
            "workflow": workflow_name,
            "action": step.get("action"),
            "prompt": step.get("prompt", ""),
            "variables": sorted(variables.items())  # Sort for consistency
        }
        
        # Generate hash
        content = json.dumps(cache_input, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get(self, workflow_name: str, step: Dict[str, Any], variables: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve cached response if available and not expired.
        
        Args:
            workflow_name: Name of the workflow
            step: Workflow step dictionary
            variables: Current workflow variables
            
        Returns:
            Cached response string or None if not found/expired
        """
        key = self._generate_key(workflow_name, step, variables)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            async with aiofiles.open(cache_file, 'r') as f:
                content = await f.read()
                cache_data = json.loads(content)
            
            # Check expiration
            age_seconds = time.time() - cache_data.get("timestamp", 0)
            if age_seconds > self.ttl_seconds:
                # Expired, remove it
                cache_file.unlink()
                return None
            
            return cache_data.get("response")
            
        except (json.JSONDecodeError, IOError, KeyError):
            # Corrupted cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    async def set(self, workflow_name: str, step: Dict[str, Any], variables: Dict[str, Any], response: str):
        """
        Store response in cache.
        
        Args:
            workflow_name: Name of the workflow
            step: Workflow step dictionary
            variables: Current workflow variables
            response: LLM response to cache
        """
        key = self._generate_key(workflow_name, step, variables)
        cache_file = self.cache_dir / f"{key}.json"
        
        cache_data = {
            "workflow": workflow_name,
            "timestamp": time.time(),
            "response": response,
            "variables": variables
        }
        
        try:
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(cache_data, indent=2))
        except IOError as e:
            # Cache write failed, log but don't crash
            print(f"Warning: Failed to write cache: {e}")
    
    def clear_expired(self):
        """Remove all expired cache entries."""
        now = time.time()
        removed_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                age_seconds = now - cache_data.get("timestamp", 0)
                if age_seconds > self.ttl_seconds:
                    cache_file.unlink()
                    removed_count += 1
                    
            except (json.JSONDecodeError, IOError, KeyError):
                # Corrupted, remove it
                cache_file.unlink(missing_ok=True)
                removed_count += 1
        
        return removed_count
    
    def clear_all(self):
        """Remove all cache entries."""
        removed_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            removed_count += 1
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats (total_entries, total_size_mb, oldest_entry_age_hours)
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        oldest_timestamp = time.time()
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    timestamp = cache_data.get("timestamp", time.time())
                    oldest_timestamp = min(oldest_timestamp, timestamp)
            except (json.JSONDecodeError, IOError, KeyError):
                continue
        
        oldest_age_hours = (time.time() - oldest_timestamp) / 3600 if cache_files else 0
        
        return {
            "total_entries": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_entry_age_hours": round(oldest_age_hours, 1)
        }
