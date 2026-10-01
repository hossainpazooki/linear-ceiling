from common import *
from datasets import load_dataset
repo='openai/gsm8k'
meta={'sha':'740312add88f781978c0658806c59bc2815b9866'}
ds=load_dataset(repo,'main',revision=meta['sha'],cache_dir=str(ROOT/'hf/datasets'))
tok=AutoTokenizer.from_pretrained(ROOT/'models/olmo200',local_files_only=True)
seed=230923
demo_idx=np.random.default_rng(seed).choice(len(ds['train']),8,replace=False).tolist()
test_idx=np.random.default_rng(seed).choice(len(ds['test']),64,replace=False).tolist()
demonstrations=[]
for i in demo_idx:
    x=ds['train'][i]
    demonstrations.extend([{'role':'user','content':x['question']+'\nSolve step by step and finish with #### followed by the numeric answer.'},
                           {'role':'assistant','content':x['answer']}])
items=[]
for i in test_idx:
    x=ds['test'][i]
    messages=demonstrations+[{'role':'user','content':x['question']+'\nSolve step by step and finish with #### followed by the numeric answer.'}]
    ids=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True)
    items.append({'id':i,'question':x['question'],'answer':x['answer'],'ids':ids})
path=ROOT/'math-inputs.json'
write(path,{'dataset_revision':meta['sha'],'demo_idx':demo_idx,'test_idx':test_idx,'items':items})
print('FROZEN',digest(path),'prompt_tokens',min(len(x['ids']) for x in items),max(len(x['ids']) for x in items),flush=True)
