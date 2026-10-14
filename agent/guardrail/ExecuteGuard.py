'''
输入:context
输出:过滤context
此模块执行所有护栏清理流程
'''
from agent.guardrail.RegexGuard import MultiPatternMatcher
from agent.guardrail.TransGuard import TranslateGuard
from agent.guardrail.utils.Guard import GuardRail


class ExecuteGuardRail:
    def __init__(self):
        self.guardrail = GuardRail()
        self.translate_tool = TranslateGuard()

    #第一步：去除标签
    #第二步：翻译分流+护栏分析
    #第三步：尾处理
    #第四步：添加标签

    def step_One(self, context):
        # 第一步：去除标签
        dangerous_labels=[
            "<system>",
            "</system>",
            "<userInput>",
            "</userInput>",
            "<reasoning>",
            "</reasoning>",
            "<tool>",
            "</tool>",
            "<acting>",
            "</acting>",
            "<MALICIOUS>",
            "<SAFE>"

        ]
        multipartern_matcher = MultiPatternMatcher(dangerous_labels)
        return multipartern_matcher.remove_matches(context)
    def step_Two(self, context):
        # 第二步：翻译分流+护栏分析
        translate_tool = self.translate_tool
        guardrail = self.guardrail
        context_ori = context
        context_trs = translate_tool.translate(context)
        r1 = (guardrail.check_injection(context_ori) and guardrail.check_injection(context_trs))
        if r1:
            r2 = (guardrail.check_firewall(context_ori) and guardrail.check_firewall(context_trs))
            if r2:
                return True
            else:
                return False
        else:
            return False
    def step_Three(self, context):
        # 第三步：尾处理
        return context
    def step_Four(self,context, label):
        # 第四步：添加标签
        return "<" + label + ">" + context + "</" + label + ">"
    def execute(self, context, label):
        # 步骤执行
        c1 = self.step_One(context)#去除外来标签
        if not self.step_Two(c1):#双检测
            return ["1",""]
        c2 = self.step_Three(c1)#尾处理
        c3 = self.step_Four(c2, label)#添加标签
        return ["0",c3]

