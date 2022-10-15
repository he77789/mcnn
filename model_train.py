#!/usr/bin/env python3

import numpy as np
import tensorflow as tf
from tensorflow import keras
import tf2onnx
import onnx
import onnxoptimizer

num_classes = 10
input_shape = (28, 28, 1)

# load data
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

# preprocess pixels
x_train = x_train.astype("float32") / 255
x_test = x_test.astype("float32") / 255
x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = keras.Sequential(
  [
    keras.Input(shape=input_shape),
    keras.layers.Conv2D(4, kernel_size=(3,3), activation='relu'),
    keras.layers.MaxPooling2D(pool_size=(4,4)),
    keras.layers.Flatten(),
    keras.layers.Dense(num_classes, activation='softmax')
  ]
)

model.summary()

# train
batch_size = 128
epochs = 15
model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs)

score = model.evaluate(x_test, y_test)
print('Test loss: ' + str(score[0]))
print('Test accuracy: ' + str(score[1]))

# write model to disk
input_signature = [tf.TensorSpec([None,28,28,1], tf.float32, name='image')]
onnx_model,_ = tf2onnx.convert.from_keras(model, input_signature, opset=13)
onnx_model = onnxoptimizer.optimize(onnx_model)
onnx.save(onnx_model, 'models/mnist_output_model.onnx')

print('Done')
