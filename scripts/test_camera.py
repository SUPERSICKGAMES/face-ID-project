import cv2
import time

def list_available_cameras():
    """Test which camera indices are available"""
    available_cameras = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

def test_camera(camera_index):
    print(f"Testing camera index: {camera_index}")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to read frame from camera {camera_index}")
        return False
        
    # Display the camera feed for 3 seconds
    start_time = time.time()
    while (time.time() - start_time) < 3:
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f'Testing Camera {camera_index}', frame)
            cv2.waitKey(1)
    
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    cameras = list_available_cameras()
    print(f"Available camera indices: {cameras}")
    
    # Test first 3 camera indices
    for i in range(3):
        print(f"\nTesting camera {i}")
        if test_camera(i):
            print(f"Camera {i} works!")
        else:
            print(f"Camera {i} failed or not available")