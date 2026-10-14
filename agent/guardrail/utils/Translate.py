import os

# ---- 禁止 stanza 联网（stanza>=1.4 不再读取 STANZA_NO_NETWORK 环境变量）----
import stanza
from stanza.pipeline.core import DownloadMethod

_orig_pipeline_init = stanza.Pipeline.__init__

def _no_download_pipeline_init(self, *args, **kwargs):
    kwargs.setdefault("download_method", DownloadMethod.NONE)
    _orig_pipeline_init(self, *args, **kwargs)

stanza.Pipeline.__init__ = _no_download_pipeline_init
# --------------------------------------------------------------------------

import argostranslate.translate

class Translate:
    """
    翻译模块
    """
    def __init__(self):
        try:
            self.zh_to_en = argostranslate.translate.get_translation_from_codes("zh", "en")
        except Exception as e:
            print(f"[WARN] 翻译模型加载失败，将使用原文检测: {e}")
            self.zh_to_en = None

    def translate_zh_en(self,text):
        if self.zh_to_en is None:
            return text
        try:
            return self.zh_to_en.translate(text)
        except Exception as e:
            print(f"[WARN] 翻译运行时失败，后续将使用原文: {e}")
            self.zh_to_en = None
            return text
