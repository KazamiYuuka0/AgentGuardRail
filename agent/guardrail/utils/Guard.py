from llamafirewall import LlamaFirewall, Role, ScannerType, UserMessage, ScanDecision
from injectionguard import detect

'''
输入:context
输出:bool
只提供护栏能力
'''

class GuardRail:
    """AI 安全护栏，封装注入检测与防火墙扫描，支持多级联检。"""

    def __init__(
        self,
        block_threshold: float = 0.7,
        suspicious_threshold: float = 0.3,
        enable_translate: bool = True,
    ):
        """
        :param block_threshold:       防火墙分数高于此值直接拒绝
        :param suspicious_threshold:  防火墙分数低于此值判定为安全
        :param enable_translate:      是否在检测前将中文翻译为英文
        """
        self.block_threshold = block_threshold
        self.suspicious_threshold = suspicious_threshold
        self.enable_translate = enable_translate

        self.firewall = LlamaFirewall(
            scanners={
                Role.USER: [ScannerType.PROMPT_GUARD],
            }
        )

        # 预热：在创建时就加载模型，避免首次检测时延迟
        self._warmup()

    def _warmup(self):
        """预热模型，避免首次调用时的懒加载延迟。"""
        try:
            dummy = "warmup"
            self.firewall.scan(UserMessage(content=dummy))
            detect(dummy)
            print("[GuardRail] 模型预热完成")
        except Exception as e:
            print(f"[GuardRail] 预热失败(不影响正常使用): {e}")

    # ---- 检测层 ----

    def check_injection(self, user_input: str) -> bool:
        """
        injectionguard 注入攻击检测
        :return: True=安全，False=检测到注入
        """
        result = detect(user_input)

        #print("[injection]过滤器分析:")
        #print(f"  是否安全  : {result.is_safe}")
        #print(f"  威胁等级  : {result.threat_level.value}")
        #print(f"  检测详情  : {result.detections}")

        if not result.is_safe:
            print(f"  [拒绝][代码检测] 原因：{result.detections}，风险分：{result.threat_level.value}")
            return False
        print(f"  [放行][代码检测] 原因：{result.detections}，风险分：{result.threat_level.value}")
        return True

    def check_firewall(self, user_input: str) -> bool:
        """
        LlamaFirewall 防火墙扫描
        :return: True=安全/可疑放行，False=高置信度攻击拒绝
        """
        result = self.firewall.scan(UserMessage(content=user_input))

        #print("[firewall]过滤器分析:")

        if result.decision == ScanDecision.BLOCK:
            if result.score > self.block_threshold:
                print(f"  [拒绝][小模型检测] 恶意输入，威胁分数: {result.score}")
                return False
            else:
                print(f"  [可疑][小模型检测] 威胁分数: {result.score}，记录但放行")
                return True

        if result.decision == ScanDecision.ALLOW and result.score < self.suspicious_threshold:
            print(f"  [放行][小模型检测] 威胁分数: {result.score}")

        return True
