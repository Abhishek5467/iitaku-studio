"""Download official anime-6B weights, never deserialize a user-supplied checkpoint."""
from pathlib import Path
from urllib.request import urlretrieve
URL="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
if __name__=="__main__":
    target=Path(__file__).resolve().parent/"weights/RealESRGAN_x4plus_anime_6B.pth";target.parent.mkdir(exist_ok=True)
    temporary=target.with_suffix(".download");urlretrieve(URL,temporary);temporary.replace(target)
    print("Downloaded official anime-6B checkpoint. Review upstream model terms before commercial deployment.")
