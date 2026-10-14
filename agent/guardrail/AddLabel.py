'''
输入:context
输出:过滤context
此模块专门用于为用户输入添加限制标签
'''
class AddLabel:
    def __init__(self):
        pass
    def add_userInput_label(self,text):
        return "<userInput>"+text+"</userInput>"
    def add_system_label(self,text):
        return "<system>"+text+"</system>"