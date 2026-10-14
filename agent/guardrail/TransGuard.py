from agent.guardrail.utils.Translate import Translate

'''
输入:context
输出:过滤context
此模块专门用于识别和翻译非英文文本
'''

class TranslateGuard:
    """
    翻译模块
    """
    def __init__(self):
        self.translateTool = Translate()

    def translate(self,text):
        try:
            return self.translateTool.translate_zh_en(text)
        except Exception as e:
            print(f"[WARN] 翻译失败，回退使用原文: {e}")
            return text