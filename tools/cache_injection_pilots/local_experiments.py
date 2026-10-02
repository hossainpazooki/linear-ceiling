import gc, hashlib, json, os, time
from pathlib import Path

ROOT = Path(__file__).parent
os.environ['HF_HOME'] = str(ROOT/'hf')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

torch.set_num_threads(4)
torch.set_grad_enabled(False)
TAUS = [0.3186442653116294, 0.10, 0.03]
MODE = os.environ.get('LOCAL_STUDY', 'initial')
OUT = ROOT/('local-results' if MODE=='initial' else 'local-results-highcoverage')
OUT.mkdir(exist_ok=True)
rows = []

def arrays(cache):
    return tuple((layer.keys.detach(), layer.values.detach()) for layer in cache.layers)

def evaluate(model, kv, token):
    cache = DynamicCache.from_legacy_cache(kv)
    return model(input_ids=token, past_key_values=cache, use_cache=True).logits[0, -1].float()

def measure(ref, logits):
    lp, lq = ref.double().log_softmax(-1), logits.double().log_softmax(-1)
    p, q = lp.exp(), lq.exp()
    return {'kl': float((p*(lp-lq)).sum()), 'tv': float((p-q).abs().sum()/2),
            'top_same': bool(ref.argmax()==logits.argmax()),
            'top_reference': int(ref.argmax()), 'top_arm': int(logits.argmax()),
            'max_logit_error': float((ref-logits).abs().max())}

def rotate(k, positions, freq):
    angle = torch.outer(positions.float(), freq.float())
    angle = torch.cat([angle, angle], -1)
    half = k.shape[-1]//2
    perpendicular = torch.cat([-k[..., half:], k[..., :half]], -1)
    return k*angle.cos() + perpendicular*angle.sin()

def fstar(d, tau):
    ordered = np.sort(d)
    good = np.flatnonzero(np.cumsum(ordered)/np.arange(1,len(d)+1) <= tau*(1+1e-9)+1e-15)
    return 1-(int(good[-1])+1)/len(d) if len(good) else 1.0

def deviation(old, new, freq):
    n = new[0][0].shape[-2]
    result = {}
    for index, name in [(0,'K'),(1,'V')]:
        deviations = []
        for a,b in zip(old,new):
            x,y = a[index][0].double(), b[index][0].double()
            if index==0:
                x=rotate(x,-torch.arange(n),freq).double()
                y=rotate(y,-torch.arange(n),freq).double()
            den = ((y-y.mean(1,keepdim=True))**2).sum(-1).mean(1)
            assert bool((den>0).all())
            deviations.append((((x-y)**2).sum(-1)/den[:,None]).mean(0).numpy())
        d=np.mean(deviations,axis=0)
        result[name]={'mean':float(d.mean()),'max':float(d.max()),
                      'fstar':{str(t):fstar(d,t) for t in TAUS},
                      'exceed':{str(t):float((d>t).mean()) for t in TAUS}}
    return result

