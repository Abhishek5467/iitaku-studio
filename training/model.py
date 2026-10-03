"""Compact residual SDF refiner. Predicting detail is not recovering missing truth."""
import torch
from torch import nn
from torch.nn import functional as F

def block(a,b):return nn.Sequential(nn.Conv3d(a,b,3,padding=1),nn.GroupNorm(4 if b>=4 else 1,b),nn.SiLU(),nn.Conv3d(b,b,3,padding=1),nn.GroupNorm(4 if b>=4 else 1,b),nn.SiLU())

class Refiner(nn.Module):
    def __init__(self,width=12):
        super().__init__();self.enc=block(1,width);self.middle=block(width,width*2);self.dec=block(width*3,width);self.out=nn.Conv3d(width,1,1)
        nn.init.zeros_(self.out.weight);nn.init.zeros_(self.out.bias)
    def forward(self,x):
        e=self.enc(x);m=self.middle(F.avg_pool3d(e,2));m=F.interpolate(m,size=e.shape[2:],mode="trilinear",align_corners=False)
        return (x+.15*torch.tanh(self.out(self.dec(torch.cat([e,m],1))))).clamp(-1,1)
