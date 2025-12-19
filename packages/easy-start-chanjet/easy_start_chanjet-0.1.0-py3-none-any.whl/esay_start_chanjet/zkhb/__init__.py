#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Optional, Iterable, Union

import arrow
import httpx
import xmltodict
from bs4 import BeautifulSoup
from pydantic_xml import BaseXmlModel, element


def validate_payment_date_range(
        daily_fee: Union[int, float] = 0,
        total_amount: Union[int, float] = 0,
        start_date: str = "",
        end_date: str = ""
):
    """
    验证支付日期范围是否合法
    :param daily_fee: 每日费用
    :param total_amount: 总金额
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 是否合法
    """
    daily_fee = float(daily_fee)
    total_amount = float(total_amount)
    start_date_arrow: arrow.Arrow = arrow.get(start_date)
    end_date_arrow: arrow.Arrow = arrow.get(end_date)
    total_days = sum(1 for i in start_date_arrow.interval(frame="days", start=start_date, end=end_date_arrow))
    return total_amount >= (daily_fee * total_days)


class SoapGetDataSet(BaseXmlModel, tag="GetDataSet", nsmap={"": "http://zkhb.com.cn/"}):
    sql: str = element()
    url: Optional[str] = element(default=None)


class SoapBody(BaseXmlModel, tag="Body"):
    node: Optional[SoapGetDataSet] = element(default=None)


class SoapEnvelope(
    BaseXmlModel,
    tag="Envelope",
    ns="soap",
    nsmap={
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsd": "http://www.w3.org/2001/XMLSchema",
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    }
):
    node: Optional[SoapBody] = element(default=None)


