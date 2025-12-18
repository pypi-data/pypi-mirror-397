"""
Media Service Managers.

This package contains service managers for various media playback technologies.
"""

from .vlc_service import VLCService
from .earth_viz_service import EarthVizService

__all__ = ['VLCService', 'EarthVizService']
