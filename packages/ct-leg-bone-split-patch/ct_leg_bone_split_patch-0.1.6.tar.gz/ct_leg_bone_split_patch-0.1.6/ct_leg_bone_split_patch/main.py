from .unet import UNet
from .blur import gaussian_smooth_2d
from .pth_list import download_all_pth, MODEL_PATH, MRI_MODEL_PATH

from PIL import Image
from torchvision import transforms
import torch
import functools
import os
import numpy as np
from typing import List
from io import BytesIO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMAGE_SIZE = (256, 256)

def merge_files_to_state_dict(folder_path: str) -> dict:
    file_list: List[str] = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    file_list.sort()
    
    merged_bytes = b""
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "rb") as f:
            merged_bytes += f.read()  # 拼接二进制内容
    
    try:
        state_dict = torch.load(
            BytesIO(merged_bytes),
            map_location=torch.device(DEVICE)
        )
        return state_dict
    except Exception as e:
        raise RuntimeError(f"解析合并后的模型数据失败：{e}") from e

@functools.lru_cache(maxsize=2)
def load_unet_model(mri=False) -> UNet:
    download_all_pth()
    
    unet = UNet(n_channels=1, n_classes=1, bilinear=False)
    unet.to(DEVICE)
    if not mri:
        unet.load_state_dict(merge_files_to_state_dict(MODEL_PATH))
    else:
        unet.load_state_dict(merge_files_to_state_dict(MRI_MODEL_PATH))
    unet.eval()
    return unet

def map_image(grey_image: Image.Image, mri=False) -> Image.Image:
    base_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize(IMAGE_SIZE),
    ])
    
    image_normalize = transforms.Normalize(
        mean=[0.457],
        std=[0.226]
    )

    grey_pil = grey_image.convert("L")
    tensor = base_transform(grey_pil)
    tensor = image_normalize(tensor)
    
    assert tensor.ndim == 3, f"Tensor维度必须为3，当前{tensor.ndim}维"
    images = tensor.unsqueeze(0).to(DEVICE)  # (1, 1, 256, 256)

    unet = load_unet_model(mri)
    with torch.no_grad():
        output_bone = unet(images)
        assert output_bone.ndim == 4, f"模型输出维度必须为4，当前{output_bone.ndim}维"

        cpu_data = gaussian_smooth_2d(output_bone.squeeze(dim=(0, 1)).cpu().numpy())
        cpu_data = np.clip(cpu_data, 0, 1)
        cpu_data_uint8 = (cpu_data * 255).astype(np.uint8)

        new_image = Image.fromarray(cpu_data_uint8, mode="L")
        new_image = new_image.resize(grey_image.size, Image.Resampling.LANCZOS)

    return new_image
