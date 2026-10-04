# Capture matched K/V before positional rotation using ordinary cached causal prefill.
from pathlib import Path
import numpy as np
import torch

@torch.inference_mode()
def capture(model, tokens, positions, directory, chunk_tokens):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    cfg = model.config
    layers = model.layers
    heads = cfg.num_key_value_heads
    dim = getattr(cfg,"head_dim",cfg.hidden_size//cfg.num_attention_heads)
    shape = (len(layers),len(positions),heads,dim)
    arrays = {k:np.lib.format.open_memmap(directory/f"{k}.npy",mode="w+",dtype=np.float32,shape=shape) for k in ["K","V"]}
    span = [0,0,0]
    handles = []
    def hook(kind, layer):
        def save(module, inputs, output):
            start, left, right = span
            if left == right:
                return
            local = torch.as_tensor(positions[left:right]-start, device=output.device)
            x = output.reshape(1,output.shape[1],heads,dim)[0].index_select(0,local)
            arrays[kind][layer,left:right] = x.float().cpu().numpy()
        return save
    for l, layer in enumerate(layers):
        attn = layer.self_attn
        handles.append(getattr(attn,"k_norm",attn.k_proj).register_forward_hook(hook("K",l)))
        handles.append(attn.v_proj.register_forward_hook(hook("V",l)))
    past = None
    try:
        for start in range(0,len(tokens),chunk_tokens):
            stop = min(len(tokens),start+chunk_tokens)
            span[:] = [start,int(np.searchsorted(positions,start)),int(np.searchsorted(positions,stop))]
            ids = torch.as_tensor(tokens[start:stop],device=model.device).unsqueeze(0)
            output = model(input_ids=ids,past_key_values=past,use_cache=True)
            past = output.past_key_values
        for a in arrays.values():
            a.flush()
    finally:
        for h in handles:
            h.remove()
        del past
    return arrays
