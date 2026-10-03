"""RRDB anime-6B inference architecture, adapted from MIT-licensed BasicSR.
Architecture credit: Xintao Wang / BasicSR, github.com/XPixelGroup/BasicSR.
Load official Real-ESRGAN anime-6B weights; no training is done by this worker."""
import torch
from torch import nn
from torch.nn import functional as F

class DenseBlock(nn.Module):
    def __init__(self):
        super().__init__()
        for i in range(1,6): setattr(self,f"conv{i}",nn.Conv2d(64+32*(i-1),32 if i<5 else 64,3,1,1))
        self.lrelu=nn.LeakyReLU(.2,inplace=True)
    def forward(self,x):
        parts=[x]
        for i in range(1,5):parts.append(self.lrelu(getattr(self,f"conv{i}")(torch.cat(parts,1))))
        return x+self.conv5(torch.cat(parts,1))*.2

class RRDB(nn.Module):
    def __init__(self):
        super().__init__();self.rdb1=DenseBlock();self.rdb2=DenseBlock();self.rdb3=DenseBlock()
    def forward(self,x):return x+self.rdb3(self.rdb2(self.rdb1(x)))*.2

class AnimeRRDB(nn.Module):
    def __init__(self):
        super().__init__();self.conv_first=nn.Conv2d(3,64,3,1,1);self.body=nn.Sequential(*[RRDB() for _ in range(6)])
        self.conv_body=nn.Conv2d(64,64,3,1,1);self.conv_up1=nn.Conv2d(64,64,3,1,1);self.conv_up2=nn.Conv2d(64,64,3,1,1)
        self.conv_hr=nn.Conv2d(64,64,3,1,1);self.conv_last=nn.Conv2d(64,3,3,1,1);self.lrelu=nn.LeakyReLU(.2,inplace=True)
    def forward(self,x):
        feat=self.conv_first(x);feat=feat+self.conv_body(self.body(feat))
        feat=self.lrelu(self.conv_up1(F.interpolate(feat,scale_factor=2,mode="nearest")))
        feat=self.lrelu(self.conv_up2(F.interpolate(feat,scale_factor=2,mode="nearest")))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))
