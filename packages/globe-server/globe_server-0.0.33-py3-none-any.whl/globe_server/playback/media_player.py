import logging
import json
from typing import Optional
from .media_services import VLCService, EarthVizService
from globe_server.db.schemas import PlanetOptions
from globe_server.db.orm import Media

class MediaPlayer:
    """Handles media playback using process-based approach (kill/restart)."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create media service managers (each manages its own process)
        self.vlc_service = VLCService()
        self.earth_viz_service = EarthVizService()
        
        self.logger.info("MediaPlayer initialized with process-based architecture")
        
    async def initialize_services(self):
        """Initialize all media services."""
        self.logger.info("Initializing media services...")
        # Services are initialized on-demand when playing media
        self.logger.info("All media services initialized successfully")
        return True

    async def play(self, media_id: int) -> bool:
        """Play a media item."""
        try:
            # Get media info from database
            from globe_server.db.database import get_by_id
            media_info = get_by_id(Media, media_id)
            if not media_info:
                self.logger.error(f"Media item {media_id} not found")
                return False

            filepath = media_info.filepath
            mediatype = media_info.type
            
            # Play based on media type
            if mediatype in ["image", "video"]:
                return self._play_vlc_media(filepath, mediatype)
            
            elif mediatype in ["planet", "weather"]:
                # Parse options for earth-viz (already validated in DB)
                opts = None
                if media_info.planet_options:
                    try:
                        opts_dict = json.loads(media_info.planet_options)
                        opts = PlanetOptions(**opts_dict)
                    except Exception as e:
                        self.logger.error(f"Failed to parse planet_options: {e}")
                        return False
                
                return await self._play_earth_viz(mediatype, opts)
            
            else:
                self.logger.error(f"Unsupported media type: {mediatype}")
                return False

        except Exception as e:
            self.logger.error(f"Error in play(): {e}")
            return False

    def _play_vlc_media(self, filepath: str, mediatype: str) -> bool:
        """Play video or image using VLC service."""
        try:
            # Kill earth-viz if running
            self.earth_viz_service.stop()
            
            # Start VLC (kills any existing VLC process first)
            if self.vlc_service.play_media(filepath):
                self.logger.info(f"Started VLC {mediatype} playback")
                return True
            else:
                self.logger.error(f"Failed to start VLC {mediatype} playback")
                return False
            
        except Exception as e:
            self.logger.error(f"Error playing {mediatype} with VLC: {e}")
            return False

    async def _play_earth_viz(self, mode: str, opts: Optional[PlanetOptions]) -> bool:
        """Play earth-viz visualization (planet or weather)."""
        try:
            self.logger.info(f"Starting earth-viz {mode} visualization with options: {opts}")
            
            # Kill VLC if running
            self.vlc_service.stop()
            
            # Configure earth-viz (starts browser and configures)
            if mode == "planet":
                success = await self.earth_viz_service.configure_for_planet(opts)
            elif mode == "weather":
                success = await self.earth_viz_service.configure_for_weather(opts)
            else:
                self.logger.error(f"Unknown earth-viz mode: {mode}")
                return False
            
            if success:
                self.logger.info(f"Successfully configured earth-viz for {mode} mode")
                return True
            else:
                self.logger.error(f"Failed to configure earth-viz for {mode} mode")
                return False
            
        except Exception as e:
            self.logger.error(f"Error starting earth-viz visualization: {e}")
            return False

    def stop(self):
        """Stop playback and clean up resources."""
        self.logger.info("Stopping playback...")
        
        # Stop both services
        self.vlc_service.stop()
        self.earth_viz_service.stop()
        
    def pause(self):
        """Pause not supported in process-based approach."""
        self.logger.warning("Pause not supported in process-based playback")
        return False

    def resume(self):
        """Resume not supported in process-based approach."""
        self.logger.warning("Resume not supported in process-based playback")
        return False
        
    def cleanup(self):
        """Clean up all media services and resources."""
        self.logger.info("Cleaning up media services...")
        
        # Cleanup services
        if hasattr(self, 'vlc_service'):
            self.vlc_service.cleanup()
            
        if hasattr(self, 'earth_viz_service'):
            self.earth_viz_service.cleanup()