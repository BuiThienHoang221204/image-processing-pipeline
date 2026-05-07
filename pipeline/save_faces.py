import os
import cv2

from pipeline.pipeline import Pipeline


class SaveFaces(Pipeline):
    """Pipeline task to save detected faces."""

    def __init__(self, path, image_ext="jpg"):
        self.path = path
        self.image_ext = image_ext

        super(SaveFaces, self).__init__()

    def map(self, data):
        image_id = data["image_id"]
        image = data["image"]
        faces = data["faces"]
        data["face_files"] = []

        # Loop over all detected faces
        for i, face in enumerate(faces):
            box, confidence = face
            (x1, y1, x2, y2) = box.astype("int")
            # Crop the face from the image
            face = image[y1:y2, x1:x2]

            # Prepare output directory for faces
            output = os.path.join(*(image_id.split(os.path.sep)))
            output = os.path.join(self.path, output)
            os.makedirs(output, exist_ok=True)

            # Validate crop bounds
            h, w = image.shape[:2]
            if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1 or x2 > w or y2 > h:
                print(f"[WARN] {image_id}: invalid face box {(x1,y1,x2,y2)}, skipping")
                continue

            # Save faces (skip empty crops)
            face_file = os.path.join(output, f"{i:05d}.{self.image_ext}")
            if face is None or face.size == 0:
                print(f"[WARN] {image_id}: empty face crop for box {(x1,y1,x2,y2)}, skipping")
                continue

            data["face_files"].append(face_file)
            success = cv2.imwrite(face_file, face)
            if not success:
                print(f"[ERROR] Failed to write face to {face_file}")

        return data
