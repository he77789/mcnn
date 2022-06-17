#!/usr/bin/env python3

"""
Q3.28 format is used in the output
"""

import numpy as np
import onnx
from onnx import numpy_helper

model = onnx.load('models/mnist_output_model.onnx')
graph = model.graph

weights = []
for tensor in graph.initializer:
  weights.append(numpy_helper.to_array(tensor))

input_shape = weights[-2][2:3]
weights = weights[:-2]

output = ""

keys = ['image']
for layer, node in enumerate(graph.node):
  print(node)
  weight_count = 0
  current_weights = []
  for t in node.input:
    if t.endswith('ReadVariableOp:0'): # weights
      current_weights.append(weights[weight_count-2*(layer+1)])
  
  match node.op_type:
    case 'Reshape':
      pass
    case 'Conv':
      print(node.attribute)
    case _:
      raise NotImplementedError(str(node.op_type) + ' is currently not supported')
