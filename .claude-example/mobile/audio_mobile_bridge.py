#!/usr/bin/env python3
"""
Mobile Audio Bridge for Claude Code Dev Stack
Cross-platform mobile audio integration with phase-aware notifications
"""

import os
import sys
import json
import time
import platform
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Mobile-specific imports
try:
    if platform.system() == "Android":
        # Android-specific audio
        import android_audio
    elif platform.system() == "iOS":
        # iOS-specific audio
        import ios_audio
    else:
        # Desktop mobile emulation
        pass
except ImportError:
    # Fallback for development
    pass

class MobileAudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    OGG = "ogg"

class MobilePlatform(Enum):
    ANDROID = "android"
    IOS = "ios"
    WINDOWS_MOBILE = "windows_mobile"
    DESKTOP_EMULATION = "desktop_emulation"

@dataclass
class MobileAudioEvent:
    event_id: str
    timestamp: float
    audio_file: str
    volume: float
    priority: int
    vibration: bool = False
    notification: bool = False
    metadata: Dict[str, Any] = None

class MobileAudioBridge:
    """
    Bridge between Claude Code audio system and mobile platforms
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.audio_dir = self.base_dir.parent / "Claude_Code_Dev_Stack_v3" / "core" / "audio" / "audio"
        self.config_dir = self.base_dir / "config"
        self.cache_dir = self.base_dir / "cache"
        
        # Create directories
        for dir_path in [self.config_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Detect mobile platform
        self.platform = self._detect_mobile_platform()
        
        # Load configuration
        self.config = self._load_mobile_config()
        
        # Audio event queue
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # Background processor
        self.processor_thread = None
        self.running = False
        
        # Audio cache
        self.audio_cache = {}
        
        print(f"Mobile Audio Bridge initialized for {self.platform.value}")
        self._start_background_processor()
    
    def _detect_mobile_platform(self) -> MobilePlatform:
        """Detect the current mobile platform"""
        system = platform.system().lower()
        
        if "android" in system:
            return MobilePlatform.ANDROID
        elif "darwin" in system and "iphone" in platform.platform().lower():
            return MobilePlatform.IOS
        elif "windows" in system and "mobile" in platform.platform().lower():
            return MobilePlatform.WINDOWS_MOBILE
        else:
            return MobilePlatform.DESKTOP_EMULATION
    
    def _load_mobile_config(self) -> Dict[str, Any]:
        """Load mobile-specific configuration"""
        config_file = self.config_dir / "mobile_audio_config.json"
        
        default_config = {
            "enabled": True,
            "volume": 0.7,
            "vibration_enabled": True,
            "notification_enabled": True,
            "battery_optimization": True,
            "offline_mode": True,
            "audio_formats": {
                "primary": "wav",
                "fallback": ["mp3", "m4a"],
                "compression": "medium"
            },
            "platform_settings": {
                "android": {
                    "use_media_player": True,
                    "use_notification_sounds": True,
                    "respect_do_not_disturb": True
                },
                "ios": {
                    "use_av_audio_player": True,
                    "haptic_feedback": True,
                    "background_audio": False
                },
                "desktop_emulation": {
                    "simulate_mobile": True,
                    "test_mode": True
                }
            },
            "network": {
                "sync_enabled": True,
                "offline_cache_size_mb": 50,
                "download_on_wifi_only": True
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading mobile config: {e}, using defaults")
        else:
            # Save default config
            try:
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                print(f"Error saving default config: {e}")
        
        return default_config
    
    def _start_background_processor(self):
        """Start background event processor"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_mobile_events, daemon=True)
        self.processor_thread.start()
    
    def _process_mobile_events(self):
        """Process mobile audio events in background"""
        while self.running:
            try:
                with self.queue_lock:
                    if self.event_queue:
                        event = self.event_queue.pop(0)
                        self._handle_mobile_audio_event(event)
                
                time.sleep(0.1)  # Prevent busy waiting
            except Exception as e:
                if self.config.get("debug_mode"):
                    print(f"Mobile audio processor error: {e}")
    
    def _handle_mobile_audio_event(self, event: MobileAudioEvent):
        """Handle a mobile audio event"""
        try:
            if not self.config.get("enabled", True):
                return
            
            # Check battery optimization
            if self.config.get("battery_optimization") and self._is_low_battery():
                return
            
            # Get audio file
            audio_file = self._get_audio_file(event.audio_file)
            if not audio_file:
                return
            
            # Play audio based on platform
            if self.platform == MobilePlatform.ANDROID:
                self._play_android_audio(audio_file, event)
            elif self.platform == MobilePlatform.IOS:
                self._play_ios_audio(audio_file, event)
            elif self.platform == MobilePlatform.WINDOWS_MOBILE:
                self._play_windows_mobile_audio(audio_file, event)
            else:
                self._play_desktop_emulation_audio(audio_file, event)
            
            # Handle vibration
            if event.vibration and self.config.get("vibration_enabled"):
                self._trigger_vibration(event.priority)
            
            # Handle notification
            if event.notification and self.config.get("notification_enabled"):
                self._show_notification(event)
                
        except Exception as e:
            if self.config.get("debug_mode"):
                print(f"Error handling mobile audio event: {e}")
    
    def _get_audio_file(self, filename: str) -> Optional[Path]:
        """Get audio file with caching and format conversion"""
        
        # Check cache first
        if filename in self.audio_cache:
            cached_file = Path(self.audio_cache[filename])
            if cached_file.exists():
                return cached_file
        
        # Find original file
        original_file = self.audio_dir / filename
        if not original_file.exists():
            # Try different extensions
            base_name = filename.rsplit('.', 1)[0]
            for ext in ['.wav', '.mp3', '.m4a', '.ogg']:
                test_file = self.audio_dir / f"{base_name}{ext}"
                if test_file.exists():
                    original_file = test_file
                    break
        
        if not original_file.exists():
            return None
        
        # Check if conversion needed
        target_format = self.config["audio_formats"]["primary"]
        if original_file.suffix[1:].lower() != target_format:
            converted_file = self._convert_audio_format(original_file, target_format)
            if converted_file:
                self.audio_cache[filename] = str(converted_file)
                return converted_file
        
        self.audio_cache[filename] = str(original_file)
        return original_file
    
    def _convert_audio_format(self, source_file: Path, target_format: str) -> Optional[Path]:
        """Convert audio file to mobile-compatible format"""
        
        target_file = self.cache_dir / f"{source_file.stem}.{target_format}"
        
        # Skip if already exists
        if target_file.exists():
            return target_file
        
        try:
            # Try ffmpeg conversion
            result = subprocess.run([
                "ffmpeg", "-i", str(source_file), 
                "-acodec", self._get_codec_for_format(target_format),
                "-ar", "44100",  # Standard sample rate
                "-ac", "2",      # Stereo
                "-y",            # Overwrite
                str(target_file)
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0 and target_file.exists():
                return target_file
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback: copy original if same format
        if source_file.suffix[1:].lower() == target_format:
            try:
                import shutil
                shutil.copy2(source_file, target_file)
                return target_file
            except Exception:
                pass
        
        return None
    
    def _get_codec_for_format(self, format: str) -> str:
        """Get audio codec for format"""
        codecs = {
            "wav": "pcm_s16le",
            "mp3": "mp3",
            "m4a": "aac",
            "ogg": "vorbis"
        }
        return codecs.get(format, "pcm_s16le")
    
    def _play_android_audio(self, audio_file: Path, event: MobileAudioEvent):
        """Play audio on Android"""
        try:
            # Try using Android MediaPlayer
            if hasattr(self, 'android_audio'):
                self.android_audio.play_sound(str(audio_file), event.volume)
            else:
                # Fallback to system player
                subprocess.run([
                    "am", "start", "-a", "android.intent.action.VIEW",
                    "-d", f"file://{audio_file}",
                    "-t", "audio/*"
                ], check=False)
        except Exception as e:
            print(f"Android audio playback error: {e}")
    
    def _play_ios_audio(self, audio_file: Path, event: MobileAudioEvent):
        """Play audio on iOS"""
        try:
            # Try using iOS AVAudioPlayer
            if hasattr(self, 'ios_audio'):
                self.ios_audio.play_sound(str(audio_file), event.volume)
            else:
                # Fallback to system player
                subprocess.run([
                    "open", "-a", "QuickTime Player", str(audio_file)
                ], check=False)
        except Exception as e:
            print(f"iOS audio playback error: {e}")
    
    def _play_windows_mobile_audio(self, audio_file: Path, event: MobileAudioEvent):
        """Play audio on Windows Mobile"""
        try:
            # Use Windows Media Player
            subprocess.run([
                "wmplayer", str(audio_file)
            ], check=False)
        except Exception as e:
            print(f"Windows Mobile audio playback error: {e}")
    
    def _play_desktop_emulation_audio(self, audio_file: Path, event: MobileAudioEvent):
        """Play audio in desktop emulation mode"""
        try:
            system = platform.system()
            
            if system == "Windows":
                try:
                    import winsound
                    winsound.PlaySound(str(audio_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
                except ImportError:
                    os.startfile(str(audio_file))
            elif system == "Darwin":
                subprocess.run(["afplay", str(audio_file), "-v", str(event.volume)], check=False)
            else:  # Linux
                subprocess.run(["aplay", str(audio_file)], check=False)
                
        except Exception as e:
            print(f"Desktop emulation audio error: {e}")
    
    def _is_low_battery(self) -> bool:
        """Check if device has low battery"""
        try:
            if self.platform == MobilePlatform.ANDROID:
                # Android battery check
                result = subprocess.run([
                    "dumpsys", "battery"
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "level:" in line:
                            level = int(line.split(":")[1].strip())
                            return level < 20
            
            elif self.platform == MobilePlatform.IOS:
                # iOS battery check (requires jailbreak or special permissions)
                pass
            
            # Default: assume battery is fine
            return False
            
        except Exception:
            return False
    
    def _trigger_vibration(self, priority: int):
        """Trigger device vibration"""
        try:
            if self.platform == MobilePlatform.ANDROID:
                # Android vibration
                duration = min(1000, priority * 200)  # Max 1 second
                subprocess.run([
                    "input", "keyevent", "KEYCODE_VIBRATE"
                ], check=False)
            
            elif self.platform == MobilePlatform.IOS:
                # iOS haptic feedback
                if hasattr(self, 'ios_audio'):
                    self.ios_audio.trigger_haptic(priority)
            
            elif self.platform == MobilePlatform.DESKTOP_EMULATION:
                # Simulate vibration with sound
                print(f"🔸 Vibration simulation (priority: {priority})")
                
        except Exception as e:
            print(f"Vibration error: {e}")
    
    def _show_notification(self, event: MobileAudioEvent):
        """Show mobile notification"""
        try:
            title = "Claude Code Audio"
            message = f"Audio event: {event.metadata.get('operation', 'Unknown')}"
            
            if self.platform == MobilePlatform.ANDROID:
                # Android notification
                subprocess.run([
                    "am", "broadcast", 
                    "-a", "android.intent.action.NOTIFICATION",
                    "--es", "title", title,
                    "--es", "message", message
                ], check=False)
            
            elif self.platform == MobilePlatform.IOS:
                # iOS notification
                subprocess.run([
                    "osascript", "-e", 
                    f'display notification "{message}" with title "{title}"'
                ], check=False)
            
            elif self.platform == MobilePlatform.DESKTOP_EMULATION:
                # Desktop notification
                print(f"📱 Mobile Notification: {title} - {message}")
                
        except Exception as e:
            print(f"Notification error: {e}")
    
    # Public API
    
    def queue_audio_event(self, audio_file: str, volume: float = 0.7, 
                         priority: int = 1, vibration: bool = False,
                         notification: bool = False, metadata: Optional[Dict] = None) -> str:
        """Queue a mobile audio event"""
        
        event = MobileAudioEvent(
            event_id=f"mobile_{int(time.time() * 1000)}",
            timestamp=time.time(),
            audio_file=audio_file,
            volume=volume,
            priority=priority,
            vibration=vibration,
            notification=notification,
            metadata=metadata or {}
        )
        
        with self.queue_lock:
            self.event_queue.append(event)
            
            # Limit queue size
            if len(self.event_queue) > 50:
                self.event_queue.pop(0)
        
        return event.event_id
    
    def play_immediate(self, audio_file: str, volume: float = 0.7):
        """Play audio immediately (bypassing queue)"""
        event = MobileAudioEvent(
            event_id=f"immediate_{int(time.time() * 1000)}",
            timestamp=time.time(),
            audio_file=audio_file,
            volume=volume,
            priority=3
        )
        
        self._handle_mobile_audio_event(event)
    
    def sync_audio_files(self) -> Dict[str, Any]:
        """Sync audio files from main system"""
        sync_results = {
            "synced_files": 0,
            "failed_files": 0,
            "cache_size_mb": 0
        }
        
        try:
            if not self.audio_dir.exists():
                return sync_results
            
            # Get available audio files
            audio_files = list(self.audio_dir.glob("*.wav")) + list(self.audio_dir.glob("*.mp3"))
            
            for audio_file in audio_files:
                try:
                    cached_file = self._get_audio_file(audio_file.name)
                    if cached_file:
                        sync_results["synced_files"] += 1
                    else:
                        sync_results["failed_files"] += 1
                except Exception:
                    sync_results["failed_files"] += 1
            
            # Calculate cache size
            cache_size = sum(f.stat().st_size for f in self.cache_dir.iterdir() if f.is_file())
            sync_results["cache_size_mb"] = cache_size / 1024 / 1024
            
        except Exception as e:
            sync_results["error"] = str(e)
        
        return sync_results
    
    def get_mobile_status(self) -> Dict[str, Any]:
        """Get mobile audio system status"""
        return {
            "platform": self.platform.value,
            "enabled": self.config.get("enabled", True),
            "queue_size": len(self.event_queue),
            "cache_files": len(self.audio_cache),
            "cache_size_mb": sum(Path(f).stat().st_size for f in self.audio_cache.values() if Path(f).exists()) / 1024 / 1024,
            "battery_optimization": self.config.get("battery_optimization", True),
            "vibration_enabled": self.config.get("vibration_enabled", True),
            "notification_enabled": self.config.get("notification_enabled", True)
        }
    
    def shutdown(self):
        """Shutdown mobile audio bridge"""
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=2)

# Global instance
_mobile_bridge = None

def get_mobile_bridge() -> MobileAudioBridge:
    """Get the global mobile bridge instance"""
    global _mobile_bridge
    if _mobile_bridge is None:
        _mobile_bridge = MobileAudioBridge()
    return _mobile_bridge

# Convenience functions for mobile integration
def play_mobile_audio(filename: str, **kwargs):
    """Play audio on mobile device"""
    bridge = get_mobile_bridge()
    return bridge.queue_audio_event(filename, **kwargs)

def mobile_notification_with_sound(filename: str, message: str):
    """Show mobile notification with sound"""
    bridge = get_mobile_bridge()
    return bridge.queue_audio_event(
        filename, 
        notification=True, 
        metadata={"message": message}
    )

def mobile_vibrate_with_sound(filename: str, priority: int = 2):
    """Play sound with vibration"""
    bridge = get_mobile_bridge()
    return bridge.queue_audio_event(
        filename, 
        vibration=True, 
        priority=priority
    )

if __name__ == "__main__":
    # Example usage and testing
    bridge = MobileAudioBridge()
    
    print("Testing mobile audio bridge...")
    
    # Test immediate playback
    bridge.play_immediate("startup.wav")
    
    # Test queued events
    bridge.queue_audio_event(
        "agent_activated.wav", 
        volume=0.8, 
        vibration=True, 
        notification=True,
        metadata={"agent": "mobile_test", "operation": "test"}
    )
    
    # Sync audio files
    sync_results = bridge.sync_audio_files()
    print(f"Sync results: {sync_results}")
    
    # Get status
    status = bridge.get_mobile_status()
    print(f"Mobile status: {status}")
    
    time.sleep(2)
    
    bridge.shutdown()
    print("Mobile audio bridge test completed")