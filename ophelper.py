import numpy as np

def numConvert(x):
  pol = 1 if x >= 0 else -1
  x = float(abs(x))
  dec = 0
  while not x.is_integer():
    if dec >= 32: # truncate if it's over 32 decimal places
      break
    dec += 1
    x *= 10
  num = str([int(x) for x in list(str(int(x)))]).replace(' ','') # looks weird, but converts it to a list of digits, e.g. 1023 turns into "[1,0,2,3]"
  return '{dec:%d,num:%s,pol:%d,base:10}' % (dec,num,pol)
  
  
def opElementwise(shape, out1d=None, out2d=None, out3d=None):
  output = ''
  match len(shape):
    case 1:
      for i in range(shape[0]):
        output += out1d % (i, i)
    case 2:
      for i,j in np.ndindex(shape):
        output += out2d % (i, j, i, j)
    case 3:
      for i,j,k in np.ndindex(shape):
        output += out3d % (i, j, k, i, j ,k)
  return output

def opFlatten(shape, out):
  output = ''
  match len(shape):
    case 1:
      for i in range(shape[0]):
        output += out % (i, i) # basically copy
    case 2:
      for i,j in np.ndindex(shape):
        output += out % (j + i * shape[0], i, j)
    case 3:
      for i,j,k in np.ndindex(shape):
        output += out % (k + j * shape[0] + i * shape[0] * shape[1], i, j, k)
  return output

def opTranspose(shape, out):
  output = ''
  for i,j,k in np.ndindex(shape):
    output += out % (j, k, i, i, j, k) # the order is (dest, source). I made this mistake and spent 2 hours on it, don't be like me
  return output

def opExp(inval,outval):
  """
  computed with [2/1] pade approximants
  y = (3+2x+0.5x^2))/(3-x)
  """
  # divisor
  output = 'data modify storage arr_math:in var1 set value {dec:0,num:[3],pol:1,base:10}\n'
  output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval {inval}\n'.format(inval=inval)
  output += 'function arr_math:divide\n'
  output += 'data modify storage nn_0001:nn_eval exp_temp_0 set from storage arr_math:main out\n'
  
  # diviend
  #output += 'data modify storage arr_math:in var1 set value {dec:0,num:[3],pol:1,base:10}\n' # set above in the divisor calculation, var1 should be unchanged
  # 2x term of diviend
  # reusing loaded 3 above and adding twice instead of multiplying and adding
  # target output is used as a temporary storage
  output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval {inval}\n'.format(inval=inval)
  output += 'function arr_math:add\n'
  output += 'data modify storage arr_math:in var1 set from storage arr_math:main out\n'
  output += 'function arr_math:add\n'
  output += 'data modify storage nn_0001:nn_eval {outval} set from storage arr_math:main out\n'.format(outval=outval)
  
  # 0.5x^2 term of diviend
  # again, var2 is reused for x
  output += 'data modify storage arr_math:in var1 set value {{dec:1,num:[5],pol:1,base:10}}\n'.format(inval=inval)
  output += 'function arr_math:multiply\n'
  output += 'data modify storage arr_math:in var1 set from storage arr_math:main out\n'
  output += 'function arr_math:multiply\n'
  output += 'data modify storage arr_math:in var1 set from storage arr_math:main out\n'
  output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval {outval}\n'.format(outval=outval)
  output += 'function arr_math:add\n'
  
  # finally dividing
  output += 'data modify storage arr_math:in var1 set from storage arr_math:main out\n'
  output += 'data modify storage arr_math:in var2 set from storage nn_0001:nn_eval exp_temp_0\n'
  output += 'function arr_math:divide\n'
  output += 'data modify storage nn_0001:nn_eval {outval} set from storage arr_math:main out\n'.format(outval=outval)
  
  return output

if __name__ == '__main__':
  print('Running self tests:')
  print('numConvert(3.14159265358979):' + numConvert(3.14159265358979))
  print('numConvert(-123.456789):' + numConvert(-123.456789))
  print('numConvert(-0):' + numConvert(-0))
  print('numConvert(69**69):' + numConvert(69**69))
  print('\nopExp("a","b"):\n' + opExp("a","b"))
