from common import *
import argparse
ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['writer','reader']);ap.add_argument('--device',default='mps');ap.add_argument('--dtype',default='float32');a=ap.parse_args()
data=json.loads((ROOT/'math-inputs.json').read_text())
items=data['items'];folder=ROOT/'math';folder.mkdir(exist_ok=True)
write(folder/'run-settings.json',{'device':a.device,'dtype':a.dtype,'input_sha256':digest(ROOT/'math-inputs.json'),'cap':384})

def fstar(d,t):
    z=np.sort(d);ok=np.flatnonzero(np.cumsum(z)/np.arange(1,len(z)+1)<=t*(1+1e-9)+1e-15)
    return 1-(int(ok[-1])+1)/len(z) if len(ok) else 1.0

def tensor_readout(old,fresh,freq):
    n=fresh[0][0].shape[-2];pos=torch.arange(0,n,4);all_d=[]
    for (ok,_),(fk,_) in zip(old,fresh):
        x=rotate(ok[:,:,pos,:],-pos,freq).double()[0]
        y=rotate(fk[:,:,pos,:],-pos,freq).double()[0]
        den=((y-y.mean(1,keepdim=True))**2).sum(-1).mean(1)
        assert bool((den>0).all())
        all_d.append((((x-y)**2).sum(-1)/den[:,None]).mean(0).numpy())
    d=np.mean(all_d,axis=0)
    return {'n_scored':len(d),'mean':float(d.mean()),'max':float(d.max()),
            'fstar':{str(t):fstar(d,t) for t in [.3186442653116294,.1,.03]}}

if a.phase=='writer':
    model,tok=load('olmo200',a.device,a.dtype);times=[]
    for i,x in enumerate(items):
        path=folder/f'old-{i}.pt'
        sync();t=time.perf_counter();c,_=prefill(model,x['ids'][:-1]);sync();elapsed=time.perf_counter()-t
        torch.save(kvs(c,cpu=True),path);del c
        times.append(elapsed);print(json.dumps({'phase':'writer','i':i,'id':x['id'],'tokens':len(x['ids'])-1,'seconds':elapsed}),flush=True)
        if i%8==7:clear()
    write(folder/'writer-times.json',times)
else:
    model,tok=load('olmo2600',a.device,a.dtype);freq=model.model.rotary_emb.inv_freq.detach().cpu()
    eos=model.generation_config.eos_token_id
    eos=set(eos if isinstance(eos,list) else [eos]);results=[]
    for i,x in enumerate(items):
        old=torch.load(folder/f'old-{i}.pt',weights_only=True,mmap=True)
        sync();t=time.perf_counter();c,_=prefill(model,x['ids'][:-1]);sync();prefill_s=time.perf_counter()-t
        fresh=kvs(c,cpu=True);del c
        gold,_=answer(x['answer']);row={'i':i,'id':x['id'],'gold':gold,'fresh_prefill_s':prefill_s,
                                      'tensor':tensor_readout(old,fresh,freq)}
        # Alternate decode order; the reader weights and input IDs are identical.
        for arm in (['fresh','stale'] if i%2==0 else ['stale','fresh']):
            c=cache_from(fresh if arm=='fresh' else old,a.device)
            sync();t=time.perf_counter();ids,first=decode(model,c,x['ids'][-1:],384,eos);sync();elapsed=time.perf_counter()-t
            text=tok.decode(ids,skip_special_tokens=True);pred,marked=answer(text)
            row[arm]={'ids':ids,'text':text,'answer':pred,'has_marker':marked,'correct':pred==gold,
                      'truncated':len(ids)==384 and ids[-1] not in eos,'decode_s':elapsed}
            if arm=='fresh':fresh_logits=first
            else:stale_logits=first
            del c
        row['next_token']=distributions(fresh_logits,stale_logits)
        if i<4:
            # A separately recomputed same-weight cache exercises rebuild/transport/decode.
            c,_=prefill(model,x['ids'][:-1]);z,_=decode(model,c,x['ids'][-1:],384,eos)
            row['zero_lag_exact']=z==row['fresh']['ids'];assert row['zero_lag_exact'],row['id'];del c
            n=old[0][0].shape[-2];perm=torch.roll(torch.arange(n),n//2);bad=[]
            for k,v in old:
                bad.append((rotate(k[:,:,perm,:],torch.arange(n)-perm,freq),v[:,:,perm,:]))
            c=cache_from(bad,a.device);z,_=decode(model,c,x['ids'][-1:],384,eos)
            text=tok.decode(z,skip_special_tokens=True);pred,_=answer(text)
            row['scrambled']={'text':text,'answer':pred,'correct':pred==gold,'n_tokens':len(z)}
            del c,bad
        results.append(row);write(folder/'results.json',results)
        print(json.dumps({'i':i,'id':x['id'],'fresh':row['fresh']['correct'],'stale':row['stale']['correct'],
             'fresh_answer':row['fresh']['answer'],'stale_answer':row['stale']['answer'],
             'tokens':[len(row[z]['ids']) for z in ['fresh','stale']],
             'truncated':[row[z]['truncated'] for z in ['fresh','stale']],
             'fstar03':row['tensor']['fstar']['0.03']}),flush=True)
        del fresh,old,fresh_logits,stale_logits
        clear()
    print('COMPLETE',len(results),flush=True)
