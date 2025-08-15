"""
WebRTC/noVNC Streaming Integration
=================================

Streaming capabilities for Claude Code Browser integration that enable
real-time screen sharing and remote browser access while maintaining
separation from the original AGPL-3.0 codebase by @zainhoda.
"""

import asyncio
import json
import logging
import os
import subprocess
import websockets
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
import base64
import io
from PIL import Image, ImageDraw
import cv2
import numpy as np

@dataclass
class StreamingConfig:
    """Configuration for streaming services."""
    webrtc_enabled: bool = True
    novnc_enabled: bool = True
    screen_capture_fps: int = 30
    max_resolution: tuple = (1920, 1080)
    compression_quality: int = 80
    webrtc_port: int = 8082
    novnc_port: int = 8083

class WebRTCStreamer:
    """WebRTC streaming implementation for real-time browser sharing."""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.peer_connections: Set[Any] = set()
        self.is_streaming = False
        
    async def start_webrtc_server(self):
        """Start WebRTC signaling server."""
        try:
            print(f"🎥 Starting WebRTC server on port {self.config.webrtc_port}")
            
            # Start WebRTC signaling server
            start_server = websockets.serve(
                self.handle_webrtc_connection,
                "localhost",
                self.config.webrtc_port
            )
            
            await start_server
            print("✅ WebRTC server started")
            
        except Exception as e:
            print(f"❌ Failed to start WebRTC server: {e}")
    
    async def handle_webrtc_connection(self, websocket, path):
        """Handle WebRTC signaling connections."""
        print("🔌 WebRTC client connected")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_webrtc_message(websocket, data)
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebRTC client disconnected")
        except Exception as e:
            print(f"❌ WebRTC connection error: {e}")
    
    async def process_webrtc_message(self, websocket, data: Dict[str, Any]):
        """Process WebRTC signaling messages."""
        message_type = data.get("type")
        
        if message_type == "offer":
            await self.handle_offer(websocket, data)
        elif message_type == "answer":
            await self.handle_answer(websocket, data)
        elif message_type == "ice-candidate":
            await self.handle_ice_candidate(websocket, data)
        elif message_type == "start-stream":
            await self.start_browser_stream(websocket)
    
    async def handle_offer(self, websocket, data: Dict[str, Any]):
        """Handle WebRTC offer."""
        # Create answer and send back
        answer = {
            "type": "answer",
            "sdp": self.create_answer_sdp(data.get("sdp"))
        }
        await websocket.send(json.dumps(answer))
    
    async def handle_answer(self, websocket, data: Dict[str, Any]):
        """Handle WebRTC answer."""
        # Process answer SDP
        pass
    
    async def handle_ice_candidate(self, websocket, data: Dict[str, Any]):
        """Handle ICE candidate."""
        # Process ICE candidate
        pass
    
    async def start_browser_stream(self, websocket):
        """Start streaming browser content via WebRTC."""
        self.is_streaming = True
        
        try:
            while self.is_streaming:
                # Capture browser screen
                frame = await self.capture_browser_screen()
                
                if frame is not None:
                    # Encode frame for WebRTC
                    encoded_frame = await self.encode_frame_for_webrtc(frame)
                    
                    # Send frame via WebRTC data channel
                    await websocket.send(json.dumps({
                        "type": "video-frame",
                        "data": encoded_frame,
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                
                # Maintain target FPS
                await asyncio.sleep(1 / self.config.screen_capture_fps)
                
        except Exception as e:
            print(f"❌ Browser streaming error: {e}")
        finally:
            self.is_streaming = False
    
    def create_answer_sdp(self, offer_sdp: str) -> str:
        """Create SDP answer for WebRTC offer."""
        # Simplified SDP answer - in production, use proper WebRTC library
        return f"""v=0
o=- 123456789 123456789 IN IP4 127.0.0.1
s=-
t=0 0
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 127.0.0.1
a=rtcp:9 IN IP4 127.0.0.1
a=ice-ufrag:abcd
a=ice-pwd:1234567890123456789012
a=fingerprint:sha-256 AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99
a=setup:active
a=mid:video
a=sendrecv
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:96 H264/90000
a=fmtp:96 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f"""

class NoVNCStreamer:
    """noVNC streaming implementation for web-based VNC access."""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.vnc_process: Optional[subprocess.Popen] = None
        self.novnc_process: Optional[subprocess.Popen] = None
    
    async def start_novnc_server(self):
        """Start noVNC server for web-based remote access."""
        try:
            print(f"🖥️ Starting noVNC server on port {self.config.novnc_port}")
            
            # Start VNC server (x11vnc for Linux/Mac, TightVNC for Windows)
            await self.start_vnc_server()
            
            # Start noVNC web server
            await self.start_novnc_web_server()
            
            print("✅ noVNC server started")
            
        except Exception as e:
            print(f"❌ Failed to start noVNC server: {e}")
    
    async def start_vnc_server(self):
        """Start the underlying VNC server."""
        if os.name == 'nt':  # Windows
            # Use TightVNC or similar
            self.vnc_process = subprocess.Popen([
                "tvnserver", "-run"
            ])
        else:  # Linux/Mac
            # Use x11vnc
            self.vnc_process = subprocess.Popen([
                "x11vnc", "-display", ":0", "-nopw", "-listen", "localhost", "-xkb"
            ])
    
    async def start_novnc_web_server(self):
        """Start noVNC web interface."""
        # Start noVNC websockify proxy
        self.novnc_process = subprocess.Popen([
            "websockify", "--web", "/usr/share/novnc/",
            str(self.config.novnc_port), "localhost:5900"
        ])
    
    def stop_novnc_server(self):
        """Stop noVNC and VNC servers."""
        if self.novnc_process:
            self.novnc_process.terminate()
        if self.vnc_process:
            self.vnc_process.terminate()
        print("🛑 noVNC server stopped")

class BrowserCapture:
    """Browser screen capture utilities."""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
    
    async def capture_browser_screen(self) -> Optional[np.ndarray]:
        """Capture the current browser screen."""
        try:
            # Use different capture methods based on platform
            if os.name == 'nt':  # Windows
                return await self.capture_windows_screen()
            else:  # Linux/Mac
                return await self.capture_x11_screen()
                
        except Exception as e:
            print(f"❌ Screen capture error: {e}")
            return None
    
    async def capture_windows_screen(self) -> Optional[np.ndarray]:
        """Capture screen on Windows using win32 API."""
        try:
            import win32gui
            import win32ui
            import win32con
            
            # Get browser window
            hwnd = win32gui.FindWindow(None, "Claude Code Browser")
            
            if hwnd:
                # Get window dimensions
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Capture window
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                if result:
                    # Convert to numpy array
                    bmpinfo = saveBitMap.GetInfo()
                    bmpstr = saveBitMap.GetBitmapBits(True)
                    img = np.frombuffer(bmpstr, dtype='uint8')
                    img.shape = (height, width, 4)
                    img = img[:, :, :3]  # Remove alpha channel
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    return img
                
        except ImportError:
            print("❌ Windows screen capture requires pywin32")
        except Exception as e:
            print(f"❌ Windows screen capture error: {e}")
        
        return None
    
    async def capture_x11_screen(self) -> Optional[np.ndarray]:
        """Capture screen on Linux/Mac using X11."""
        try:
            import pyscreenshot as ImageGrab
            
            # Capture full screen (could be optimized to capture specific window)
            img = ImageGrab.grab()
            img_np = np.array(img)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            return img_np
            
        except ImportError:
            print("❌ X11 screen capture requires pyscreenshot")
        except Exception as e:
            print(f"❌ X11 screen capture error: {e}")
        
        return None
    
    async def encode_frame_for_webrtc(self, frame: np.ndarray) -> str:
        """Encode frame for WebRTC transmission."""
        try:
            # Resize frame if needed
            height, width = frame.shape[:2]
            max_width, max_height = self.config.max_resolution
            
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.compression_quality]
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            
            if result:
                # Convert to base64 for WebRTC transmission
                img_base64 = base64.b64encode(encoded_img).decode('utf-8')
                return img_base64
            
        except Exception as e:
            print(f"❌ Frame encoding error: {e}")
        
        return ""

class StreamingManager:
    """Main streaming management class."""
    
    def __init__(self, config: StreamingConfig = None):
        self.config = config or StreamingConfig()
        self.webrtc_streamer = WebRTCStreamer(self.config) if self.config.webrtc_enabled else None
        self.novnc_streamer = NoVNCStreamer(self.config) if self.config.novnc_enabled else None
        self.browser_capture = BrowserCapture(self.config)
    
    async def start_streaming_services(self):
        """Start all enabled streaming services."""
        print("🎬 Starting streaming services...")
        
        tasks = []
        
        if self.webrtc_streamer:
            tasks.append(self.webrtc_streamer.start_webrtc_server())
        
        if self.novnc_streamer:
            tasks.append(self.novnc_streamer.start_novnc_server())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        print("✅ Streaming services started")
        print(f"   WebRTC: {'enabled' if self.webrtc_streamer else 'disabled'}")
        print(f"   noVNC: {'enabled' if self.novnc_streamer else 'disabled'}")
    
    def stop_streaming_services(self):
        """Stop all streaming services."""
        print("🛑 Stopping streaming services...")
        
        if self.novnc_streamer:
            self.novnc_streamer.stop_novnc_server()
        
        print("✅ Streaming services stopped")
    
    async def capture_browser_screen(self) -> Optional[np.ndarray]:
        """Capture browser screen."""
        return await self.browser_capture.capture_browser_screen()

# Global streaming manager instance
streaming_manager = StreamingManager()

if __name__ == "__main__":
    # Example usage
    async def main():
        await streaming_manager.start_streaming_services()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            streaming_manager.stop_streaming_services()
    
    asyncio.run(main())