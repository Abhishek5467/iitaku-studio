"""Time-bounded training with epoch checkpoints and optimizer/RNG resume.
python training/train.py --pairs /kaggle/input/my-pairs --out /kaggle/working/run --hours 3.5
Checkpoint files are trusted local files; never load a stranger's .pt."""
import argparse
import json
import random
import time
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset,DataLoader
from model import Refiner

class Pairs(Dataset):
    def __init__(self,root,split):
        self.root=Path(root);self.rows=[r for r in json.loads((self.root/"manifest.json").read_text()) if r["split"]==split]
        if not self.rows:raise ValueError(f"No {split} objects. Check the manifest before training.")
    def __len__(self):return len(self.rows)
    def __getitem__(self,i):
        with np.load(self.root/self.rows[i]["file"]) as d:return torch.from_numpy(d["low"].copy())[None],torch.from_numpy(d["high"].copy())[None]

def loss(pred,high):
    weights=1+4*(high.abs()<.5);return ((pred-high).abs()*weights).mean()

def validate(model,loader,device):
    model.eval();scores=[];baseline=[]
    with torch.inference_mode():
        for low,high in loader:
            low=low.to(device);high=high.to(device);scores.append(loss(model(low),high).item());baseline.append(loss(low,high).item())
    return float(np.mean(scores)),float(np.mean(baseline))

def train(a):
    torch.set_num_threads(min(4,torch.get_num_threads()));random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu");model=Refiner(a.width).to(device);optim=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=1e-4)
    amp=device.type=="cuda";scaler=torch.amp.GradScaler("cuda",enabled=amp);start_epoch=0;best=float("inf")
    if a.resume:
        cp=torch.load(a.resume,map_location="cpu",weights_only=False);model.load_state_dict(cp["model"]);optim.load_state_dict(cp["optimizer"]);scaler.load_state_dict(cp["scaler"]);start_epoch=cp["epoch"]+1;best=cp["best"]
        random.setstate(cp["random"]);np.random.set_state(cp["numpy"]);torch.set_rng_state(cp["torch_rng"])
        if amp and cp.get("cuda_rng") is not None:torch.cuda.set_rng_state_all(cp["cuda_rng"])
    trainset=Pairs(a.pairs,"train");valset=Pairs(a.pairs,"val");loader=DataLoader(trainset,batch_size=a.batch,shuffle=True,num_workers=0);val=DataLoader(valset,batch_size=1,num_workers=0)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);deadline=time.monotonic()+a.hours*3600
    for epoch in range(start_epoch,a.epochs):
        model.train();scores=[];t=time.monotonic();partial=False
        for low,high in loader:
            if time.monotonic()>deadline:partial=True;break
            low=low.to(device);high=high.to(device);optim.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type,enabled=amp):prediction=model(low);error=loss(prediction,high)
            scaler.scale(error).backward();scaler.unscale_(optim);torch.nn.utils.clip_grad_norm_(model.parameters(),1);scaler.step(optim);scaler.update();scores.append(error.item())
        val_loss,identity=validate(model,val,device);better=val_loss<best;best=min(best,val_loss)
        row={"epoch":epoch,"train_loss":float(np.mean(scores)) if scores else None,"val_loss":val_loss,"identity_baseline":identity,"seconds":time.monotonic()-t,"partial_epoch":partial};print(json.dumps(row),flush=True)
        cp={"model":model.state_dict(),"optimizer":optim.state_dict(),"scaler":scaler.state_dict(),"epoch":epoch,"best":best,"width":a.width,"seed":a.seed,"random":random.getstate(),"numpy":np.random.get_state(),"torch_rng":torch.get_rng_state(),"cuda_rng":torch.cuda.get_rng_state_all() if amp else None}
        torch.save(cp,out/"last.pt")
        if better:torch.save(cp,out/"best.pt")
        with (out/"metrics.jsonl").open("a") as f:f.write(json.dumps(row)+"\n")
        if partial or time.monotonic()>deadline:break
    (out/"run.json").write_text(json.dumps({**vars(a),"device":str(device),"objects":{"train":len(trainset),"val":len(valset)},"best_val":best},indent=2))
    print("Saved resumable last.pt and best.pt. Assess held-out meshes before any quality claim.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--pairs",required=True);p.add_argument("--out",default="training/runs/pilot");p.add_argument("--hours",type=float,default=3.5);p.add_argument("--epochs",type=int,default=500);p.add_argument("--width",type=int,default=12);p.add_argument("--batch",type=int,default=2);p.add_argument("--lr",type=float,default=2e-4);p.add_argument("--seed",type=int,default=42);p.add_argument("--resume");train(p.parse_args())
