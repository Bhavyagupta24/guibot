import json
import os
from typing import Optional, Dict, List
import discord

class EmbedStorage:
    """
    Manages guild-wise embed storage using JSON files.
    Each guild has its own file: data/embeds_{guild_id}.json
    """
    
    def __init__(self):
        self.data_dir = "data"
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_guild_file(self, guild_id: int) -> str:
        """Get the file path for a guild's embeds."""
        return os.path.join(self.data_dir, f"embeds_{guild_id}.json")
    
    def _load_guild_data(self, guild_id: int) -> Dict:
        """Load all embeds for a guild."""
        file_path = self._get_guild_file(guild_id)
        
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_guild_data(self, guild_id: int, data: Dict) -> bool:
        """Save all embeds for a guild."""
        file_path = self._get_guild_file(guild_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving guild data: {e}")
            return False
    
    def save_embed(self, guild_id: int, embed_name: str, embed_state: Dict) -> bool:
        """
        Save an embed for a specific guild.
        
        Args:
            guild_id: Discord guild ID
            embed_name: Name of the embed
            embed_state: Dictionary containing embed data
        
        Returns:
            True if successful, False otherwise
        """
        guild_data = self._load_guild_data(guild_id)
        guild_data[embed_name] = embed_state
        return self._save_guild_data(guild_id, guild_data)
    
    def load_embed(self, guild_id: int, embed_name: str) -> Optional[Dict]:
        """
        Load a specific embed from a guild.
        
        Args:
            guild_id: Discord guild ID
            embed_name: Name of the embed
        
        Returns:
            Embed state dictionary or None if not found
        """
        guild_data = self._load_guild_data(guild_id)
        return guild_data.get(embed_name)
    
    def delete_embed(self, guild_id: int, embed_name: str) -> bool:
        """
        Delete a specific embed from a guild.
        
        Args:
            guild_id: Discord guild ID
            embed_name: Name of the embed
        
        Returns:
            True if deleted, False if not found
        """
        guild_data = self._load_guild_data(guild_id)
        
        if embed_name in guild_data:
            del guild_data[embed_name]
            self._save_guild_data(guild_id, guild_data)
            return True
        
        return False
    
    def list_embeds(self, guild_id: int) -> List[str]:
        """
        Get list of all saved embed names for a guild.
        
        Args:
            guild_id: Discord guild ID
        
        Returns:
            List of embed names
        """
        guild_data = self._load_guild_data(guild_id)
        return list(guild_data.keys())
    
    def embed_exists(self, guild_id: int, embed_name: str) -> bool:
        """
        Check if an embed exists for a guild.
        
        Args:
            guild_id: Discord guild ID
            embed_name: Name of the embed
        
        Returns:
            True if exists, False otherwise
        """
        guild_data = self._load_guild_data(guild_id)
        return embed_name in guild_data