#!/usr/bin/env python3
import numpy as np
import onnx
import onnxruntime as ort
from collections import OrderedDict
import ophelper

# add all intermediate outputs to onnx net
ort_session = ort.InferenceSession("mnist_output_model.onnx")
org_outputs = [x.name for x in ort_session.get_outputs()]

model = onnx.load("mnist_output_model.onnx")
for node in model.graph.node:
    for output in node.output:
        if output not in org_outputs:
            model.graph.output.extend([onnx.ValueInfoProto(name=output)])

# excute onnx
ort_session = ort.InferenceSession(model.SerializeToString())
outputs = [x.name for x in ort_session.get_outputs()]
ort_outs = ort_session.run(outputs, {'image': np.full((1,28,28,1), 0.1, np.float32)} )
ort_outs = OrderedDict(zip(outputs, ort_outs))
outs = []
for key,element in ort_outs.items():
  outs.append(element[0])
  print(element[0])

"""
outs = outs[1:] + [outs[0]]
while True:
  l = int(input("l:"))
  c1 = int(input("c1:"))
  c2 = int(input("c2:"))
  c3 = int(input("c3:"))
  if (c2 == -1):
    p=(outs[l][c1])
  elif (c3 == -1):
    p=(outs[l][c1][c2])
  else:
    p=(outs[l][c1][c2][c3])
  print(np.vectorize(ophelper.decomposefp)(p))
"""
