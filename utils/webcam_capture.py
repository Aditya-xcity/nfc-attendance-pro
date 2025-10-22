"""
Webcam Capture Module
Captures photos from webcam when NFC cards are scanned.
Handles camera initialization, photo capture, and file management.
"""

import os
from datetime import datetime
from typing import Optional, Tuple
import threading
import time

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("[WARN] OpenCV not installed. Webcam feature disabled.")
    print("[WARN] Install with: pip install opencv-python")

class WebcamCapture:
    """Manages webcam photo capture for attendance."""
    
    def __init__(self, storage_dir: str = "static/photos", camera_index: int = 0):
        """
        Initialize webcam capture.
        
        Args:
            storage_dir: Directory to save photos
            camera_index: Camera device index (0 = default camera)
        """
        self.storage_dir = storage_dir
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
        self.current_frame = None
        self.last_photo_path = None
        
        # Create storage directory
        os.makedirs(storage_dir, exist_ok=True)
        
        # Try to initialize camera
        self._initialize_camera()
    
    def _initialize_camera(self) -> bool:
        """Initialize camera connection."""
        if not OPENCV_AVAILABLE:
            print("[WARN] OpenCV not available. Camera disabled.")
            return False
        
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print(f"[WARN] Camera {self.camera_index} not available")
                return False
            
            # Set camera properties for LOWER latency (reduce resolution)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)    # Reduced from 1280
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)   # Reduced from 720
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)        # Disable for speed
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)       # Reduce buffer lag
            
            # Discard old frames to reduce latency
            for _ in range(5):
                self.cap.read()
            
            # Test capture
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.is_initialized = True
                print("[INFO] Webcam initialized (low-latency mode)")
                return True
            else:
                print("[WARN] Could not read from camera")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to initialize camera: {e}")
            return False
    
    def start_capture_thread(self) -> bool:
        """Start background thread for continuous frame capture."""
        if not self.is_initialized:
            print("[WARN] Camera not initialized")
            return False
        
        def capture_loop():
            while self.is_initialized:
                try:
                    ret, frame = self.cap.read()
                    if ret:
                        self.current_frame = frame
                    time.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    print(f"[ERROR] Capture loop error: {e}")
                    break
        
        thread = threading.Thread(target=capture_loop, daemon=True)
        thread.start()
        return True
    
    def capture_photo(self, student_name: str = "Unknown") -> Optional[str]:
        """
        Capture a photo from the webcam (optimized for speed).
        
        Args:
            student_name: Name of student for filename
            
        Returns:
            Filename if successful, None otherwise
        """
        if not self.is_initialized or self.current_frame is None:
            print("[ERROR] Camera not ready")
            return None
        
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            safe_name = "".join(c if c.isalnum() or c in ' -_' else '' for c in student_name)
            safe_name = safe_name.replace(" ", "_")[:20]  # Limit name length
            
            filename = f"{timestamp}_{safe_name}.jpg"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Capture frame (use current frame buffer for speed)
            ret, frame = self.cap.read()
            
            if not ret:
                print("[ERROR] Failed to capture frame")
                return None
            
            # Add text with minimal processing
            time_str = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, time_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame, student_name, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
            
            # Save with lower quality for speed (60% quality = faster)
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            
            if success:
                self.last_photo_path = filepath
                file_size = os.path.getsize(filepath) / 1024  # KB
                print(f"[INFO] Photo captured: {filename} ({file_size:.1f} KB)")
                return filename
            else:
                print(f"[ERROR] Failed to save photo to {filepath}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Photo capture failed: {e}")
            return None
    
    def get_current_frame_base64(self) -> Optional[str]:
        """
        Get current frame as base64 for streaming to web.
        
        Returns:
            Base64 encoded image string or None
        """
        if self.current_frame is None:
            return None
        
        try:
            import base64
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            base64_str = base64.b64encode(buffer).decode('utf-8')
            return base64_str
        except Exception as e:
            print(f"[ERROR] Failed to encode frame: {e}")
            return None
    
    def get_photo_url(self, filename: str) -> str:
        """Get web URL for a saved photo."""
        return f"/static/photos/{filename}"
    
    def cleanup_old_photos(self, keep_count: int = 100) -> int:
        """
        Delete oldest photos to save space, keep recent ones.
        
        Args:
            keep_count: Number of recent photos to keep
            
        Returns:
            Number of photos deleted
        """
        try:
            photos = [f for f in os.listdir(self.storage_dir) if f.endswith('.jpg')]
            
            if len(photos) <= keep_count:
                return 0
            
            # Sort by modification time
            photos_with_time = [(f, os.path.getmtime(os.path.join(self.storage_dir, f))) 
                               for f in photos]
            photos_with_time.sort(key=lambda x: x[1])
            
            # Delete oldest
            to_delete = len(photos_with_time) - keep_count
            deleted = 0
            
            for filename, _ in photos_with_time[:to_delete]:
                try:
                    filepath = os.path.join(self.storage_dir, filename)
                    os.remove(filepath)
                    deleted += 1
                except Exception as e:
                    print(f"[WARN] Could not delete {filename}: {e}")
            
            print(f"[INFO] Cleaned up {deleted} old photos")
            return deleted
            
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
            return 0
    
    def get_storage_stats(self) -> dict:
        """Get statistics about stored photos."""
        try:
            photos = [f for f in os.listdir(self.storage_dir) if f.endswith('.jpg')]
            total_size = sum(os.path.getsize(os.path.join(self.storage_dir, f)) 
                           for f in photos)
            
            return {
                'photo_count': len(photos),
                'total_size_kb': total_size / 1024,
                'storage_dir': self.storage_dir
            }
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {'error': str(e)}
    
    def release(self):
        """Release camera resource."""
        if self.cap:
            self.cap.release()
            self.is_initialized = False
            print("[INFO] Camera released")
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.release()


# Global webcam instance
_webcam = None

def get_webcam(storage_dir: str = "static/photos", camera_index: int = 0) -> WebcamCapture:
    """Get or create global webcam instance."""
    global _webcam
    if _webcam is None:
        _webcam = WebcamCapture(storage_dir, camera_index)
    return _webcam


if __name__ == "__main__":
    # Test the webcam
    print("Testing webcam capture...")
    webcam = get_webcam()
    
    if webcam.is_initialized:
        print("✅ Webcam initialized")
        
        # Capture test photo
        filename = webcam.capture_photo("Test Student")
        if filename:
            print(f"✅ Photo saved: {filename}")
            print(f"   URL: {webcam.get_photo_url(filename)}")
            print(f"   Path: {webcam.last_photo_path}")
        
        # Show stats
        stats = webcam.get_storage_stats()
        print(f"\n📊 Storage Stats:")
        print(f"   Photos: {stats.get('photo_count', 0)}")
        print(f"   Size: {stats.get('total_size_kb', 0):.1f} KB")
    else:
        print("❌ Webcam not available")
    
    webcam.release()
