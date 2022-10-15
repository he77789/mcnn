#!/usr/bin/env python3

import warnings
import numpy as np
import onnx
from onnx import numpy_helper
import ophelper

model = onnx.load('models/mnist_output_model.onnx')
graph = model.graph

outputs = []

weights = []
for tensor in graph.initializer:
  weights.append(numpy_helper.to_array(tensor))

input_shape = tuple(weights[-2][2:])
weights = weights[:-2]
weight_order = [2,4,3] # note: they will be multiplied by -1

default_layer = lambda l:ophelper.opElementwise(last_shape, 'data modify storage nn_0001:nn_eval l{cn}_%d set from storage nn_0001:nn_eval l{pn}_%d\n'.format(cn=l,pn=l-1), 'data modify storage nn_0001:nn_eval l{cn}_%d_%d set from storage nn_0001:nn_eval l{pn}_%d_%d\n'.format(cn=l,pn=l-1), 'data modify storage nn_0001:nn_eval l{cn}_%d_%d_%d set from storage nn_0001:nn_eval l{pn}_%d_%d_%d\n'.format(cn=l,pn=l-1)) # copy

keys = ['image']
unweighted_layers = 0
last_shape = input_shape
for layer, node in enumerate(graph.node):
  output = "# generated with he77789's mcnn tool\n"
  print(last_shape)
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
        output += ophelper.opFlatten(last_shape, 'data modify storage nn_0001:nn_eval l{cn}_%d set from storage l{pn}_%d_%d_%d nn_0001:nn_eval\n'.format(cn=layer,pn=layer-1))
        last_shape = (np.prod(last_shape),)
    
    # very heavy layer: it will split itself into one function per filter
    case 'Conv':
      match len(last_shape):
        case 2:
          attributes = list(node.attribute)
          dilations = list(attributes[0].ints)
          strides = list(attributes[1].ints)
          kernel_shape = list(attributes[2].ints)
          filter_count = len(current_weights[1]) # length of list of biases
          
          ea_factor = (np.floor(kernel_shape)/2).astype(int) # edge avoidance for padding='valid' in tf
          
          for fc in range(filter_count):
            for ic,ci in enumerate(range(ea_factor[0],last_shape[0] - ea_factor[0])):
              for jc,cj in enumerate(range(ea_factor[1],last_shape[1] - ea_factor[1])):
                output += 'data modify storage nn_0001:nn_eval l{cn}_{f}_{x}_{y} set value {{dec:0,num:[0],pol:1,base:10}}\n'.format(cn=layer,x=ic,y=jc,f=fc)
                
                for fi in range(-ea_factor[0], ea_factor[0] + 1):
                  for fj in range(-ea_factor[1], ea_factor[1] + 1):
                    output += 'data modify storage arr_math:in var2 set value {weight}\n'.format(weight=ophelper.numConvert(current_weights[0][fc][0][fi][fj]))
                    output += 'data modify storage arr_math:in var1 set from storage nn_0001:nn_eval l{pn}_{x}_{y}\n'.format(pn=layer-1,x=ci+fi,y=cj+fj)
                    output += 'function arr_math:call/multiply\n'
                    output += 'data modify storage arr_math:in var1 set from storage arr_math:main out\n'
                    output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l{cn}_{f}_{x}_{y}\n'.format(cn=layer,x=ic,y=jc,f=fc)
                    output += 'function arr_math:call/add\n'
                    output += 'data modify storage nn_0001:nn_eval l{cn}_{f}_{x}_{y} set from storage arr_math:main out\n'.format(cn=layer,x=ic,y=jc,f=fc)
                    
                output += 'data modify storage arr_math:in var1 set value {bias}\n'.format(bias=ophelper.numConvert(current_weights[1][fc]))
                output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l{cn}_{f}_{x}_{y}\n'.format(cn=layer,x=ic,y=jc,f=fc)
                output += 'function arr_math:call/add\n'
                output += 'data modify storage nn_0001:nn_eval l{cn}_{f}_{x}_{y} set from storage arr_math:main out\n'.format(cn=layer,x=ic,y=jc,f=fc)
            outputs.append(output)
            output = "# generated with he77789's mcnn tool\n"

          last_shape = (filter_count, last_shape[0] - 2*ea_factor[0],last_shape[1] - 2*ea_factor[1])
        case 1:
          raise NotImplementedError('Conv1D not implemented, failing due to likely failure of output')
      
    case 'Relu':
      # copy and zero out if negative; conditional copy + zero out uncopied values also take 2 commands but takes 2 checks instead of one
      output += default_layer(layer)
      # curly brackets are doubled for str.format()
      match len(last_shape):
        case 1:
          output += ophelper.opElementwise(last_shape, out1d = 'execute if data storage nn_0001:nn_eval {{l{cn}_%d:{{pol:-1}}}} run data modify storage nn_0001:nn_eval l{cn}_%d set value {{dec:0,num:[0],pol:1,base:10}}\n'.format(cn=layer))
        case 2:
          output += ophelper.opElementwise(last_shape, out2d = 'execute if data storage nn_0001:nn_eval {{l{cn}_%d_%d:{{pol:-1}}}} run data modify storage nn_0001:nn_eval l{cn}_%d_%d set value {{dec:0,num:[0],pol:1,base:10}}\n'.format(cn=layer))
        case 3:
          output += ophelper.opElementwise(last_shape, out3d = 'execute if data storage nn_0001:nn_eval {{l{cn}_%d_%d_%d:{{pol:-1}}}} run data modify storage nn_0001:nn_eval l{cn}_%d_%d_%d set value {{dec:0,num:[0],pol:1,base:10}}\n'.format(cn=layer))
          
    case 'MaxPool':
      attributes = list(node.attribute)
      strides = list(attributes[0].ints)
      kernel_shape = list(attributes[1].ints)
      rk_shape = [kernel_shape[0]//2,kernel_shape[1]//2]
      match len(last_shape):
        case 2:
          warnings.warn('MaxPool for 2D inputs are not supported, skipping')
        case 3:
          for k in range(last_shape[2]):
            for ic, i in enumerate(range(rk_shape[0],last_shape[0]-rk_shape[0],strides[0])):
              for jc, j in enumerate(range(rk_shape[1],last_shape[1]-rk_shape[1],strides[1])):
                output += 'data modify storage nn_0001:nn_eval l{cn}_{z}_{x}_{y} set value {{dec:100,num:[1],pol:-1,base:10}}\n'.format(cn=layer,x=ic,y=jc,z=k) # -1e100 used as smallest value, we got worse problems if we have values smaller than that
                
                for a in range(-rk_shape[0],rk_shape[1]+1):
                  for b in range(-rk_shape[1],rk_shape[1]+1):
                    # subtraction is used here instead of built in comparison because the built in comparison is very janky
                    output += 'data modify storage arr_math:in var1 set from storage nn_0001:nn_eval l{cn}_{z}_{x}_{y}\n'.format(cn=layer,x=ic,y=jc,z=k,a=i+a,b=j+b)
                    output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l{pn}_{z}_{a}_{b}\n'.format(pn=layer-1,z=k,a=i+a,b=j+b)
                    output += 'function arr_math:call/subtract\n'
                    output += 'execute if data storage arr_math:main {{out:{{pol:-1}}}} run data modify storage nn_0001:nn_eval l{cn}_{z}_{x}_{y} set from storage nn_0001:nn_eval l{pn}_{z}_{a}_{b}\n'.format(cn=layer,pn=layer-1,x=ic,y=jc,z=k,a=i+a,b=j+b)
                    
          last_shape = (last_shape[0],last_shape[1]//strides[0],last_shape[2]//strides[1])
          
    case 'Transpose': # convert from N,C,H,W to N,H,W,C
      output += ophelper.opTranspose(last_shape,'data modify storage nn_0001:nn_eval l{cn}_%d_%d_%d set from storage nn_0001:nn_eval l{pn}_%d_%d_%d\n'.format(cn=layer,pn=layer-1))
      
    case 'MatMul': # 1D input
      output_length = len(current_weights[0][0])
      for i in range(output_length):
        output += 'data modify storage nn_0001:nn_eval l{cn}_{y} set value {{dec:0,num:[0],pol:1,base:10}}\n'.format(cn=layer,y=i)
        for j in range(last_shape[0]):
          output += 'data modify storage arr_math:in var1 set value {weight}\n'.format(weight=ophelper.numConvert(current_weights[0][j][i])) # notice i and j are swapped
          output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval #l{pn}_{x}\n'.format(pn=layer-1,x=j)
          output += 'function arr_math:call/multiply\n'
          output += 'data modify storage arr_math:in var1 set from storage nn_0001:nn_eval l{cn}_{y}\n'.format(cn=layer,y=i)
          output += 'data modify storage arr_math:in var2 set from storage arr_math:main out\n'
          output += 'function arr_math:call/add\n'
          output += 'data modify storage nn_0001:nn_eval l{cn}_{y} set from storage arr_math:main out\n'.format(cn=layer,y=i)
      last_shape = (output_length,)
          
    case 'Add':
      match len(last_shape):
        case 1:
          for i in range(last_shape[0]):
            output += 'data modify storage arr_math:in var1 set value %s\n' % (ophelper.numConvert(current_weights[0][i]))
            output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval l{pn}_{i}\n'.format(pn=layer-1,i=i)
            output += 'function arr_math:call/add\n'
            output += 'data modify storage nn_0001:nn_eval l{cn}_{i} set from storage arr_math:main out\n'.format(cn=layer,i=i)
        case 2:
          warnings.warn('2D add is not supported, skipping layer')
          
    case 'Softmax':
      match len(last_shape):
        case 1:
          output += 'data modify storage nn_0001:nn_eval softmax_temp_0 set value {dec:0,num:[0],pol:1,base:10}\n'
          
          for i in range(last_shape[0]):
            output += ophelper.opExp('l{pn}_{x}'.format(pn=layer-1,x=i), 'l{cn}_{x}'.format(cn=layer,x=i))
            output += 'data modify storage arr_math:in var1 set from storage nn_0001:nn_eval l{cn}_{x}\n'.format(cn=layer,x=i)
            output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval softmax_temp_0\n'
            output += 'function arr_math:call/add\n'
            output += 'data modify storage nn_0001:nn_eval softmax_temp_0 set from storage arr_math:main out\n'
          
          output += 'data modify storage arr_math:main var2 set from storage nn_0001:nn_eval softmax_temp_0\n'
          for i in range(last_shape[0]):
            output += 'data modify storage arr_math:main var1 set from storage nn_0001:nn_eval l{cn}_{x}\n'.format(cn=layer,x=i)
            output += 'function arr_math:call/divide\n'
            output += 'data modify storage nn_0001:nn_eval l{cn}_{x} set from storage arr_math:main out\n'.format(cn=layer,x=i)
         
        case 2:
          warnings.warn('2D softmax is currently not supported, skipping layer')
          output += default_layer(layer)
          
    case _:
      output += default_layer(layer)
      warnings.warn(str(node.op_type) + ' is currently not supported, skipping layer')
  outputs.append(output)

for i,layer_output in enumerate(outputs):
  with open('nnoutput_{i}.mcfunction'.format(i=i), 'w') as f:
    f.write(layer_output)

# generate init file
output = 'function arr_math:setup\n'
output += 'gamerule maxCommandChainLength 2147483647\n'
output += 'scoreboard players set mdp= arr_main.main 20\n'
for i,j in np.ndindex(input_shape):
  output += 'data modify storage nn_0001:nn_eval l0_{x}_{y} set value {{dec:0,num:[0],pol:-1,base:10}}\n'.format(x=i,y=j)

with open('nninit.mcfunction', 'w') as f:
  f.write(output)
