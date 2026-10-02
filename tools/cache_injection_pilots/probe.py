from common import *
out=[]
for device,dtype in [('cpu','float32'),('mps','float32'),('mps','float16')]:
    model,tok=load('olmo200',device,dtype)
    ids=tok('Alice has 12 apples. She gives away 5 apples. How many apples does she have left? '*12).input_ids
    c,_=prefill(model,ids[:32]);del c
    sync();t=time.perf_counter();c,_=prefill(model,ids[:-1]);sync();prefill_s=time.perf_counter()-t
    saved=kvs(c,cpu=True)
    sync();t=time.perf_counter();generated,first=decode(model,c,ids[-1:],max_new=24);sync();decode_s=time.perf_counter()-t
    c=cache_from(saved,device);again,first2=decode(model,c,ids[-1:],max_new=24)
    record={'device':device,'dtype':dtype,'prefill_tokens':len(ids)-1,'prefill_s':prefill_s,
            'decode24_s':decode_s,'zero_lag_exact':generated==again,'roundtrip':distributions(first,first2)}
    out.append(record);print(json.dumps(record),flush=True)
    del model,tok,c,saved,first,first2
    clear()
write(ROOT/'probe-results.json',out)
