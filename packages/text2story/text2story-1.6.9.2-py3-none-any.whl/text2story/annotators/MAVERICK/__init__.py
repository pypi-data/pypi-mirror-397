from maverick import Maverick
from text2story.core.exceptions import InvalidLanguage
from omegaconf import DictConfig, ListConfig, OmegaConf
import torch

# Register OmegaConf's DictConfig as safe for torch.load
torch.serialization.add_safe_globals([DictConfig, ListConfig, OmegaConf])

from lightning_fabric.utilities import cloud_io
original_load = cloud_io._load

def patched_load(path_or_url, map_location=None, weights_only=None):
    # Force weights_only=False for MAVERICK checkpoints
    return original_load(path_or_url, map_location=map_location, weights_only=False)

cloud_io._load = patched_load



pipeline = {}
def load(lang):
    if lang == "en":
        pipeline['coref_en'] = Maverick(hf_name_or_path="sapienzanlp/maverick-mes-ontonotes", device="cpu")
    else:
        raise InvalidLanguage(lang)

def extract_objectal_links(lang, text):
    prediction = pipeline['coref_en'].predict(text)

    cluster_indexes_list = prediction["clusters_char_offsets"]
    # for some reason, maverick model is cutting the last character
    #, so in the following line we update the end

    cluster_indexes_list = [[ (start, end + 1) for (start, end) in cluster]   for cluster in cluster_indexes_list]

    return cluster_indexes_list

