#!/usr/bin/env python3

"""
Q3.28 format is used in the output
"""
FPSF = 2**28 # fixed point scale factor
sqrtFPSF = 2**14 # useful in multiplication and division

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

output = "scoreboard players set #sqFPSF nn_eval %d\n" % sqrtFPSF

default_layer = lambda l:ophelper.opElementwise(last_shape, 'scoreboard players operation #l{cn}_%d nn_eval = #l{pn}_%d nn_eval\n'.format(cn=l,pn=l-1), 'scoreboard players operation #l{cn}_%d_%d nn_eval = #l{pn}_%d_%d nn_eval\n'.format(cn=l,pn=l-1), 'scoreboard players operation #l{cn}_%d_%d_%d nn_eval = #l{pn}_%d_%d_%d nn_eval\n'.format(cn=l,pn=l-1)) # copy

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
        output += ophelper.opFlatten(last_shape, 'scoreboard players operation #l{cn}_%d nn_eval = #l{pn}_%d_%d nn_eval\n'.format(cn=layer,pn=layer-1))
        last_shape = (np.prod(last_shape),)
    case 'Conv': # assumed 2D for now, who uses Conv1D for images anyways
      attributes = list(node.attribute)
      dilations = list(attributes[0].ints)
      strides = list(attributes[1].ints)
      kernel_shape = list(attributes[2].ints)
      filter_count = len(current_weights[1]) # length of list of biases
      
      ea_factor = (np.floor(kernel_shape)/2).astype(int) # edge avoidance for padding='valid' in tf
      
      for fc in range(filter_count):
        for ci in range(ea_factor[0],last_shape[0] - ea_factor[0]):
          for cj in range(ea_factor[1],last_shape[1] - ea_factor[1]):
            output += 'scoreboard players set #conv_temp_1 nn_eval 0\n'
            for fi in range(-ea_factor[0], ea_factor[0] + 1):
              for fj in range(-ea_factor[1], ea_factor[1] + 1):
                output += 'scoreboard players set #weight_temp_0 nn_eval {weight}\n'.format(weight=int(current_weights[0][fc][0][fi][fj] * sqrtFPSF)) # * FPSF / sqrtFPSF
                output += 'scoreboard players operation #conv_temp_0 nn_eval = #l{pn}_{x}_{y} nn_eval\n'.format(pn=layer-1,x=ci+fi,y=cj+fj)
                output += 'scoreboard players operation #conv_temp_0 nn_eval /= #sqrtSPSF nn_eval\n'
                output += 'scoreboard players operation #conv_temp_0 nn_eval *= #weight_temp_0 nn_eval\n'
                output += 'scoreboard players operation #conv_temp_1 nn_eval += #conv_temp_0 nn_eval\n'
            output += 'scoreboard players set #bias_temp_0 nn_eval {bias}\n'.format(bias=int(current_weights[1][fc] * FPSF))
            output += 'scoreboard players operation #conv_temp_1 nn_eval += #bias_temp_0 nn_eval\n'
            output += 'scoreboard players operation #l{cn}_{x}_{y}_{f} nn_eval = #conv_temp_1 nn_eval\n'.format(cn=layer,x=ci,y=cj,f=fc)
      
      last_shape = (last_shape[0] - ea_factor[0],last_shape[1] - ea_factor[1], filter_count)
      
    case 'Relu':
      # copy and zero out if negative; conditional copy + zero out uncopied values also take 2 commands but takes 2 checks instead of one
      output += default_layer(layer)
      match len(last_shape):
        case 1:
          output += ophelper.opElementwise(last_shape, out1d = 'execute if score test #l{cn}_%d matches ..0 run scoreboard players operation #l{cn}_%d nn_eval 0\n'.format(cn=layer))
        case 2:
          output += ophelper.opElementwise(last_shape, out2d = 'execute if score test #l{cn}_%d_%d matches ..0 run scoreboard players operation #l{cn}_%d_%d nn_eval 0\n'.format(cn=layer))
        case 3:
          output += ophelper.opElementwise(last_shape, out3d = 'execute if score test #l{cn}_%d_%d_%d matches ..0 run scoreboard players operation #l{cn}_%d_%d_%d nn_eval 0\n'.format(cn=layer,pn=layer-1))
    case 'MaxPool':
      attributes = list(node.attribute)
      strides = list(attributes[1].ints)
      kernel_shape = list(attributes[2].ints)
      match len(last_shape):
        case 2:
          pass
        case 3:
          for k in range(last_shape[2]):
            for ic, i in enumerate(range(0,last_shape[0],strides[0])):
              for jc, j in enumerate(range(0,last_shape[1],strides[1])):
                
          last_shape = (last_shape[0]//strides[0],last_shape[1]//strides[1],last_shape[2])
    case 'Transpose':
      output += default_layer(layer)
    case 'MatMul': # 1D input
      print(last_shape)
      output_length = len(current_weights[0][0])
      for i in range(output_length):
        output == 'scoreboard players set #l{cn}_{y} nn_eval 0\n'.format(cn=layer,y=i)
        for j in range(last_shape[0]):
          output += 'scoreboard players set #weight_temp nn_eval {weight}\n'.format(weight=int(current_weights[0][j][i] * sqrtFPSF)) # * FPSF / sqrtFPSF and notice i and j are swapped
          output += 'scoreboard players operation #matmul_temp_0 nn_eval = #l{pn}_{x} nn_eval\n'.format(pn=layer-1,x=j)
          output += 'scoreboard players operation #matmul_temp_0 nn_eval /= #sqrtFPST nn_eval\n'
          output += 'scoreboard players operation #matmul_temp_0 nn_eval *= #weight_temp nn_eval\n'
          output += 'scoreboard players operation #l{cn}_{y} nn_eval += #matmul_temp_0 nn_eval\n'.format(cn=layer,y=i)
          
    case 'Add':
      output += default_layer(layer)
    case 'Softmax':
      output += default_layer(layer)
    case _:
      output += default_layer(layer)
      warnings.warn(str(node.op_type) + ' is currently not supported, skipping layer')
  output += '\n'

with open('nnOutput.mcfunction', 'w') as f:
  f.write(output)
