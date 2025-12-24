import os
from remote_auto_fetch import remote_auto_fetch

DIRNOW = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(DIRNOW, "model")
MRI_MODEL_PATH = os.path.join(DIRNOW, "mri_model")

class NetworkError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

PTH_LIST = {
    os.path.join(MODEL_PATH, f"unet_model_part_00{i:01d}.pth"): 
        f"https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/pth_binary/unet_model_part_00{i:01d}.pth"
    for i in range(0, 3 + 1)
}

PTH_LIST.update({
    os.path.join(MRI_MODEL_PATH, f"mri_best_model_a{chr(i)}.pth"): 
        f"https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_a{chr(i)}.pth"
    for i in range(ord('a'), ord('l') + 1)
})

HASH_VALUE = {
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/pth_binary/unet_model_part_000.pth"   : "476d47d31437a62710f3d6a56024df17",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/pth_binary/unet_model_part_001.pth"   : "ca1c6c8d3d5a25d32a332a373cfedef9",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/pth_binary/unet_model_part_002.pth"   : "102f998105f7fa398befb58e06f42e42",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/pth_binary/unet_model_part_003.pth"   : "c746d571f84c0f030f6d29506f292229",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_aa.pth" : "5e4bc4e849099f0b36b976d4df153b96",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ab.pth" : "0891480debd1ddc0cbaf2595a392a320",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ac.pth" : "425b09e29f9e67eba09e4bda6fba4efa",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ad.pth" : "d2c69772131cb3a2b80fcd6e6da255dd",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ae.pth" : "d133e462067095f171ed40c018174434",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_af.pth" : "e7f39f66d59537652100c7c5025d0ebc",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ag.pth" : "4f0de627ff6f31c8db9c8f416548ab92",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ah.pth" : "f8c80bebc14f893af575f69899b3719c",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ai.pth" : "9e95ca8f87f3cde97f85bd2f5c18a1db",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_aj.pth" : "9cca59e2b493caa3fc581c0502f7fd54",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_ak.pth" : "cb7c45327ec62f485a48cc2578901eb4",
    "https://github.com/GGN-2015/ct_leg_bone_split_patch/releases/download/mri_pth_binary/mri_best_model_al.pth" : "4c1f4da89d26db5b3922c9aea837f01e",
}

def download_all_pth(MAX_TRY:int=5):
    print(f"\033[1;33mdownloading {len(PTH_LIST)} files ...\033[0m")
    for filepath in PTH_LIST:
        file_url = PTH_LIST[filepath]
        remote_auto_fetch(file_url, filepath, HASH_VALUE.get(file_url), max_try=MAX_TRY)
    for filepath in PTH_LIST:
        assert os.path.isfile(filepath)
