#!/usr/bin/env python3

"""
Uses hanmangokiwi's Hmmm module for math
each float is represented as 3 scoreboard values, one for sign, one for exponent, one for mantissa
so 1D vectors would actually be 2D, 2D vectors would actually be 3D and so on
"""

import numpy as np
import onnx
from onnx import numpy_helper
import ophelper

zero_float = ophelper.decomposefp(0.0)
most_neg_float = ophelper.decomposefp(-3.4028234663852885981170418348451692544e+38) # most negative value representable by ieee754 binary32

model = onnx.load('models/mnist_output_model.onnx')
graph = model.graph

weights = []
for tensor in graph.initializer:
  weights.append(numpy_helper.to_array(tensor))

input_shape = tuple(weights[-2][2:])
weights = weights[:-2]
weight_order = [2,4,3] # note: they will be multiplied by -1

# create temporary directory to hold the generated files
from pathlib import Path
Path("./build").mkdir(exist_ok = True)

keys = ['image']
unweighted_layers = 0
last_shape = input_shape

outputlist = []

for layer, node in enumerate(graph.node):
  output = ''
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

  match node.op_type:
    case 'Reshape':
      if flatten:
        output += ophelper.opFlatten(last_shape, 'scoreboard players operation #l{cn}_%d-%d nn_eval = #l{pn}_%d_%d_%d-%d nn_eval\n'.format(cn=layer,pn=layer-1))
        last_shape = (np.prod(last_shape),)
    
    case 'Conv': # assumed 2D for now, who uses Conv1D for images anyways
      attributes = list(node.attribute)
      dilations = list(attributes[0].ints)
      strides = list(attributes[1].ints)
      kernel_shape = list(attributes[2].ints)
      filter_count = len(current_weights[1]) # length of list of biases
      
      ea_factor = (np.floor(kernel_shape)/2).astype(int) # edge avoidance for padding='valid' in tf
      
      for fc in range(filter_count):
        for ic,ci in enumerate(range(ea_factor[0],last_shape[0] - ea_factor[0])):
          for jc,cj in enumerate(range(ea_factor[1],last_shape[1] - ea_factor[1])):
            decomposed_bias = ophelper.decomposefp(current_weights[1][fc])
            output += ophelper.setconst("#l{cn}_{f}_{x}_{y}-".format(cn=layer,x=ic,y=jc,f=fc), decomposed_bias) 
            for fi in range(-ea_factor[0], ea_factor[0] + 1):
              for fj in range(-ea_factor[1], ea_factor[1] + 1):
                decomposed_weight = ophelper.decomposefp(current_weights[0][fc][0][fi][fj])
                output += ophelper.setconst("P", decomposed_weight, "io", 3)
                output += ophelper.singlecopy("#l{pn}_{x}_{y}-".format(pn=layer-1,x=ci+fi,y=cj+fj), "P", objd = "io")
                output += "function float:32/multiply/main\n"
                output += ophelper.singlecopy("R", "P", "io", "io")
                output += ophelper.singlecopy("#l{cn}_{f}_{x}_{y}-".format(cn=layer,x=ic,y=jc,f=fc), "P", objd = "io", dbbias = 3)
                output += "function float:32/add/main\n"
                output += ophelper.singlecopy("R", "#l{cn}_{f}_{x}_{y}-".format(cn=layer,x=ic,y=jc,f=fc), objs = "io")
      
      last_shape = (filter_count, last_shape[0] - 2*ea_factor[0],last_shape[1] - 2*ea_factor[1])
      
    case 'Relu':
      # copy and zero out if negative; conditional copy + zero out uncopied values also take 2 commands but takes 2 checks instead of one
      output += ophelper.default_layer(last_shape, layer)
      output += ophelper.opElementwise(last_shape,
        out1d = 'execute if score #l{cn}_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d-{b} nn_eval -127\n'.format(cn=layer,b=1),
        out2d = 'execute if score #l{cn}_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d-{b} nn_eval -127\n'.format(cn=layer,b=1),
        out3d = 'execute if score #l{cn}_%d_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d_%d-{b} nn_eval -127\n'.format(cn=layer,b=1)
        )
      output += ophelper.opElementwise(last_shape,
        out1d = 'execute if score #l{cn}_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d-{b} nn_eval 0\n'.format(cn=layer,b=2),
        out2d = 'execute if score #l{cn}_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d-{b} nn_eval 0\n'.format(cn=layer,b=2),
        out3d = 'execute if score #l{cn}_%d_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d_%d-{b} nn_eval 0\n'.format(cn=layer,b=2)
        )
      output += ophelper.opElementwise(last_shape,
        out1d = 'execute if score #l{cn}_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d-{b} nn_eval 0\n'.format(cn=layer,b=0),
        out2d = 'execute if score #l{cn}_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d-{b} nn_eval 0\n'.format(cn=layer,b=0),
        out3d = 'execute if score #l{cn}_%d_%d_%d-0 nn_eval matches 1 run scoreboard players set #l{cn}_%d_%d_%d-{b} nn_eval 0\n'.format(cn=layer,b=0)
        )
    
    case 'MaxPool':
      attributes = list(node.attribute)
      strides = list(attributes[0].ints)
      kernel_shape = list(attributes[1].ints)
      rk_shape = [kernel_shape[0]//2,kernel_shape[1]//2]
      match len(last_shape):
        case 2:
          raise NotImplementedError("2D Maxpool not implemented")
        case 3:
          for k in range(last_shape[0]):
            for ic, i in enumerate(range(rk_shape[0],last_shape[1]-rk_shape[0],strides[0])):
              for jc, j in enumerate(range(rk_shape[1],last_shape[2]-rk_shape[1],strides[1])):
                output += ophelper.setconst("#l{cn}_{z}_{x}_{y}-".format(cn=layer,x=ic,y=jc,z=k), most_neg_float)
                for a in range(-rk_shape[0],rk_shape[1]+1):
                  for b in range(-rk_shape[1],rk_shape[1]+1):
                    output += ophelper.singlecopy("#l{cn}_{z}_{x}_{y}-".format(cn=layer,x=ic,y=jc,z=k), "P", objd = "io", dbbias = 3)
                    output += ophelper.singlecopy("#l{pn}_{z}_{a}_{b}-".format(pn=layer-1,z=k,a=i+a,b=j+b), "P", objd = "io")
                    output += "function float:32/compare/greater/main\n"
                    output += ophelper.cond_singlecopy("#l{pn}_{z}_{a}_{b}-".format(pn=layer-1,z=k,a=i+a,b=j+b), "#l{cn}_{z}_{x}_{y}-".format(cn=layer,x=ic,y=jc,z=k), cond = "if score R0 io matches 1")
                    
          last_shape = (last_shape[0],last_shape[1]//strides[0],last_shape[2]//strides[1])
    
    case 'Transpose': # convert from N,C,H,W to N,H,W,C
      output += ophelper.opTranspose(last_shape,'scoreboard players operation #l{cn}_%d_%d_%d-%d nn_eval = #l{pn}_%d_%d_%d-%d nn_eval\n'.format(cn=layer,pn=layer-1))
      last_shape = (last_shape[1], last_shape[2], last_shape[0])
    
    case 'MatMul': # 1D input
      output_length = len(current_weights[0][0])
      for i in range(output_length):
        output += ophelper.setconst("#l{cn}_{y}-".format(cn=layer,y=i), zero_float)
        for j in range(last_shape[0]):
          decomposed_weight = ophelper.decomposefp(current_weights[0][j][i]) # notice i and j are swapped
          output += ophelper.setconst("P", decomposed_weight, "io", 3)
          output += ophelper.singlecopy("#l{pn}_{x}-".format(pn=layer-1,x=j), "P", objd = "io")
          output += "function float:32/multiply/main\n"
          output += ophelper.singlecopy("R", "P", "io", "io")
          output += ophelper.singlecopy("#l{cn}_{y}-".format(cn=layer,y=i), "P", objd = "io", dbbias = 3)
          output += "function float:32/add/main\n"
          output += ophelper.singlecopy("R", "#l{cn}_{y}-".format(cn=layer,y=i), objs = "io")
      last_shape = (output_length,)
          
    case 'Add':
      match len(last_shape):
        case 1:
          for i in range(last_shape[0]):
            decomposed_bias = ophelper.decomposefp(current_weights[0][i])
            output += ophelper.setconst("P", decomposed_bias, "io", 3)
            output += ophelper.singlecopy("#l{pn}_{x}-".format(pn=layer-1,x=i), "P", objd = "io")
            output += "function float:32/add/main\n"
            output += ophelper.singlecopy("R", "#l{cn}_{x}-".format(cn=layer,x=i), objs = "io")
        case _:
          raise NotImplementedError("Multi-dimensional add not implemented yet")
    
    case 'Softmax':
      match len(last_shape):
        case 1:
          output += ophelper.setconst("#softmax_temp-",zero_float)
          
          for i in range(last_shape[0]):
            output += ophelper.opExp('#l{pn}_{x}-'.format(pn=layer-1,x=i), '#l{cn}_{x}-'.format(cn=layer,x=i))
            output += ophelper.singlecopy("#l{cn}_{x}-".format(cn=layer,x=i), "P", objd = "io", dbbias = 3)
            output += ophelper.singlecopy("#softmax_temp-", "P", objd = "io")
            output += "function float:32/add/main\n"
            output += ophelper.singlecopy("R", "#softmax_temp-", objs = "io")
          
          output += ophelper.singlecopy("#softmax_temp-", "P", objd = "io", dbbias = 3)
          for i in range(last_shape[0]):
            output += ophelper.singlecopy("#l{cn}_{x}-".format(cn=layer,x=i), "P", objd = "io")
            output += "function float:32/divide/main\n"
            output += ophelper.singlecopy("R", "#l{cn}_{x}-".format(cn=layer,x=i), objs = "io")
          
        case 2:
          raise NotImplementedError('2D softmax is currently not supported, skipping layer')
    
    case _:
      raise NotImplementedError(str(node.op_type) + ' is currently not supported, skipping layer')
  outputlist.append(output)

layercount = len(outputlist)
for l,o in enumerate(outputlist):
  if (l != layercount - 1): # not the last layer
    ofinal = o +'\nschedule function nn_0001:nnoutput_%03d 1t\n' % (layer + 1) # spread layers over multiple ticks to not lock the server up
  else: # last layer
    ofinal = o + '\nfunction #nn_0001:finish_callback\n'
  with open('build/nnoutput_%03d.mcfunction' % l, 'w') as f:
    f.write(ofinal)

# generate init file
output = 'scoreboard objectives add nn_eval dummy "NN internals"\ngamerule maxCommandChainLength 2147483647\n\n'
output += "function main:setup\n"
output += "function float:setup\n"
output += "function extended_float:setup\n"

with open('build/nninit.mcfunction', 'w') as f:
  f.write(output)

output = ''

for i,j in np.ndindex(input_shape):
  # set to a uniform grey of 0.1 for testing
  output += 'scoreboard players set #l0_{x}_{y}-0 nn_eval 0\n'.format(x=i,y=j)
  output += 'scoreboard players set #l0_{x}_{y}-1 nn_eval -4\n'.format(x=i,y=j)
  output += 'scoreboard players set #l0_{x}_{y}-2 nn_eval 5033165\n'.format(x=i,y=j)

with open('build/nn_test_img.mcfunction', 'w') as f:
  f.write(output)
