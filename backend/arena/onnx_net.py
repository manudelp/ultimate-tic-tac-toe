"""CPU wrapper around the NMCTS2 network published at uttt.ai.

The file is the browser export: policy logits and a state value. Search does
not read the auxiliary action-value head, so that tensor is zeros.
"""
import numpy as np


class OnnxPolicyValue:
    def __init__(self, path):
        import onnxruntime as ort
        import torch

        self.session = ort.InferenceSession(
            str(path), providers=["CPUExecutionProvider"]
        )
        self._device = torch.device("cpu")
        self._input_name = self.session.get_inputs()[0].name

    @property
    def device(self):
        return self._device

    def eval(self):
        return self

    def __call__(self, inputs):
        import torch

        array = inputs.detach().cpu().numpy().astype(np.float32, copy=False)
        logits, value = self.session.run(None, {self._input_name: array})
        policy = torch.from_numpy(np.ascontiguousarray(logits))
        state = torch.from_numpy(np.ascontiguousarray(value)).reshape(-1)
        return policy, torch.zeros_like(policy), state
