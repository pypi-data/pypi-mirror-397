import json
import os

class I18nManager:
    def __init__(self, translations_file=None):
        self.translations = {}
        self.current_locale = 'zh'
        
        if translations_file:
            self.load_translations(translations_file)
        else:
            # 默认加载项目根目录下的translations.json
            default_path = os.path.join(os.getcwd(), 'translations.json')
            if os.path.exists(default_path):
                self.load_translations(default_path)
    
    def load_translations(self, file_path):
        """加载翻译文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"加载翻译文件失败: {str(e)}")
    
    def set_locale(self, locale):
        """设置当前语言"""
        if locale in self.translations:
            self.current_locale = locale
    
    def translate(self, text, locale=None):
        """翻译文本"""
        if not text:
            return text
        
        current_locale = locale or self.current_locale
        if current_locale in self.translations:
            return self.translations[current_locale].get(text, text)
        return text
    
    def get_locale(self):
        """获取当前语言"""
        return self.current_locale
    
    def get_supported_locales(self):
        """获取支持的语言列表"""
        return list(self.translations.keys())

# 创建全局i18n实例
i18n = I18nManager()
