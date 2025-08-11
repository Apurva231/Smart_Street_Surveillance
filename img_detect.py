import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import torch
import cv2
import os

# Paths
oimages_path = Path("C:/Users/Acer.DESKTOP-76HB3FE/Desktop/pr_project/static/images")
dimages_path = Path("C:/Users/Acer.DESKTOP-76HB3FE/Desktop/pr_project/static/detected_images")

# Load YOLOv5 model once
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)

class ImageHandler(FileSystemEventHandler):
    def process_image(self, path):
        if path.lower().endswith(('.jpg', '.jpeg', '.png')):
            time.sleep(1)  # wait for file write to complete
            print(f"Image detected: {path}")
            self.run_detection(path)

    def on_created(self, event):
        if not event.is_directory:
            self.process_image(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_image(event.src_path)

    def run_detection(self, image_path):
        image_path = Path(image_path)
        results = model(str(image_path))
        results.render()

        dimages_path.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(results.ims):
            output_path = dimages_path / image_path.name
            cv2.imwrite(str(output_path), img[:, :, ::-1])  # RGB to BGR
            print(f"Saved detection result to: {output_path}")

if __name__ == "__main__":
    print(f"Watching folder: {oimages_path}")
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(oimages_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()