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
        output += out % (i, j, j + i * shape[0])
    case 3:
      for i,j,k in np.ndindex(shape):
        output += out % (i, j, k, k + j * shape[0] + i * shape[0] * shape[1])
  return output
