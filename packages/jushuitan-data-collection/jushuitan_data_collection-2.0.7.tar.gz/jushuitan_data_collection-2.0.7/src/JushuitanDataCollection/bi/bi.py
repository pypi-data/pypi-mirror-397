"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-07-14
Author: Martian Bugs
Description: 报表模块数据采集
"""

from BrowserAutomationLauncher import Browser

from .sales_theme_analysis import SalesThemeAnalysis
from .stock_analysis import StockAnalysis


class Bi:
    def __init__(self, browser: Browser):
        self._browser = browser

        self._sales_theme_analysis = None
        self._stock_analysis = None

    @property
    def sales_theme_analysis(self):
        """销售主题分析"""

        if self._sales_theme_analysis is None:
            self._sales_theme_analysis = SalesThemeAnalysis(self._browser)

        return self._sales_theme_analysis

    @property
    def stock_analysis(self):
        """商品库存分析"""

        if self._stock_analysis is None:
            self._stock_analysis = StockAnalysis(self._browser)

        return self._stock_analysis
