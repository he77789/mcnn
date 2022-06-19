#!/usr/bin/env python3
import numpy as np
import onnxruntime as rt

sess = rt.InferenceSession("mnist_output_model.onnx")
input_name = sess.get_inputs()[0].name
pred_onx = sess.run(None, {input_name: np.zeros((1,28,28,1), np.float32)})[0]
print(pred_onx)
