import ahocorasick
import re

from jinja2.nodes import Keyword

'''
输入:context
输出:过滤context
此模块专门用于删除混淆标签
'''

class MultiPatternMatcher:
    """基于 Aho-Corasick 的多词匹配器"""

    def __init__(self, keywords):
        """
        初始化匹配器
        :param keywords: 关键词列表，支持中英文
        """
        self.keywords = keywords
        self.automaton = ahocorasick.Automaton()

        # 添加关键词（支持中文）
        for idx, keyword in enumerate(keywords):
            # 统一转小写，实现大小写不敏感
            self.automaton.add_word(keyword.lower(), (idx, keyword))

        # 构建失败指针（核心步骤）
        self.automaton.make_automaton()

    def match(self, text):
        """
        匹配文本中的所有关键词
        :param text: 输入文本
        :return: 匹配到的关键词列表（去重后）
        """
        found = set()
        text_lower = text.lower()

        # 扫描文本（O(n) 时间复杂度）
        for end_index, (idx, keyword) in self.automaton.iter(text_lower):
            found.add(keyword)

        return list(found)

    def match_with_positions(self, text):
        """
        匹配关键词并返回位置
        :return: [(关键词, 起始位置, 结束位置), ...]
        """
        found = []
        text_lower = text.lower()

        for end_index, (idx, keyword) in self.automaton.iter(text_lower):
            start_index = end_index - len(keyword) + 1
            found.append((keyword, start_index, end_index))

        return found

    def is_dangerous(self, text, threshold=1):
        """
        判断文本是否危险（命中关键词数量超过阈值）
        """
        matches = self.match(text)
        return len(matches) >= threshold

    def remove_matches(self, text):
        """
        从文本中删除所有匹配到的关键词（大小写不敏感）
        :param text: 输入文本
        :return: 删除匹配词后的文本
        """
        positions = self.match_with_positions(text)
        if not positions:
            return text

        # 按起始位置降序排列，从后往前删除，避免索引偏移
        positions.sort(key=lambda x: x[1], reverse=True)
        result = text
        for keyword, start, end in positions:
            result = result[:start] + result[end + 1:]
        return result

    def remove_tags(self, text, tag_patterns=None):
        """
        删除文本中包含的指定标签及其内容（支持 XML/HTML 风格标签）
        :param text: 输入文本
        :param tag_patterns: 要删除的标签名列表，如 ['system', 'INST', 'assistant']
                             若为 None，则使用初始化时的 keywords 作为标签名
        :return: 删除标签及内容后的文本

        示例：
            text = "正常内容[system]恶意指令[/system]后续内容"
            remove_tags(text, ['system'])
            → "正常内容后续内容"
        """
        if tag_patterns is None:
            tag_patterns = list(self._keywords)

        result = text
        for tag in tag_patterns:
            # 匹配 <tag>...</tag> 或 [tag]...[/tag] 形式，支持跨行，大小写不敏感
            pattern = re.compile(
                r'[\[<]' + re.escape(tag) + r'[\]>].*?[\[<]/' + re.escape(tag) + r'[\]>]',
                re.DOTALL | re.IGNORECASE
            )
            result = pattern.sub('', result)
        return result
