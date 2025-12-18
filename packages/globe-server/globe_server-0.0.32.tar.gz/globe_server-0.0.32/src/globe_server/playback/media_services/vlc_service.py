"""
VLC Service Manager.

This module handles VLC playback using python-vlc library.
"""

import logging
import time
import vlc
from typing import Optional, Any

class VLCService:
    """Manages VLC media player using python-vlc."""
    
    def __init__(self):
        self.vlc_instance: Optional[Any] = None
        self.vlc_player: Optional[Any] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def is_running(self) -> bool:
        """Check if VLC is running."""
        return self.vlc_instance is not None and self.vlc_player is not None
    
    def play_media(self, filepath: str, duration: Optional[int] = None) -> bool:
        """Play media file using VLC in fullscreen."""
        try:
            # Stop any existing playback
            self.stop()
            
            # Create VLC instance and player
            self.vlc_instance = vlc.Instance('--no-audio')
            self.vlc_player = self.vlc_instance.media_player_new()
            
            # Set fullscreen mode
            self.vlc_player.set_fullscreen(True)
            
            # Set up media with optional duration (useful for images)
            if duration:
                media = self.vlc_instance.media_new(filepath, f':duration={duration}')
            else:
                media = self.vlc_instance.media_new(filepath)
            
            self.vlc_player.set_media(media)
            
            # Start playback
            self.vlc_player.play()
            
            self.logger.info(f"Started VLC playback of {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting VLC playback: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop VLC playback and release resources."""
        try:
            if self.vlc_player:
                self.vlc_player.stop()
                self.vlc_player.release()
                self.vlc_player = None
            
            if self.vlc_instance:
                self.vlc_instance.release()
                self.vlc_instance = None
            
            self.logger.info("VLC playback stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping VLC: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause the current playback."""
        try:
            if not self.vlc_player:
                self.logger.info("No VLC player found")
                return False
            
            # Get current state before pause
            current_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state before pause: {current_state}")
            
            # Pause
            self.vlc_player.set_pause(1)
            
            # Give VLC a moment to process
            time.sleep(0.1)
            
            # Verify state after pause
            new_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state after pause: {new_state}")
            
            if new_state == vlc.State.Playing:
                self.logger.error("Failed to pause VLC playback")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error pausing VLC: {e}")
            return False
    
    def resume(self) -> bool:
        """Resume the current playback."""
        try:
            if not self.vlc_player:
                self.logger.info("No VLC player found")
                return False
            
            # Get current state before resume
            current_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state before resume: {current_state}")
            
            # Resume
            self.vlc_player.set_pause(0)
            
            # Give VLC a moment to process
            time.sleep(0.1)
            
            # Verify state after resume
            new_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state after resume: {new_state}")
            
            if new_state == vlc.State.Paused:
                self.logger.error("Failed to resume VLC playback")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resuming VLC: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up VLC resources."""
        self.stop()
        self.logger.info("VLC service cleaned up")
