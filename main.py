#!/usr/bin/env python3

"""
Q3.28 format is used in the output
"""

import warnings
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
  
  print(node)
  
  flatten = False
  
  for t in node.input:
    if t.endswith('ReadVariableOp:0'): # weights
      current_weights.append(weights[weight_count-weight_order[layer-unweighted_layers]])
      weight_count += 1
    elif t.startswith('const_fold_opt'):
      flatten = True
    elif layer != 0: # load output of last layer to this layer
      output += ophelper.opElementwise(last_shape, 'scoreboard players operation #l{cn}_%d nn_eval = #l{pn}_%d nn_eval\n'.format(cn=layer,pn=layer-1), 'scoreboard players operation #l{cn}_%d_%d nn_eval = #l{pn}_%d_%d nn_eval\n'.format(cn=layer,pn=layer-1), 'scoreboard players operation #l{cn}_%d_%d_%d nn_eval = #l{pn}_%d_%d_%d nn_eval\n'.format(cn=layer,pn=layer-1)) # copy
    
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
    case 'Conv': # assumed 2D for now, who uses Conv1D for images anyways
      attributes = list(node.attribute)
      dilations = attributes[0].ints
      strides = attributes[1].ints
      kernel_shape = attributes[2].ints
      filter_count = len(current_weights[1]) # length of list of biases
      
      ea_factor = floor(kernel_shape / 2) # edge avoidance for padding='valid' in tf
      
      for fc in range(filter_count):
        # the +1 in the ranges below are to include the end
        for ci in range(ea_factor[0],last_shape[0] - ea_factor[0] + 1):
          for cj in range(ea_factor[1],last_shape[1] - ea_factor[1] + 1):
            for fi in range(-ea_factor[0], ea_factor[0] + 1):
              for fj in range(-ea_factor[1], ea_factor[1] + 1):
                output += 'scoreboard players operation #conv_temp_0 nn_eval = #l{cn}_%d_%d nn_eval'.format(cn=layers)
                # TODO: multiply weights and sum
      
    case 'Relu':
      match len(last_shape):
        case 2:
          output += ophelper.opElementwise(last_shape, out2d = 'execute if score test #l{cn}_%d_%d matches ..0 run scoreboard players set #l{cn}_%d_%d nn_eval 0\n'.format(cn=layer))
        case 3:
          output += ophelper.opElementwise(last_shape, out3d = 'execute if score test #l{cn}_%d_%d_%d matches ..0 run scoreboard players set #l{cn}_%d_%d_%d nn_eval 0\n'.format(cn=layer))
    case 'MaxPool':
      
      pass
    case 'Transpose':
      pass
    case 'MatMul':
      pass
    case 'Add':
      pass
    case 'Softmax':
      pass
    case _:
      pass
      warnings.warn(str(node.op_type) + ' is currently not supported, skipping layer')
  
  output += '\n'

with open('nnOutput.mcfunction', 'w') as f:
  f.write(output)
