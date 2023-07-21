import numpy as np
import struct

def singlecopy(source, dest, objs = "nn_eval", objd = "nn_eval", sbbias = 0, dbbias = 0):
  output = ''
  for b in range(3):
    output += "scoreboard players operation %s%d %s = %s%d %s\n" % (dest, b + dbbias, objd, source, b + sbbias, objs)
  return output

def cond_singlecopy(source, dest, cond, objs = "nn_eval", objd = "nn_eval", sbbias = 0, dbbias = 0):
  output = ''
  for b in range(3):
    output += "execute %s run scoreboard players operation %s%d %s = %s%d %s\n" % (cond, dest, b + dbbias, objd, source, b + sbbias, objs)
  return output

# copy
def default_layer(shape, l):
  output = ''
  match len(shape):
    case 1:
      for i in range(shape[0]):
        varc = "#l%d_%d-" % (l, i)
        varp = "#l%d_%d-" % (l-1, i)
        output += singlecopy(varp, varc)
    case 2:
      for i,j in np.ndindex(shape):
        varc = "#l%d_%d_%d-" % (l, i, j)
        varp = "#l%d_%d_%d-" % (l-1, i, j)
        output += singlecopy(varp, varc)
    case 3:
      for i,j,k in np.ndindex(shape):
        varc = "#l%d_%d_%d_%d-" % (l, i, j, k)
        varp = "#l%d_%d_%d_%d-" % (l-1, i, j, k)
        output += singlecopy(varp, varc)
  return output

def decomposefp(x):
  # packing the value into a struct and unpacking it as an int turns it into the bitwise representation
  s = struct.pack(">f", x)
  intbits = struct.unpack(">l", s)[0]
  sign = (intbits >> 31) & 0b1
  exponent = ((intbits >> 23) & 0b11111111) - 127 # the exponent is signed in hmmm
  mantissa = (intbits) & 0b11111111111111111111111 # bottom 23 bits
  return (sign, exponent, mantissa)

def setconst(name, decomposed, obj = "nn_eval", bbias = 0):
  output = ''
  for b in range(3):
    output += 'scoreboard players set %s%d %s %d\n' % (name, b + bbias, obj, decomposed[b])
  return output

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
  for b in range(3):
    match len(shape):
      case 1:
        for i in range(shape[0]):
          output += out % (i, b, i, b) # basically copy
      case 2:
        for s,(i,j) in enumerate(np.ndindex(shape)):
          output += out % (s, b, i, j, b)
      case 3:
        for s,(i,j,k) in enumerate(np.ndindex(shape)):
          output += out % (s, b, i, j, k, b)
  return output

def opTranspose(shape, out):
  output = ''
  for b in range(3):
    for i,j,k in np.ndindex(shape):
      output += out % (j, k, i, b, i, j, k, b) # the order is (dest, source). I made this mistake and spent 2 hours on it, don't be like me
  return output

def opExp(inval,outval):
  output = ''
  output += singlecopy(inval, "P", objd = "io")
  output += "function extended_float:32/exponential/main\n"
  output += singlecopy("R", outval, objs = "io")
  
  return output
