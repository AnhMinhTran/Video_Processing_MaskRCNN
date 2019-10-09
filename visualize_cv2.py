import cv2
import numpy as np
import os
import sys

ROOT_DIR = os.path.abspath("../")
sys.path.append(ROOT_DIR)
from mrcnn import utils
import mrcnn.model as modellib

sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))
import coco

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(coco.CocoConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


config = InferenceConfig()
config.display()

model = modellib.MaskRCNN(
    mode="inference", model_dir=MODEL_DIR, config=config
)
model.load_weights(COCO_MODEL_PATH, by_name=True)
class_names = [
    'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
    'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
    'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
    'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
    'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard',
    'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
    'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
    'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
    'teddy bear', 'hair drier', 'toothbrush'
]

def random_colors(N):
    np.random.seed(1)
    colors = [tuple(255 * np.random.rand(3)) for _ in range(N)]
    return colors

def apply_mask(image, mask, color, alpha =0.5):
    """apply mask to images"""
    """ loop over colors instead of range"""
    for n,c in enumerate(color):
        image[:,:,n] = np.where(
            mask ==1,
            image[:,:,n] * (1-alpha) + alpha *c,
            image[:,:,n]
            )
    return image


def display_instances(image, boxes, masks, ids, names, scores):
    n_instances = boxes.shape[0]
    if not n_instances:
        print('No instances to display')
    else:
        assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]

    colors = random_colors(n_instances)
    height,width = image.shape[:2]

    for i,color in enumerate(colors):
        if not np.any(boxes[i]):
            continue

        y1,x1,y2,x2 = boxes[i]
        mask = masks[:,:,i]
        image = apply_mask(image, mask, color)
        image = cv2.rectangle(image, (x1,y1), (x2,y2), color, 2)
        label = names[ids[i]]
        score = scores[i] if scores is not None else None
        caption = '{}{:.2f}'.format(label, score) if score else label
        image = cv2.putText(
            image, caption, (x1,y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2
        )
    return image

if __name__ == '__main__':
    """
        test everything
    """


    capture = cv2.VideoCapture(0)
    # Check if the webcam is opened correctly
    if not capture.isOpened():
        raise IOError("Cannot open webcam")

    return_value, image = capture.read()
    print("We take a picture of you, check the folder")
    cv2.imwrite("image.png", image)

    capture.release()  # Error is here
    cv2.destroyAllWindows()
    # these 2 lines can be removed if you dont have a 1080p camera.
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ret, frame = capture.read()
        results = model.detect([frame], verbose=0)
        r = results[0]
        frame = display_instances(
            frame, r['rois'], r['masks'], r['class_ids'], class_names, r['scores']
        )
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()