def save(row):
    rows.append(row)
    (OUT/'results.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps(row), flush=True)

report=json.loads((ROOT/'records/e9/report.json').read_text())
ordered=sorted(report['scores'].items())
selected=ordered[:8] if MODE=='initial' else [ordered[i] for i in np.rint(np.linspace(0,len(ordered)-1,8)).astype(int)]
examples=[]
for hid,rec in selected:
    with np.load(ROOT/'records/e9/align'/rec['score_file'].replace('.json','.npz')) as z:
        s,r,p=z['sender'],z['receiver'],z['pairs']
        change=np.flatnonzero((np.diff(p[:,0]-p[:,1],prepend=p[0,0]-p[0,1])!=0)&(p[:,1]>=32)&(p[:,0]>=32))
        if MODE=='initial':
            ps,pr=p[int(change[0]) if len(change) else len(p)//2]
        else:
            breaks=np.flatnonzero(np.any(np.diff(p,axis=0)!=1,axis=1))+1
            starts=np.r_[0,breaks]; ends=np.r_[breaks,len(p)]
            candidates=[int(a) for a,b in zip(starts,ends) if b-a>=128 and p[a,1]>=32]
            assert candidates, hid
            ps,pr=p[candidates[0]]
        ss,rs=max(0,int(ps)-128),max(0,int(pr)-128)
        sw,rw=s[ss:ss+256],r[rs:rs+256]
        pp=p- [ss,rs]
        keep=(pp[:,0]>=0)&(pp[:,0]<len(sw))&(pp[:,1]>=0)&(pp[:,1]<len(rw)-1)
        examples.append({'id':hid,'s':sw.tolist(),'r':rw.tolist(),'pairs':pp[keep].tolist(),
                         'sender_start':ss,'receiver_start':rs})
(OUT/'inputs.json').write_text(json.dumps(examples))
print('FROZEN_INPUTS', hashlib.sha256((OUT/'inputs.json').read_bytes()).hexdigest(), flush=True)

qpath=ROOT/'models/qwen'
qtok=AutoTokenizer.from_pretrained(qpath,local_files_only=True)
texts=[qtok.decode(e['r'],skip_special_tokens=True) for e in examples]
model=AutoModelForCausalLM.from_pretrained(qpath,torch_dtype=torch.float32,attn_implementation='sdpa',local_files_only=True).eval()
freq=model.model.rotary_emb.inv_freq.detach()
for i,e in enumerate(examples):
    t=time.perf_counter()
    s=torch.tensor([e['s']]); r=torch.tensor([e['r']]); p=torch.tensor(e['pairs'])
    assert len(p)>0
    assert torch.equal(s[0,p[:,0]],r[0,p[:,1]])
    fresh=arrays(model(input_ids=r[:,:-1],use_cache=True,logits_to_keep=1).past_key_values)
    native=model(input_ids=r,use_cache=False,logits_to_keep=1).logits[0,-1]
    identity=evaluate(model,fresh,r[:,-1:])
    identity_check=measure(native,identity)
    assert identity_check['max_logit_error'] <= 1e-4, identity_check
    old=arrays(model(input_ids=s,use_cache=True,logits_to_keep=1).past_key_values)
    arm_results={}
    rng=np.random.default_rng(23)
    permutation=np.roll(rng.permutation(len(p)),1)
    for arm,srcrows in [('stale',p[:,0]),('permuted',p[permutation,0])]:
        mixed=[]
        for (fk,fv),(sk,sv) in zip(fresh,old):
            k,v=fk.clone(),fv.clone()
            k[:,:,p[:,1],:]=rotate(sk[:,:,srcrows,:],p[:,1]-srcrows,freq)
            v[:,:,p[:,1],:]=sv[:,:,srcrows,:]
            mixed.append((k,v))
        arm_results[arm]=measure(identity,evaluate(model,tuple(mixed),r[:,-1:]))
    save({'experiment':'injection','id':e['id'],'matched':len(p),'prefix':len(e['r'])-1,
          'identity':identity_check,**arm_results,'seconds':time.perf_counter()-t})
    del fresh,old,mixed,k,v,native,identity
del model,qtok,freq
gc.collect()
if MODE!='initial':
    print('COMPLETE',len(rows),flush=True)
    raise SystemExit(0)

for step in [200,1200,2600]:
    path=ROOT/'models'/f'olmo{step}'
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True)
    ids=[tok(text,return_tensors='pt',truncation=True,max_length=256).input_ids for text in texts]
    if step==200:
        frozen=[x.tolist() for x in ids]
        (OUT/'olmo-inputs.json').write_text(json.dumps(frozen))
    else:
        assert [x.tolist() for x in ids]==frozen
    model=AutoModelForCausalLM.from_pretrained(path,torch_dtype=torch.float32,attn_implementation='sdpa',local_files_only=True).eval()
    freq=model.model.rotary_emb.inv_freq.detach()
    for i,r in enumerate(ids):
        t=time.perf_counter()
        fresh=arrays(model(input_ids=r[:,:-1],use_cache=True,logits_to_keep=1).past_key_values)
        native=model(input_ids=r,use_cache=False,logits_to_keep=1).logits[0,-1]
        ref=evaluate(model,fresh,r[:,-1:])
        control=measure(native,ref)
        assert control['max_logit_error']<=1e-4, control
        save({'experiment':'olmo-identity','step':step,'i':i,**control,'seconds':time.perf_counter()-t})
        for anchor in [a for a in [200,1200] if a<step]:
            old=torch.load(OUT/f'cache-{anchor}-{i}.pt',weights_only=True)
            save({'experiment':'holdover','writer':anchor,'reader':step,'i':i,'n':r.shape[1]-1,
                  'tensor':deviation(old,fresh,freq),'output':measure(ref,evaluate(model,old,r[:,-1:]))})
            del old
        if step in [200,1200]:
            torch.save(fresh,OUT/f'cache-{step}-{i}.pt')
        del fresh,native,ref
    del model,tok,freq
    gc.collect()
print('COMPLETE',len(rows),flush=True)
