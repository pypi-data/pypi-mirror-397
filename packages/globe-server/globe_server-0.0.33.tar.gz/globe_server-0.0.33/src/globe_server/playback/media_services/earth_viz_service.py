"""
Earth-Viz Service Manager.

This module handles Earth-Viz browser process management and API configuration.
"""

import logging
import subprocess
from typing import Optional

from globe_server.db.schemas import PlanetOptions, PlanetName, WeatherOverlay, AirLevel
from earth_viz_backend.earth_control import (
    set_projection, 
    set_planet_mode, 
    set_air_mode, 
    hideUI,
    enable_full_screen,
    await_earth_connection
)

class EarthVizService:
    """Manages Earth-Viz browser process and API configuration."""
    
    def __init__(self, earth_viz_url: str = "http://localhost:8000/earth-viz-app/"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.process: Optional[subprocess.Popen] = None
        self.earth_viz_url = earth_viz_url
    
    def is_running(self) -> bool:
        """Check if browser process is running."""
        return self.process is not None and self.process.poll() is None
    
    def start_browser(self) -> bool:
        """Start browser with earth-viz URL in kiosk mode."""
        try:
            # Kill any existing browser process
            self.stop()
            
            # Detect OS and build appropriate command
            import platform
            import os
            system = platform.system().lower()
            self.logger.info(f"Detected OS: {system}")
            
            if system == 'windows':
                # Find Chrome on Windows
                chrome_paths = [
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\Application\\chrome.exe'),
                ]
                
                browser_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        browser_path = path
                        break
                
                if not browser_path:
                    self.logger.error("Chrome not found on Windows")
                    return False
                
                cmd = [
                    browser_path,
                    '--kiosk',
                    '--noerrdialogs',
                    '--disable-infobars',
                    '--no-first-run',
                    self.earth_viz_url
                ]
            else:
                # Linux (Raspberry Pi) - use chromium-browser
                cmd = [
                    'chromium',
                    '--kiosk',
                    '--noerrdialogs',
                    '--disable-infobars',
                    '--no-first-run',
                    '--check-for-update-interval=31536000',
                    self.earth_viz_url
                ]
            
            # Start browser process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"Started earth-viz browser on {system} (PID: {self.process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting earth-viz browser: {e}")
            return False
    
    async def configure_for_planet(self, planet_opts: Optional[PlanetOptions] = None) -> bool:
        """Start browser and configure earth-viz for planet visualization."""
        try:
            # Start browser
            if not self.start_browser():
                self.logger.error("Failed to start earth-viz browser")
                return False
            
            self.logger.info("Waiting for earth-viz client to connect...")
            if not await await_earth_connection(timeout=15.0):
                self.logger.error("Earth-viz client did not connect within 15 seconds")
                return False
            
            self.logger.info("Earth-viz client connected, configuring...")
                
            # Use default options if none are provided
            opts = planet_opts or PlanetOptions(planet_name=PlanetName.EARTH)
            
            # Configure earth-viz
            await hideUI()
            await set_projection('equirectangular')
            await enable_full_screen()
            await set_planet_mode(opts.planet_name.value)
            
            self.logger.info(f"Successfully configured earth-viz for planet mode: {opts.planet_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring earth-viz for planet visualization: {e}")
            return False
    
    async def configure_for_weather(self, weather_opts: Optional[PlanetOptions] = None) -> bool:
        """Start browser and configure earth-viz for weather visualization."""
        try:
            # Start browser
            if not self.start_browser():
                self.logger.error("Failed to start earth-viz browser")
                return False
            
            self.logger.info("Waiting for earth-viz client to connect...")
            if not await await_earth_connection(timeout=15.0):
                self.logger.error("Earth-viz client did not connect within 15 seconds")
                return False
            
            self.logger.info("Earth-viz client connected, configuring...")
            
            # Use safe defaults if options are missing
            level = weather_opts.level.value if weather_opts and weather_opts.level else AirLevel.SURFACE.value
            overlay = weather_opts.overlay.value if weather_opts and weather_opts.overlay else WeatherOverlay.WIND.value
            
            # Configure earth-viz
            await hideUI()
            await set_projection('equirectangular')
            await enable_full_screen()
            await set_air_mode(level, 'wind', overlay)
            
            self.logger.info(f"Successfully configured earth-viz for weather mode: level={level}, overlay={overlay}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring earth-viz for weather visualization: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop browser process."""
        try:
            if self.is_running():
                self.logger.info(f"Stopping earth-viz browser (PID: {self.process.pid})")
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Browser didn't terminate gracefully, killing...")
                    self.process.kill()
                    self.process.wait()
                self.process = None
                self.logger.info("Earth-viz browser stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping earth-viz browser: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up earth-viz resources."""
        self.stop()
        self.logger.info("Earth-viz service cleaned up")