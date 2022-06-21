import numpy as np
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
  output = 'scoreboard players set #exp_temp_0 nn_eval 786432\n' # FPSF * 3
  output += 'scoreboard players operation #exp_temp_0 nn_eval -= {inval} nn_eval\n'.format(inval=inval)
  
  # diviend
  output += 'scoreboard players set {outval} nn_eval 786432\n'.format(outval=outval) # again, FPSF * 3
  # 2x term of diviend
  output += 'scoreboard players operation #exp_temp_1 nn_eval = {inval} nn_eval\n'.format(inval=inval)
  output += 'scoreboard players operation #exp_temp_1 nn_eval *= #TWO nn_eval\n'
  output += 'scoreboard players operation {outval} nn_eval += #exp_temp_1 nn_eval\n'.format(outval=outval)
  # 0.5x^2 term of diviend
  output += 'scoreboard players operation #exp_temp_2 nn_eval = {inval} nn_eval\n'.format(inval=inval)
  output += 'scoreboard players operation #exp_temp_2 nn_eval /= #TWO nn_eval\n' # /2 interlaced to prevent overflow in intermediate step
  output += 'scoreboard players operation #exp_temp_2 nn_eval /= #sqrtFPSF nn_eval\n'
  output += 'scoreboard players operation #exp_temp_2 nn_eval *= {inval} nn_eval\n'.format(inval=inval)
  output += 'scoreboard players operation #exp_temp_2 nn_eval /= #sqrtFPSF nn_eval\n'
  output += 'scoreboard players operation {outval} nn_eval += #exp_temp_2 nn_eval\n'.format(outval=outval)
  
  # putting it all together
  output += 'scoreboard players operation #exp_temp_0 nn_eval /= #sqrtFPSF nn_eval\n'
  output += 'scoreboard players operation {outval} nn_eval *= #sqrtFPSF nn_eval\n'.format(outval=outval)
  output += 'scoreboard players operation {outval} nn_eval /= #exp_temp_0 nn_eval\n'.format(outval=outval)
  
  """
  computed with [1/1] pade approximants; less accurate but faster
  y = (2+x)/(2-x)
  
  output = 'scoreboard players set {outval} nn_eval 524288\n'.format(outval=outval) # FPSF * 2
  output += 'scoreboard players operation {outval} nn_eval += {inval} nn_eval\n'.format(inval=inval,outval=outval)
  output += 'scoreboard players set #exp_temp_0 nn_eval 524288\n'
  output += 'scoreboard players operation #exp_temp_0 nn_eval -= {inval} nn_eval\n'.format(inval=inval)
  output += 'scoreboard players operation {outval} nn_eval *= #sqrtFPSF nn_eval\n'.format(outval=outval)
  output += 'scoreboard players operation #exp_temp_0 nn_eval /= #sqrtFPSF nn_eval\n'
  output += 'scoreboard players operation {outval} nn_eval /= #exp_temp_0 nn_eval\n'.format(outval=outval)
  """
  
  return output
