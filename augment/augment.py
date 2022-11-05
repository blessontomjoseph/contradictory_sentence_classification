from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import pandas as pd
from tqdm import trange, tqdm
import warnings
warnings.simplefilter('ignore')


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torch.load('../usr/lib/mdw_model_translation/model_arch')
model.load_state_dict(torch.load(
    '../usr/lib/mdw_model_translation/model_state'))
model.to(device)
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")


data=pd.read_csv('../input/contradictory-my-dear-watson/train.csv')
from_lang=['en']
to_lang_=[i for i in data.lang_abv.unique() if i!='en']
to_lang=[i for i in to_lang_ if i not in ['ar','bg','de','fr','ru','th','tr','ur']]

def Augment():
    for lang in from_lang: #converting a perticular lang
        conv_from=data[data['lang_abv']==lang] #data in that specific lang

        for other_lang in to_lang: #converting to all the other langs
            mini=pd.DataFrame(columns=['premise','hypothesis','lang_abv','label'],index=range(len(conv_from)))
            conv_from.reset_index(drop=True,inplace=True)
            mini['label']=conv_from['label']

            for i in trange(len(conv_from),desc='wait boss...'): #looping through each rowas of that perticular lang data to convert from it
                pre_text = conv_from.premise.iloc[i]
                hyp_text = conv_from.hypothesis.iloc[i]
                tokenizer.src_lang = lang  #*

                encoded_hy = tokenizer(hyp_text, return_tensors="pt")
                encoded_hy={k:v.to(device) for k,v in encoded_hy.items()}
                generated_tokens_hy = model.generate(**encoded_hy, forced_bos_token_id=tokenizer.get_lang_id(other_lang))
                sent_hy=tokenizer.batch_decode(generated_tokens_hy, skip_special_tokens=True)

                encoded_pre = tokenizer(pre_text, return_tensors="pt")
                encoded_pre={k:v.to(device) for k,v in encoded_pre.items()}
                generated_tokens_pre = model.generate(**encoded_pre, forced_bos_token_id=tokenizer.get_lang_id(other_lang))
                sent_pre=tokenizer.batch_decode(generated_tokens_pre, skip_special_tokens=True)

                mini.hypothesis.iloc[i]=sent_hy[0]
                mini.premise.iloc[i]=sent_pre[0]
                mini.lang_abv.iloc[i]=other_lang    
            mini.to_csv(lang+'_to_'+other_lang+'.csv',header=True)
            
if __name__=='__main__':
    Augment()