import pandas as pd
import math
import bisect

from rqdatac.validators import (
    ensure_date_or_today_int,
    ensure_list_of_string,
    ensure_date_int,
    check_quarter,
    quarter_string_to_date,
    check_items_in_container,
    ensure_date_range,
    ensure_order_book_ids,
)
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api, ttl_cache
from rqdatac.hk_decorators import support_hk_order_book_id
from rqdatac.services.financial import HK_FIELDS_LIST_EX
from rqdatac.services.calendar import get_trading_dates_in_type
from rqdatac.utils import int8_to_datetime
from rqdatac.services.basic import hk_all_unique_id_to_order_book_id


@export_as_api(namespace="hk")
@support_hk_order_book_id
def get_detailed_financial_items(
    order_book_ids,
    fields,
    start_quarter,
    end_quarter,
    date=None,
    statements="latest",
    market="hk",
):
    """
    查询财务细分项目(point-in-time 形式)

    Parameters
    ----------
    order_book_ids : str | list[str]
        合约代码，可传入 order_book_id 或 order_book_id list。
    fields : list[str]
        需要返回的财务字段。
    start_quarter : str
        财报回溯查询的起始报告期，例如 '2015q2' 代表 2015 年半年报。
    end_quarter : str
        财报回溯查询的截止报告期，例如 '2015q4' 代表 2015 年年报。
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，默认查询日期为当前最新日期。
    statements : str, optional
        基于查询日期，返回某一个报告期的所有记录或最新一条记录，statements 为 all 时返回所有记录，latest 时返回最新一条记录，默认为 latest。
    market : str, optional
        市场，仅限'hk'香港市场。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - quarter : str, 报告期
        - info_date : pandas.Timestamp, 公告发布日
        - field : list, 需要返回的财务字段
        - if_adjusted : int, 是否为非当期财报数据，0 代表当期，1 代表非当期
        - fiscal_year : pandas.Timestamp, 财政年度
        - standard : str, 会计准则
        - relationship : int, 运算符号，0 表示不参与计算，1 为正号，-1 为负号
        - subject : str, 细分项目名称（财报原字段名）
        - amount : float, 未做港币汇率转换的原始值
        - currency : str, 货币单位

    Examples
    --------
    获取 02318.XHKG 2023q1-2023q2 fields 下所有细分项目的最新一次记录

    >>> rqdatac.hk.get_detailed_financial_items(order_book_ids=['02318.XHKG'],start_quarter='2023q1', end_quarter='2023q2',fields=['other_operating_expense_items'],market='hk')
                         info_date fiscal_year                          field  relationship        amount currency     subject         standard  if_adjusted
    order_book_id quarter
    02318.XHKG    2023q1   2024-04-23    2023-12-31  other_operating_expense_items           1.0 -4.600000e+07      人民币元  提取保费准备金  非中国会计准则_保险公司            1
                  2023q1   2024-04-23    2023-12-31  other_operating_expense_items           1.0 -2.634700e+10      人民币元    银行业务利息支出  非中国会计准则_保险公司            1
                  2023q1   2024-04-23    2023-12-31  other_operating_expense_items           1.0 -1.894000e+09      人民币元  非保险业务手续费及佣金支出  非中国会计准则_保险公司            1
                  2023q2   2024-08-22    3-12-31  other_operating_expense_items           1.0 -1.440000e+08      人民币元  提取保费金  非中国会计准则_保险公司            1
                  2023q2   2024-08-22    2023-12-31  other_operating_expense_items           1.0 -5.329500e+10      人民币元    银务利息支出  非中国会计准则_保险公司            1
                  2023q2   2024-08-22    2023-12-31  other_operating_expense_items           1.0 -4.368000e+09      人民币元  非保险业务手续费及佣金支出  非中国会计准则_保险公司            1
    """
    order_book_ids = ensure_list_of_string(order_book_ids, "order_book_ids")
    check_quarter(start_quarter, "start_quarter")
    start_quarter_int = ensure_date_int(quarter_string_to_date(start_quarter))
    check_quarter(end_quarter, "end_quarter")
    end_quarter_int = ensure_date_int(quarter_string_to_date(end_quarter))
    if start_quarter > end_quarter:
        raise ValueError(
            "invalid quarter range: [{!r}, {!r}]".format(start_quarter, end_quarter)
        )
    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, HK_FIELDS_LIST_EX, "fields")
    if statements not in ["all", "latest"]:
        raise ValueError("invalid statements , got {!r}".format(statements))
    date = ensure_date_or_today_int(date)
    result = get_client().execute(
        "hk.get_detailed_financial_items",
        order_book_ids,
        fields,
        start_quarter_int,
        end_quarter_int,
        date,
        statements,
    )
    if not result:
        return None
    df = pd.DataFrame.from_records(result)
    df["end_date"] = df["end_date"].apply(
        lambda d: "{}q{}".format(d.year, math.ceil(d.month / 3))
    )
    df.sort_values(["order_book_id", "end_date", "info_date"], inplace=True)
    df.rename(columns={"end_date": "quarter"}, inplace=True)
    df.set_index(["order_book_id", "quarter"], inplace=True)
    return df


