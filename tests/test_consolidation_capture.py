import importlib.util
from pathlib import Path
import numpy as np
import torch
import pytest

pytest.importorskip("transformers")
from transformers import Qwen3Config, Qwen3Model

def test_chunking_and_causality(tmp_path):
    spec = importlib.util.spec_from_file_location("capture",Path(__file__).parents[1]/"tools/consolidation/capture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    torch.manual_seed(20260930)
    model = Qwen3Model(Qwen3Config(vocab_size=32,hidden_size=32,intermediate_size=48,num_hidden_layers=2,
        num_attention_heads=2,num_key_value_heads=1,head_dim=16,attn_implementation="sdpa")).eval()
    ids = np.arange(17)%32
    positions = np.array([0,3,7,8,15,16])
    full = module.capture(model,ids,positions,tmp_path/"full",32)
    chunked = module.capture(model,ids,positions,tmp_path/"chunked",4)
    extended = module.capture(model,np.r_[ids,[4,5,6]],positions,tmp_path/"extended",4)
    for k in ["K","V"]:
        np.testing.assert_allclose(full[k],chunked[k],rtol=1e-5,atol=1e-6)
        np.testing.assert_allclose(full[k],extended[k],rtol=1e-5,atol=1e-6)