class WebService:
    def __init__(self, base_url: str = ""):
        """
        初始化WebService
        :param base_url: 基础URL
        """
        self.base_url: str = base_url[:-1] if base_url.endswith("/") else base_url

    def client(self, **kwargs):
        """
        创建同步HTTP客户端
        :param kwargs: 其他参数
        :return: 同步HTTP客户端
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("base_url", self.base_url)
        kwargs.setdefault("timeout", 120)
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("base_url", self.base_url)
        kwargs.setdefault("timeout", 120)
        return httpx.AsyncClient(**kwargs)

    def get_data_set(self, soap_envelope: SoapEnvelope, client: httpx.Client = None, **kwargs):
        """
        调用GetDataSet接口
        :param soap_envelope: SOAP请求体
        :param client: HTTP客户端
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("url", f"{self.base_url}/estate/webService/ForcelandEstateService.asmx")
        params = kwargs.get("params", dict())
        params.setdefault("op", "GetDataSet")
        kwargs["params"] = params
        headers = kwargs.get("headers", dict())
        headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        kwargs["headers"] = headers
        kwargs["data"] = soap_envelope.to_xml(encoding='utf-8').decode("utf-8")
        response: httpx.Response = None
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        xml_doc = BeautifulSoup(response.text, features="xml")
        data_set_dict = xmltodict.parse(xml_doc.find("NewDataSet").encode("utf-8"), encoding="utf-8")
        data_set_dict = data_set_dict if isinstance(data_set_dict, dict) else dict()
        results = data_set_dict.get("NewDataSet", dict()).get("Table")
        if isinstance(results, list):
            results = [results]
        return results, xml_doc, results

    async def async_get_data_set(self, soap_envelope: SoapEnvelope, client: httpx.AsyncClient = None, **kwargs):
        """
        调用GetDataSet接口（异步）
        :param soap_envelope: SOAP请求体
        :param client: HTTP客户端
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("url", f"{self.base_url}/estate/webService/ForcelandEstateService.asmx")
        params = kwargs.get("params", dict())
        params.setdefault("op", "GetDataSet")
        kwargs["params"] = params
        headers = kwargs.get("headers", dict())
        headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        kwargs["headers"] = headers
        kwargs["data"] = soap_envelope.to_xml(encoding='utf-8').decode("utf-8")
        response: httpx.Response = None
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        xml_doc = BeautifulSoup(response.text, features="xml")
        data_set_dict = xmltodict.parse(xml_doc.find("NewDataSet").encode("utf-8"), encoding="utf-8")
        data_set_dict = data_set_dict if isinstance(data_set_dict, dict) else dict()
        results = data_set_dict.get("NewDataSet", dict()).get("Table")
        if not isinstance(results, list):
            results = [results]
        return results, xml_doc, results

    def get_actual_payment_item_list(self, client: httpx.Client = None, column_str: str = "", condition_str: str = "",
                                     order_by_str: str = "order by cfi.ChargeFeeItemID", **kwargs):
        """
        查询实际支付项目列表
        :param client: HTTP客户端
        :param column_str: 列字符串
        :param condition_str: 条件字符串
        :param order_by_str: 排序字符串
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("url", f"{self.base_url}/estate/webService/ForcelandEstateService.asmx")
        params = kwargs.get("params", dict())
        params.setdefault("op", "GetDataSet")
        kwargs["params"] = params
        headers = kwargs.get("headers", dict())
        headers.setdefault("Content-Type", "text/xml; charset=utf-8")
        kwargs["headers"] = headers
        sql = f"select {column_str} {','.join([
            'cml.ChargeMListID',
            'cml.ChargeMListNo',
            'cml.ChargeTime',
            'cml.PayerName',
            'cml.ChargePersonName',
            'cml.ActualPayMoney',
            'cml.EstateID',
            'cml.ItemNames',
            'ed.Caption as EstateName',
            'cfi.ChargeFeeItemID',
            'cfi.ActualAmount',
            'cfi.SDate',
            'cfi.EDate',
            'cfi.RmId',
            'rd.RmNo',
            'cml.CreateTime',
            'cml.LastUpdateTime',
            'cbi.ItemName',
            'cbi.IsPayFull',
        ])} {''.join([
            ' from chargeMasterList as cml',
            ' left join EstateDetail as ed on cml.EstateID=ed.EstateID',
            ' left join ChargeFeeItem as cfi on cml.ChargeMListID=cfi.ChargeMListID',
            ' left join RoomDetail as rd on cfi.RmId=rd.RmId',
            ' left join ChargeBillItem as cbi on cfi.CBillItemID=cbi.CBillItemID',
        ])} where 1=1 {condition_str} {order_by_str};";
        kwargs["data"] = SoapEnvelope(node=SoapBody(node=SoapGetDataSet(sql=sql))).to_xml(encoding='utf-8').decode(
            "utf-8")
        response: httpx.Response = None
        if not isinstance(client, httpx.AsyncClient):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        xml_doc = BeautifulSoup(response.text, features="xml")
        data_set_dict = xmltodict.parse(xml_doc.find("NewDataSet").encode("utf-8"), encoding="utf-8")
        data_set_dict = data_set_dict if isinstance(data_set_dict, dict) else dict()
        results = data_set_dict.get("NewDataSet", dict()).get("Table")
        if not isinstance(results, list):
            results = [results]
        return results, xml_doc, results

    async def async_get_actual_payment_item_list(self, client: httpx.AsyncClient = None, column_str: str = "",
                                                 condition_str: str = "",
                                                 order_by_str: str = "order by cfi.ChargeFeeItemID", **kwargs):
        """
        查询实际支付项目列表（异步）
        :param client: HTTP客户端
        :param column_str: 列字符串
        :param condition_str: 条件字符串
        :param order_by_str: 排序字符串
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "GET")
        kwargs.setdefault("url", f"{self.base_url}/estate/WebSerVice/jsonPostInterfaceNew.ashx")
        params = kwargs.get("params", dict())
        params.setdefault("json", "Getpayment")
        params.setdefault("type", "B")
        kwargs["params"] = params
        response: httpx.Response = None
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        response_json = response.json() if response.text else dict()
        return response_json.get("result", "false").lower() == "true", response_json.get("Getpayment", list()), response


class Http:
    def __init__(self, base_url: str = ""):
        """
        初始化HTTP客户端
        :param base_url: 基础URL
        """
        self.base_url: str = base_url[:-1] if base_url.endswith("/") else base_url

    def client(self, **kwargs):
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("base_url", self.base_url)
        kwargs.setdefault("timeout", 120)
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("base_url", self.base_url)
        kwargs.setdefault("timeout", 120)
        return httpx.AsyncClient(**kwargs)

    def get_actual_payment_item_list(self, client: httpx.Client = None, **kwargs):
        """
        查询实际支付项目列表
        :param client: HTTP客户端
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "GET")
        kwargs.setdefault("url", f"{self.base_url}/estate/WebSerVice/jsonPostInterfaceNew.ashx")
        params = kwargs.get("params", dict())
        params.setdefault("json", "Getpayment")
        kwargs["params"] = params
        response: httpx.Response = None
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        response_json = response.json() if response.text else dict()
        return response_json.get("result", "false").lower() == "true", response_json.get("Getpayment", list()), response

    async def async_get_actual_payment_item_list(self, client: httpx.AsyncClient = None, **kwargs):
        """
        查询实际支付项目列表（异步）
        :param client: HTTP客户端
        :param kwargs: 其他参数
        :return: 结果
        """
        kwargs = kwargs if kwargs else dict()
        kwargs.setdefault("method", "GET")
        kwargs.setdefault("url", f"{self.base_url}/estate/WebSerVice/jsonPostInterfaceNew.ashx")
        params = kwargs.get("params", dict())
        params.setdefault("json", "Getpayment")
        params.setdefault("type", "B")
        kwargs["params"] = params
        response: httpx.Response = None
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        response_json = response.json() if response.text else dict()
        return response_json.get("result", "false").lower() == "true", response_json.get("Getpayment", list()), response
