# ct_leg_bone_split_patch
Given a 128×128 grayscale image representing a CT/MRI cross-sectional slice, identify bone tissue from it and generate a binary mask.

## Installation
```bash
pip install ct_leg_bone_split_patch
```

## Usage

processing CT image.

```python
from PIL import Image
from ct_leg_bone_split_patch import map_image

img_in  = Image.open("path/to/file")
img_out = map_image(img_in)

img_out.save("path/to_file")
```

processing MRI image.

```python
from PIL import Image
from ct_leg_bone_split_patch import map_image

img_in  = Image.open("path/to/file")
img_out = map_image(img_in, mri=True)

img_out.save("path/to_file")
```
