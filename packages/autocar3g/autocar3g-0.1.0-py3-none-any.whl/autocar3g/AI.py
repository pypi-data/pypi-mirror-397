import cv2, time, os, sys
import numpy as np
# import tensorrt as trt
import atexit
import __main__

import warnings
warnings.filterwarnings(action='ignore')

IDENTIFIER="_models"

mnist_train_x=None
mnist_train_y=None
mnist_test_x=None
mnist_test_y=None

#---------------------------------------------  Ondevice AI ---------------------------------------------

def import_tensorflow():
    global tf
    import tensorflow as tf
    import tensorflow.keras as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    import tensorflow.keras.models as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    import tensorflow.keras.losses as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    import tensorflow.keras.layers as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    import tensorflow.keras.optimizers as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    import tensorflow.keras.utils as __module
    
    for k in [m for m in dir(__module) if not "__" in m]:
        globals()[k]=__module.__dict__[k]

    gpus=tf.config.experimental.list_physical_devices('GPU')

    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

def bgr8_to_jpeg(value):
    return bytes(cv2.imencode('.jpg', value)[1])

from ultralytics import YOLO

class Object_Follow():
    def __init__(self, camera):

        self.camera = camera
        self.boxes_image = None
    
    def load_model(self, path):    
        self.model = YOLO(path)
    
    def detect(self, image=None, index=None, threshold=0.5, callback=None):
        if image is None:
            image=self.camera.read()
            if image is None:
                return

        if type(index)==str:
            try:
                index=list(self.model.names.values()).index(index)
            except ValueError:
                print("index is not available.")
                return

        result = self.model.predict(source=image, imgsz=640, verbose=False)[0]
        self.boxes_image = result.plot()

        width = image.shape[1]
        height = image.shape[0]

        detections = []
        for b in result.boxes:
            detected_index = int(b.cls[0].cpu().numpy().astype(int))
            xywh = b.xywh[0].cpu().numpy()
            if index is not None:
                if detected_index != index:
                    continue
            detections.append({
                'index' : detected_index,
                'label' : self.model.names[detected_index],
                'x' : xywh[0],
                'y' : xywh[1],
                'size_rate' : (xywh[2] * xywh[3]) / (width*height)
            })

        return detections

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import *
from tensorflow.keras.models import *
from tensorflow.keras.losses import *
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import *
from tensorflow.keras.utils import *
from autocar3g.camera import Camera

class Track_Follow_TF():
    MODEL_PATH = 'Track_Follow.h5'
    dataset_path = 'track_dataset'
    BATCH_SIZE = 8
    model=None
    device=None
    datasets=None
    optimizer=None
    prob=None
    probWidget=None
    STAT_DEFINED=0
    STAT_READY=1
    _stat=STAT_DEFINED

    def __init__(self,camera:Camera):
        self.camera = camera
        import_tensorflow()
        self.default_path=os.path.abspath(__file__+"/../model/Track_Follow/")

    def _load_layers(self):
        input1 = keras.layers.Input(shape=(150, 400, 3,))
        conv1 = keras.layers.Conv2D(filters=16, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(input1)
        norm1 = keras.layers.BatchNormalization()(conv1)
        pool1 = keras.layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(norm1)
        conv2 = keras.layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(pool1)
        norm2 = keras.layers.BatchNormalization()(conv2)
        conv3 = keras.layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish")(norm2)
        norm3 = keras.layers.BatchNormalization()(conv3)
        add1 = keras.layers.Add()([norm2, norm3])
        conv4 = keras.layers.Conv2D(filters=64, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(add1)
        norm4 = keras.layers.BatchNormalization()(conv4)
        conv5 = keras.layers.Conv2D(filters=64, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish")(norm4)
        norm5 = keras.layers.BatchNormalization()(conv5)
        add2 = keras.layers.Add()([norm4, norm5])
        conv6 = keras.layers.Conv2D(filters=128, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(add2)
        norm6 = keras.layers.BatchNormalization()(conv6)
        conv7 = keras.layers.Conv2D(filters=128, kernel_size=(3, 3), strides=(1, 1), padding="same", activation="swish")(norm6)
        norm7 = keras.layers.BatchNormalization()(conv7)
        add3 = keras.layers.Add()([norm6, norm7])
        conv8 = keras.layers.Conv2D(filters=256, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(add3)
        norm7 = keras.layers.BatchNormalization()(conv8)
        conv9 = keras.layers.Conv2D(filters=512, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="swish")(norm7)
        norm8 = keras.layers.BatchNormalization()(conv9)
        flat1 = keras.layers.Flatten()(norm8)
        dense1 = keras.layers.Dense(128, activation="swish")(flat1)
        norm9 = keras.layers.BatchNormalization()(dense1)
        dense2 = keras.layers.Dense(64, activation="swish")(norm9)
        norm10 = keras.layers.BatchNormalization()(dense2)
        dense3 = keras.layers.Dense(64, activation="swish")(norm10)
        norm11 = keras.layers.BatchNormalization()(dense3)
        dense4 = keras.layers.Dense(2, activation="sigmoid")(norm11)
        self.model = keras.models.Model(inputs=input1, outputs=dense4)

    def load_model(self,path=MODEL_PATH):
        if not os.path.exists(path):
            print(path," doesn't exist.")
            return

        if self.model is None:
            self._load_layers()
            decay=schedules.ExponentialDecay(1.0e-04, decay_steps=800, decay_rate=0.96, staircase=True)
            adam=Adam(learning_rate=decay, beta_1=0.9, beta_2=0.999, epsilon=1e-07, amsgrad=False)
            self.model.compile(optimizer=adam, loss='MAE')

        self.model.load_weights(path)

    def run(self, value=None, callback=None):
        if self.model is None :
            print("Please load datasets as load_datasets() method or load a trained model as load_model() method.")
            return

        img = self.camera.read()[120:270,:] if value is None else value
        x, y = self.model(np.array([img]).astype(np.float32)).numpy()[0]
        height, width, _ = img.shape
        cX = int(width * (x))
        cY = int(height * (y))

        self.value = cv2.circle(img, (cX, cY), 6, (255, 255, 255), 2)

        result={"x":x,"y":y}

        if callback is not None:
            callback(result)

        return result
