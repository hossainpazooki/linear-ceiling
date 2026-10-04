import gc,json,os,time
from pathlib import Path
ROOT=Path(__file__).parent
os.environ['HF_HOME']=str(ROOT/'hf')
import torch
from transformers import AutoModelForCausalLM,DynamicCache
torch.set_num_threads(4)
torch.set_grad_enabled(False)
out=[]
control_only=os.environ.get('ZERO_LAG_CONTROL')=='1'
inputs=json.loads((ROOT/'local-results/olmo-inputs.json').read_text())

def decode(model,kv,token):
    cache=DynamicCache.from_legacy_cache(kv)
    result=[]
    for _ in range(32):
        r=model(input_ids=token,past_key_values=cache,use_cache=True,logits_to_keep=1)
        token=r.logits[:,-1].argmax(-1,keepdim=True)
        result.append(int(token.item()))
        cache=r.past_key_values
    return result

for step in ([1200] if control_only else [1200,2600]):
    model=AutoModelForCausalLM.from_pretrained(ROOT/'models'/f'olmo{step}',dtype=torch.float32,attn_implementation='sdpa',local_files_only=True).eval()
    for i,values in enumerate(inputs):
        r=torch.tensor(values)
        cache=model(input_ids=r[:,:-1],use_cache=True,logits_to_keep=1).past_key_values
        kv=tuple((l.keys,l.values) for l in cache.layers)
        fresh=decode(model,kv,r[:,-1:])
        for writer in ([1200] if control_only else [a for a in [200,1200] if a<step]):
            old=torch.load(ROOT/'local-results'/f'cache-{writer}-{i}.pt',weights_only=True)
            stale=decode(model,old,r[:,-1:])
            mismatch=[j for j,(a,b) in enumerate(zip(fresh,stale)) if a!=b]
            row={'writer':writer,'reader':step,'i':i,'identical':not mismatch,
                 'first_difference':mismatch[0]+1 if mismatch else None,'mismatched_positions':len(mismatch),
                 'fresh':fresh,'stale':stale}
            out.append(row)
            name='zero-lag-continuations.json' if control_only else 'continuations.json'
            (ROOT/'local-results'/name).write_text(json.dumps(out,indent=2))
            print(json.dumps({k:v for k,v in row.items() if k not in ['fresh','stale']}),flush=True)
            del old
        del kv,cache
    del model
    gc.collect()
print('COMPLETE',len(out),flush=True)
