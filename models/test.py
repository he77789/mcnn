#!/usr/bin/env python3
import numpy as np
import onnx
import onnxruntime as ort
from collections import OrderedDict

# add all intermediate outputs to onnx net
ort_session = ort.InferenceSession("mnist_output_model.onnx")
org_outputs = [x.name for x in ort_session.get_outputs()]

model = onnx.load("mnist_output_model.onnx")
for node in model.graph.node:
    for output in node.output:
        if output not in org_outputs:
            model.graph.output.extend([onnx.ValueInfoProto(name=output)])

# excute onnx
ort_session = ort.InferenceSession(model.SerializeToString())
outputs = [x.name for x in ort_session.get_outputs()]
ort_outs = ort_session.run(outputs, {'image': np.zeros((1,28,28,1), np.float32)} )
ort_outs = OrderedDict(zip(outputs, ort_outs))
print(ort_outs)
