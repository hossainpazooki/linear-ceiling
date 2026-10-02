import os,gc,time,json,hashlib,re
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).parent
os.environ['HF_HOME']=str(ROOT/'hf')
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK']='1'
import numpy as np
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer,AutoConfig,DynamicCache
torch.set_num_threads(4)
torch.set_grad_enabled(False)
DEVICE=torch.device('cpu')

def sync():
    if DEVICE.type=='cuda':torch.cuda.synchronize(DEVICE)
    elif DEVICE.type=='mps':torch.mps.synchronize()

def clear():
    gc.collect()
    if DEVICE.type=='mps':torch.mps.empty_cache()

def load(name,device='cpu',dtype='float32',yarn=False):
    global DEVICE
    DEVICE=torch.device(device)
    path=ROOT/'models'/name
    cfg=AutoConfig.from_pretrained(path,local_files_only=True)
    if yarn:
        cfg.rope_scaling={'rope_type':'yarn','factor':2.5,'original_max_position_embeddings':32768}
        cfg.max_position_embeddings=81920
    model=AutoModelForCausalLM.from_pretrained(path,config=cfg,dtype=getattr(torch,dtype),
            attn_implementation='sdpa',local_files_only=True).eval().to(device)
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True)
    return model,tok

def kvs(cache,cpu=False):
    return tuple((l.keys.detach().cpu() if cpu else l.keys.detach(),
                  l.values.detach().cpu() if cpu else l.values.detach()) for l in cache.layers)

def cache_from(kv,device=None):
    c=DynamicCache()
    for i,(k,v) in enumerate(kv):c.update(k.to(device) if device else k,v.to(device) if device else v,i)
    return c

def prefill(model,ids,cache=None,chunk=256):
    device=model.device
    ids=torch.as_tensor(ids,dtype=torch.long,device=device).reshape(1,-1)
    if cache is None:cache=DynamicCache()
    logits=None
    for a in range(0,ids.shape[1],chunk):
        r=model(input_ids=ids[:,a:a+chunk],past_key_values=cache,use_cache=True,logits_to_keep=1)
        cache,logits=r.past_key_values,r.logits[0,-1]
        if device.type=='mps':torch.mps.synchronize()
    return cache,logits

def decode(model,cache,last,max_new=384,eos=()):
    token=torch.as_tensor(last,dtype=torch.long,device=model.device).reshape(1,-1)
    out=[]; first=None
    for _ in range(max_new):
        r=model(input_ids=token,past_key_values=cache,use_cache=True,logits_to_keep=1)
        logits=r.logits[0,-1]
        if first is None:first=logits.detach().float().cpu()
        token=logits.argmax().reshape(1,1)
        value=int(token.item());out.append(value)
        cache=r.past_key_values
        if value in eos:break
    return out,first

def distributions(a,b):
    x,y=a.double().log_softmax(-1),b.double().log_softmax(-1)
    p,q=x.exp(),y.exp()
    return {'kl':float((p*(x-y)).sum()),'tv':float((p-q).abs().sum()/2),
            'top_same':bool(a.argmax()==b.argmax()),'max_logit_error':float((a-b).abs().max())}

def rotate(x,positions,freq,scale=1.0):
    # Transform in fp32 on the same device; positions address the penultimate axis.
    a=torch.outer(torch.as_tensor(positions,device=x.device).float(),freq.to(x.device).float())
    a=torch.cat([a,a],-1)
    y=x.float();h=y.shape[-1]//2
    return ((y*a.cos()+torch.cat([-y[...,h:],y[...,:h]],-1)*a.sin())*scale).to(x.dtype)

def write(path,body):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(body,indent=2))

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def answer(text):
    text=text.replace('−','-')
    text=re.sub(r'\\frac\{(-?[\d.]+)\}\{([\d.]+)\}',r'\1/\2',text)
    marked='####' in text
    if marked:text=text.rsplit('####',1)[1]
    numbers=re.findall(r'-?(?:\d[\d,]*\.?\d*|\.\d+)(?:/\d+(?:\.\d+)?)?',text)
    if not numbers:return None,marked
    try:return str(Fraction(numbers[-1].replace(',',''))),marked
    except (ValueError,ZeroDivisionError):return None,marked
