import re
from agent.guardrail.RegexGuard import MultiPatternMatcher


class Cleaning:
    def __init__(self):
        self.sensitive_patterns = self._build_sensitive_patterns()
        #self.keyword_matcher = MultiPatternMatcher(self._build_sensitive_keywords())

    @staticmethod
    def _build_sensitive_patterns() -> list[dict]:
        return [
            {"name": "身份证号", "regex": re.compile(r'(?<!\d)\d{17}[\dXx](?!\d)')},
            {"name": "邮箱地址", "regex": re.compile(r'[\w.-]+@[\w.-]+\.\w{2,}')},
            {"name": "API_Key(sk-)", "regex": re.compile(r'sk-[a-zA-Z0-9]{20,}')},
            {"name": "AWS_Key", "regex": re.compile(r'AKIA[0-9A-Z]{16}')},
            {"name": "银行卡号", "regex": re.compile(r'(?<!\d)\d{16,19}(?!\d)')},
            {"name": "IP地址", "regex": re.compile(r'(?<!\d)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?!\d)')},
            {"name": "密码字段", "regex": re.compile(r'(?:password|passwd|pwd|密码)\s*[:=]\s*\S+', re.IGNORECASE)},
            {"name": "Bearer_Token", "regex": re.compile(r'Bearer\s+[a-zA-Z0-9_\-\.]+')},
            {"name": "私钥片段", "regex": re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----')},
            {"name": "手机号", "regex": re.compile(r'(?<!\d)1[3-9]\d{9}(?!\d)')},
        ]

    #容易误报不建议使用
    @staticmethod
    def _build_sensitive_keywords() -> list[str]:
        return [
            "数据库密码", "数据库连接串", "内部地址", "内网ip",
            "系统管理员", "root密码", "admin密码", "密钥是",
            "secret_key", "private_key", "api_secret",
        ]

    def scan(self, text: str) -> list[dict]:
        """
        扫描文本中的敏感信息
        :return: 命中的敏感信息列表 [{"type": "手机号", "value": "138xxxx1234"}, ...]
        """
        findings = []

        for pat in self.sensitive_patterns:
            matches = pat["regex"].findall(text)
            for m in matches:
                findings.append({"type": pat["name"], "value": m})

        #keyword_hits = self.keyword_matcher.match(text)
        #for kw in keyword_hits:
        #    findings.append({"type": "敏感关键词", "value": kw})

        return findings

    def is_safe(self, text: str) -> bool:
        """
        判断输出是否安全（不含敏感信息）
        """
        return len(self.scan(text)) == 0

    @staticmethod
    def _mask_value(match_str: str) -> str:
        """
        保留前后四位，中间替换为 *
        若长度不足 8 位，则仅保留首尾各一位，中间全部用 * 填充
        """
        n = len(match_str)
        if n <= 2:
            return match_str
        if n <= 8:
            return match_str[0] + '*' * (n - 2) + match_str[-1]
        return match_str[:3] + '*' * (n - 6) + match_str[-3:]

    def redact(self, text: str) -> str:
        """
        将敏感信息脱敏：保留前后四位，其余用 * 替代
        """
        result = text
        for pat in self.sensitive_patterns:
            result = pat["regex"].sub(
                lambda m, p=pat: self._mask_value(m.group(0)),
                result
            )
        return result
