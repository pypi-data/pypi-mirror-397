"""
Copyright (c) now Martian Bugs All rights reserved.
Build Date: 2025-12-08
Author: Martian Bugs
Description: 商品库存分析
"""

import json
from contextlib import suppress
from enum import StrEnum

from BrowserAutomationLauncher import Browser
from DrissionPage.errors import ElementNotFoundError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class Urls(StrEnum):
    main_page = 'https://bi.erp321.com/app/report/subject/stockanalysis/default.aspx?_c=jst-epaas&epaas=true'


class DataPacketUrls(StrEnum):
    stock_analysis = (
        'https://bi.erp321.com/app/report/subject/stockanalysis/showbysku.aspx'
    )


class StockAnalysis:
    PAGE_TITLE = '商品库存分析'

    def __init__(self, browser: Browser):
        self._browser = browser
        self._timeout = 15

    def _get__main_page(self):
        """
        获取标题为 [商品库存分析] 的页面
        """

        with suppress(Exception):
            page = self._browser.chromium.get_tab(title=self.PAGE_TITLE)
            return page

        page = self._browser.chromium.new_tab(url=Urls.main_page)
        return page

    @retry(
        retry=retry_if_exception_type((ElementNotFoundError, TimeoutError)),
        wait=wait_fixed(3),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def get_stock_by_goods(
        self, goods: list[str] | str, is_goods_name=False
    ) -> list[str] | None:
        """
        获取指定商品编码/商品名称的商品库存信息

        Args:
            goods: 商品编码/商品名称列表
            is_goods_name: 搜索条件是否为商品名称
        Returns:
            商品库存信息列表
        """

        page = self._get__main_page()
        search_btn = page.ele('c:input.btn_search', timeout=15)
        if not search_btn:
            raise ElementNotFoundError('未找到搜索按钮')

        reset_btn = page.ele('c:span.btn_search_reset', timeout=3)
        if reset_btn:
            reset_btn.click(by_js=True)

        if is_goods_name is not True:
            goods_code_input = page.ele('#sku_id_s', timeout=3)
            if not goods_code_input:
                raise ElementNotFoundError('未找到商品编码输入框')

            goods_codes = goods if isinstance(goods, list) else [goods]
            goods_code_input.input(','.join(goods_codes), clear=True)
        else:
            goods_name = goods if isinstance(goods, str) else goods[0]
            goods_name_input = page.ele('#name_s', timeout=3)
            if not goods_name_input:
                raise ElementNotFoundError('未找到商品名称输入框')
            goods_name_input.input(goods_name, clear=True)

        page_selector = page.ele('#pageSize', timeout=3)
        if not page_selector:
            raise ElementNotFoundError('未找到分页选择框')
        page_selector.select.by_value('500')

        page.listen.start(
            targets=DataPacketUrls.stock_analysis, method='POST', res_type='XHR'
        )
        search_btn.click(by_js=True)
        datapacket = page.listen.wait(timeout=60)
        response = datapacket.response.body

        if not isinstance(response, str):
            raise ValueError('返回的数据格式非预期的字符串')
        response = response[2:]

        try:
            response_jsonify: dict = json.loads(response)
            return_value: str = response_jsonify.get('ReturnValue')
            if not return_value or not isinstance(return_value, str):
                raise ValueError(
                    '响应体中未找到 ReturnValue 字段或字段类型非预期的 str'
                )
        except json.JSONDecodeError as err:
            raise ValueError('响应体数据转 JSON 失败') from err

        try:
            return_value_jsonify: dict = json.loads(return_value)
        except json.JSONDecodeError as err:
            raise ValueError('ReturnValue 字段数据转 JSON 失败') from err

        return return_value_jsonify.get('datas')
