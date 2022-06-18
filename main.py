#!/usr/bin/env python3

"""
Q3.28 format is used in the output
"""

import numpy as np
import onnx
from onnx import numpy_helper
import ophelper

model = onnx.load('models/mnist_output_model.onnx')
graph = model.graph

weights = []
for tensor in graph.initializer:
  weights.append(numpy_helper.to_array(tensor))

input_shape = tuple(weights[-2][2:])
print(input_shape)
weights = weights[:-2]
weight_order = [2,0,1]

output = ""



keys = ['image']
unweighted_layers = 0
last_shape = input_shape
for layer, node in enumerate(graph.node):
  weight_count = 0
  current_weights = []
  
  flatten = False
  
  for t in node.input:
    if t.endswith('ReadVariableOp:0'): # weights
      current_weights.append(weights[weight_count-weight_order[layer-unweighted_layers]])
      weight_count += 1
    elif t.startswith('const_fold_opt'):
      flatten = True
    elif layer != 0: # load output of last layer to this layer
      output += ophelper.opCopy(last_shape, 'scoreboard players operation #l{cn}_%d nn_eval = #l{pn}_%d nn_eval\n'.format(cn=layer,pn=layer-1), 'scoreboard players operation #l{cn}_%d_%d nn_eval = #l{pn}_%d_%d nn_eval\n'.format(cn=layer,pn=layer-1), 'scoreboard players operation #l{cn}_%d_%d_%d nn_eval = #l{pn}_%d_%d_%d nn_eval\n'.format(cn=layer,pn=layer-1))
    
  if weight_count == 0:
    unweighted_layers += 1
  
  """
  print(layer)
  print(unweighted_layers)
  print(current_weights)
  """
  
  match node.op_type:
    case 'Reshape':
      if flatten:
        output += ophelper.opFlatten(last_shape, 'scoreboard players operation #l{cn}_%d_%d nn_eval = #l{pn}_%d nn_eval\n'.format(cn=layer,pn=layer-1))
        last_shape = [np.prod(last_shape)]
    case 'Conv':
      pass
      # print(node.attribute)
    case _:
      pass
      # raise NotImplementedError(str(node.op_type) + ' is currently not supported')
  
  output += '\n'

#print(output)