@export_as_api(namespace="hk")
def get_southbound_eligible_secs(
    trading_type="sh",
    date=None,
    start_date=None,
    end_date=None,
    market="hk"
):
    """
    获取港股通成分股数据

    Parameters
    ----------
    trading_type : str
        支持填写 'sh': 港股通（沪），'sz': 港股通（深）。
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，默认为最新记录日期。
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        指定开始日期，不能和 date 同时指定。
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        指定结束日期，需与 start_date 同时指定且不小于开始日期。
    market : str, optional
        市场，仅限'hk'香港市场。

    Returns
    -------
    list[str] | dict[datetime.datetime, list[str]]
        某一天港股通成分股的 order_book_id 列表或某时间区间内的日期与 order_book_id 列表的对应关系。

    Examples
    --------
    指定 date 获取某一天的 sh 港股通成分股数据

    >>> rqdatac.hk.get_southbound_eligible_secs(trading_type='sh', date=20250929)
    ['00001.XHKG',
     '00002.XHKG',
     '00003.XHKG',
     '00004.XHKG',
     '00005.XHKG',
     ...
     '01929.XHKG']

    获取某段时间的 sz 港股通成分股数据

    >>> rqdatac.hk.get_southbound_eligible_secs(trading_type='sz', start_date=20250925, end_date=20250929)
    [{datetime.datetime(2025, 9, 25, 0, 0): ['00001.XHKG',
      '00002.XHKG',
      ...,
      '01929.XHKG'],
      datetime.datetime(2025, 9, 29, 0, 0): ['00001.XHKG',
      '00002.XHKG',
      ...,
      '01929.XHKG']}]
    """
    if date and (start_date or end_date):
        raise ValueError("date cannot be input together with start_date or end_date")
    elif (start_date and not end_date) or (end_date and not start_date):
        raise ValueError("start_date and end_date need to be applied together")

    unique_id_to_order_book_id = hk_all_unique_id_to_order_book_id()

    if start_date:
        start_date, end_date = ensure_date_range(start_date, end_date)
        trading_dates = get_trading_dates_in_type(start_date, end_date, expect_type="int", market="hk")
        if not trading_dates:
            return
        data = get_client().execute(
            "hk.get_southbound_eligible_secs", trading_type, start_date, end_date
        )
        data = {d['date']: [unique_id_to_order_book_id.get(item, item) for item in d['southbound_eligible_secs']] for d in data}
        dates = sorted(data.keys())
        date0 = dates[0]
        result = {}
        for trading_date in trading_dates:
            if trading_date < date0:
                continue
            position = bisect.bisect_right(dates, trading_date) - 1
            result[int8_to_datetime(trading_date)] = data[dates[position]]
        return result
    else:
        date = ensure_date_or_today_int(date)
        data = get_client().execute(
            "hk.get_southbound_eligible_secs", trading_type, date, date
        )
        if not data:
            return None
        return [unique_id_to_order_book_id.get(item, item) for item in data[0]["southbound_eligible_secs"]]


ANNOUNCEMENT_FIELDS = ["media", "first_category", "second_category", "third_category",
                       "title", "language", "file_type", "announcement_link"]


@ttl_cache(12 * 3600)
def _get_announcement_category_dict():
    category = get_client().execute("hk.get_announcement_category")
    return {r['type_code']: r['type_eng_name'] for r in category}


@export_as_api(namespace="hk")
@support_hk_order_book_id
def get_announcement(order_book_ids, start_date=None, end_date=None, fields=None, market="hk"):
    """
    获取港股公司公告数据，包括标题及正文链接

    Parameters
    ----------
    order_book_ids: str | list[str]
        股票合约代码，如 '00001_01.XHKG' 或 ['00001_01.XHKG', '00002_01.XHKG']
    start_date: str | int | datetime.datetime | None
        开始日期，如 '2017-01-01' 或 20170101 或 datetime.datetime(2017, 1, 1)
    end_date: str | int | datetime.datetime | None
        结束日期，如 '2017-01-01' 或 20170101 或 datetime.datetime(2017, 1, 1)
    fields: list[str] | None
        需要返回的字段，默认返回所有字段
    market: str
        市场代码，默认为 'hk'

    Returns
    -------
    pandas.DataFrame
        以 MultiIndex(order_book_id, info_date) 为行索引的公告数据表，默认返回包含以下字段：
        - order_book_id: 股票合约代码
        - info_date: 公告日期
        - media: 媒体名称
        - first_category: 一级分类
        - second_category: 二级分类
        - third_category: 三级分类
        - title: 公告标题
        - language: 语言
        - file_type: 文件类型
        - announcement_link: 公告链接
        - rice_create_tm: 米筐入库时间
    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market="hk")
    start_date, end_date = ensure_date_range(start_date, end_date)
    if fields is not None:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, ANNOUNCEMENT_FIELDS, "fields")
    else:
        fields = ANNOUNCEMENT_FIELDS
    data = get_client().execute("hk.get_announcement", order_book_ids, start_date, end_date, fields)
    if not data:
        return None
    df = pd.DataFrame(data)
    for col in ['first_category', 'second_category', 'third_category']:
        df[col] = df[col].map(_get_announcement_category_dict())
    df['rice_create_tm'] = pd.to_datetime(df['rice_create_tm'] + 3600 * 8, unit="s")
    df.set_index(["order_book_id", "info_date"], inplace=True)
    df.sort_index(inplace=True)
    return df
