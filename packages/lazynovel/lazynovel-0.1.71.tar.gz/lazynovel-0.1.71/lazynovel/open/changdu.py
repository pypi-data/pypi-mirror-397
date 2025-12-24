#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker

开发文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb
"""
from lazysdk import lazyrequests
from lazysdk import lazytime
from lazysdk import lazymd5
import time
import json


def get_sign(
        distributor_id,  # 分销商标识
        secret_key,  # 签名密钥
        ts=None  # 时间戳
):
    """
    生成签名
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param ts: 时间戳
    """
    if ts is None:
        ts = int(time.time())
    param_str = str(distributor_id) + str(secret_key) + str(ts)
    return lazymd5.md5_str(content=param_str)


def get_charge(
        distributor_id,
        secret_key,
        begin=None,
        end=None,
        offset=None,
        limit=None,
        device_id=None,
        outside_trade_no=None,
        paid=None,
        optimizer_account=None,
        open_id=None,
        retry_limit=5
):
    """
    获取用户充值事件
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param begin: 数据查询开始时间点（unix 时间戳），默认为上一个小时开始时间点，最大支持获取3天内数据-订单创建时间
    :param end: 数据查询截止时间点（unix 时间戳），默认为当前小时的开始时间点，最大时间范围为1小时-订单创建时间
    :param offset: 分页模式使用，默认为0
    :param limit: 分页模式使用，默认100，最大值1000
    :param device_id: 用户设备id
    :param outside_trade_no: 第三方订单号
    :param paid: 是否支付成功
    :param optimizer_account: 优化师邮箱（不可使用主管账户邮箱请求）
    :param open_id: 用户微信open_id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/user/recharge/v1'
    if begin is not None:
        params['begin'] = begin
    if end is not None:
        params['end'] = end
    if offset is not None:
        params['offset'] = offset
    if limit is not None:
        params['limit'] = limit
    if device_id is not None:
        params['device_id'] = device_id
    if outside_trade_no is not None:
        params['outside_trade_no'] = outside_trade_no
    if paid is not None:
        params['paid'] = paid
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id

    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_user_read(
        distributor_id,
        secret_key,
        device_id=None,
        begin_time=None,
        end_time=None,
        page_size=None,
        page_index=None,
        optimizer_account=None,
        open_id=None,
        retry_limit=5
):
    """
    获取用户阅读进度
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param device_id: 用户ID
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :param page_size: 每页大小
    :param page_index: 页码，从0开始
    :param optimizer_account: 优化师邮箱
    :param open_id: 用户微信open_id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/user/read/list/v1/'
    if device_id is not None:
        params['device_id'] = device_id
    if begin_time is not None:
        params['begin_time'] = begin_time
    if end_time is not None:
        params['end_time'] = end_time
    if page_size is not None:
        params['page_size'] = page_size
    if page_index is not None:
        params['page_index'] = page_index
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_package_info(
        distributor_id,
        secret_key,
        retry_limit=5
):
    """
    获取可用快应用/公众号列表
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }

    url = 'https://www.changdunovel.com/novelsale/openapi/package_info/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_package_list(
        distributor_id,
        app_type,
        secret_key,
        page: int = 1,
        page_size: int = 50,
        retry_limit=5
):
    """
    2.25 获取账户下分包信息V2（快应用|微信H5|小程序）
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param retry_limit: 重试次数
    :param page: 页码
    :param page_size: 每页数量
    :param app_type: 应用业务类型。枚举值，提供该字段则只返回对应渠道分包列表
        - 快应用 = 1
        - 微信h5 = 3
        - 微信付费短剧 = 4
        - 抖小付费短剧 = 7
        - 抖小付费网文 = 8
        - 微信付费网文=12
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    params["page_index"] = page - 1
    params["page_size"] = page_size
    params["app_type"] = app_type

    url = 'https://www.changdunovel.com/novelsale/openapi/wx/get_package_list/v2/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_bound_package_list(
        distributor_id,
        app_type,
        app_id,
        secret_key,
        page: int = 1,
        page_size: int = 50,
        retry_limit=5
):
    """
    2.26 获取小程序绑定的渠道信息
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥
    :param retry_limit: 重试次数
    :param page: 页码
    :param page_size: 每页数量
    :param app_type: 应用业务类型。枚举值，提供该字段则只返回对应渠道分包列表
        - 快应用 = 1
        - 微信h5 = 3
        - 微信付费短剧 = 4
        - 抖小付费短剧 = 7
        - 抖小付费网文 = 8
        - 微信付费网文=12
    :param app_id: 查询的小程序appid，2.25获取
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    params["page_index"] = page - 1
    params["page_size"] = page_size
    params["app_type"] = app_type
    params["app_id"] = app_id

    url = 'https://www.changdunovel.com/novelsale/openapi/wx/get_bound_package_list/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_purchase(
        distributor_id,
        secret_key,
        book_id=None,
        promotion_id=None,
        device_id=None,
        begin=None,
        end=None,
        offset=None,
        limit=None,
        optimizer_account=None,
        open_id=None,
        retry_limit=5
):
    """
    获取用户消费记录
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书籍id
    :param promotion_id: 推广链id
    :param device_id: 用户设备id
    :param begin:
    :param end:
    :param offset:
    :param limit:
    :param optimizer_account: 优化师邮箱
    :param open_id: 微信open_id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if book_id is not None:
        params['book_id'] = book_id
    if promotion_id is not None:
        params['promotion_id'] = promotion_id
    if device_id is not None:
        params['device_id'] = device_id
    if begin is not None:
        params['begin'] = begin
    if end is not None:
        params['end'] = end
    if offset is not None:
        params['offset'] = offset
    if limit is not None:
        params['limit'] = limit
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if open_id is not None:
        params['open_id'] = open_id

    url = 'https://www.changdunovel.com/novelsale/openapi/user/purchase/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_user(
        distributor_id,
        secret_key,
        media_source=None,
        book_source=None,
        promotion_id=None,
        show_not_recharge=None,
        page_size=None,
        page_index=None,
        optimizer_account=None,
        begin_time: int = None,
        end_time: int = None,
        open_id=None,
        retry_limit=5
):
    """
    获取用户信息接口
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param media_source: 1 为字节/ 2为腾讯
    :param book_source: 书籍来源
    :param promotion_id: 推广链来源
    :param show_not_recharge: true 展示所有用户; false/不传 只展示充值用户
    :param page_size: 每页大小
    :param page_index: 页码，从0开始
    :param optimizer_account: 优化师邮箱
    :param begin_time: 开始时间（注册/染色时间）
    :param end_time: 结束时间（注册/染色时间）
    :param open_id: 用户微信open_id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if media_source is not None:
        params['media_source'] = media_source
    if book_source is not None:
        params['book_source'] = book_source
    if promotion_id is not None:
        params['promotion_id'] = promotion_id
    if show_not_recharge is not None:
        params['show_not_recharge'] = show_not_recharge
    if page_size is not None:
        params['page_size'] = page_size
    if page_index is not None:
        params['page_index'] = page_index
    if optimizer_account is not None:
        params['optimizer_account'] = optimizer_account
    if begin_time is not None:
        params['begin_time'] = begin_time
    if end_time is not None:
        params['end_time'] = end_time
    if open_id is not None:
        params['open_id'] = open_id

    url = 'https://www.changdunovel.com/novelsale/openapi/user/list/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_book_meta(
        distributor_id,
        secret_key,
        book_id=None,
        retry_limit=5
):
    """
    获取书籍信息 接口
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if book_id is not None:
        params['book_id'] = book_id

    url = 'https://www.changdunovel.com/novelsale/openapi/content/book_meta/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_promotion(
        distributor_id,
        secret_key,
        book_id=None,
        promotion_id=None,
        retry_limit=5,
        page: int = 1,
        page_size: int = 100,
        begin: int = None,
        end: int = None
):
    """
    获取 获取推广链接列表 接口 【不完整】
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    if book_id:
        params['book_id'] = book_id
    if promotion_id:
        params['promotion_id'] = promotion_id
    if not begin:
        begin = int(time.time()) - 86400
    params['begin'] = begin
    if not end:
        end = int(time.time())
    params['end'] = end

    params['offset'] = page_size * (page-1)
    params['limit'] = page_size

    url = 'https://www.changdunovel.com/novelsale/openapi/promotion/list/v1'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


def get_optimizer(
        distributor_id,
        secret_key,
        retry_limit=5,
        page: int = 1,
        page_size: int = 10,
        optimizer_account=None,
        optimizer_nickname=None
):
    """
    2.16 获取优化师信息
    参考文档：https://bytedance.feishu.cn/docx/doxcnoXWGp3qywnQYC8zVw069Bb
    :param distributor_id: 分销商标识
    :param secret_key: 签名密钥

    :param book_id: 书id
    :param retry_limit: 重试次数
    """
    sign = get_sign(
        distributor_id=distributor_id,
        secret_key=secret_key
    )
    params = {
        'distributor_id': distributor_id,
        'sign': sign,
        'ts': int(time.time())
    }
    params['page_index'] = page - 1
    params['page_size'] = page_size
    if optimizer_account:
        params['optimizer_account'] = optimizer_account
    if optimizer_nickname:
        params['optimizer_nickname'] = optimizer_nickname

    url = 'https://www.changdunovel.com/novelsale/openapi/optimizer_list/v1/'
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        return_json=True,
        retry_limit=retry_limit
    )


class OpenChangDu:
    """
    {'code': 411, 'message': 'sign invalid', 'promotion_id': ''}
    """
    def __init__(
            self,
            secret_key,
            distributor_id: int = None,  # 分销商标识
            host: str = "openapi.changdupingtai.com"
    ):
        """

        :param distributor_id: 分销商标识
        :param secret_key: 签名密钥
        """
        self.secret_key = secret_key
        self.distributor_id = distributor_id
        self.host = host

    def make_sign(
            self,
            distributor_id: int = None,
            data: dict = None,
            method: str = 'GET',
            ts=None  # 时间戳
    ):
        """
        1.2.1 签名字段加签逻辑升级
        文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-Xs7Jd0qsKoQQ5DxnyQzc7bLOn4Y
        :param distributor_id:
        :param data: 传入的数据
        :param method:
        :param ts: 时间戳
        """
        if ts is None:
            ts = int(time.time())

        if distributor_id:
            # 如果输入，就按照输入
            inner_distributor_id = distributor_id
        else:
            # 如果未输入
            if data.get('distributor_id'):
                # 如果数据中有，就使用数据中的
                inner_distributor_id = data['distributor_id']
            else:
                # 如果数据中没有，就用默认的
                inner_distributor_id = self.distributor_id

        data_sort = dict(sorted(data.items(), reverse=False))  # 对key进行排序
        if data and method.upper() == "GET":
            params_values = list()
            # 对value进行拼接
            for k, v in data_sort.items():
                params_values.append(str(v))
            params_value = "|".join(params_values)
            params_value += "|"
        elif data and method.upper() == "POST":
            params_value = json.dumps(data)
        else:
            return None

        param_str = str(inner_distributor_id) + str(self.secret_key) + str(ts) + str(params_value)
        # if distributor_id is not None:
        #     param_str = str(distributor_id) + str(self.secret_key) + str(ts) + str(params_value)
        # else:
        #     param_str = str(self.distributor_id) + str(self.secret_key) + str(ts) + str(params_value)
        return lazymd5.md5_str(content=param_str)

    def create_promotion(
            self,
            distributor_id: int,
            book_id: str,
            index: int,
            promotion_name: str = None,
            optimizer_account: str = None,
            ad_callback_config_id: int = None,
            recharge_template_id: int = None,
            media_source: int = None,
            start_chapter: int = None,
            price: int = None,
            pack_strategy_status: int = None,
            strategy_config: dict = None,
            customize_params: str = None,
            wx_video_id: str = None,
            wx_video_name: str = None,
            no_need_promotion_http_url: bool = None,
            custom_params: list = None,
            batch_num: int = None,

            retry_limit=5,
    ):
        """
        2.7 创建推广链接
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-JBmYdTdN5oWXH8xfnNRcDnA9nOb
        :param distributor_id:

        :param book_id: 书id
        :param index: 第几章开始生成推广链。
            - 快应用&H5可以生成（该书自定义起始付费章节减1和19）的最小值；
            - 短剧可以生成（该短剧自定义起始付费集数减1和9）的最小值；
        :param promotion_name: 推广链接名称
        :param optimizer_account: 优化师邮箱(仅快应用使用)
        :param ad_callback_config_id: 广告回传配置id；通过2.28获取id，H5不需要填写
        :param recharge_template_id: 推广链对应充值模版ID，通过2.15获取id
        :param media_source: 快应用：1 字节、2 腾讯、6 vivo，不填默认字节；H5：不需要填写
            短剧：1 字节、3 快手、 4 微信、10 视频号
        :param start_chapter: 仅短剧支持，和price一起。起始付费集数/章节（范围：2-100）；若短剧集数不到100则最大值为短剧最大集数, start_chapter 需要 > index
        :param price: 仅短剧支持，和start_chapter绑定（单位：分）（范围：10-500）
        :param pack_strategy_status: 起量助手开关，只对微信小程序有效，其他类型传值无效
            枚举值：
            0：关闭（默认）
            1：开启
        :param strategy_config: 策略开关配置
        :param customize_params: 推广链自定义追加参数，即推广链以&连接自定义参数，随用户买入下发
        :param wx_video_id: 视频ID（仅视频号场景，必填）
        :param wx_video_name: 视频名称（仅视频号场景）
        :param no_need_promotion_http_url: 是否需要创建http短链（仅微信小程序、抖音小程序）
            true：不创建http短链
            false：创建http短链
        :param custom_params: 根据创建推广链的部分请求参数，前置请求接口2.30，得到满足的自定义配置项。
        :param batch_num: 创建推广链，批量数量。有效范围[1,100]

        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/promotion/create/v1'
        method = 'POST'
        data = dict()
        data["distributor_id"] = distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        data['book_id'] = str(book_id)  # 必须
        data['index'] = index  # 必须

        if promotion_name is not None:
            data['promotion_name'] = promotion_name
        if optimizer_account is not None:
            data['optimizer_account'] = optimizer_account
        if ad_callback_config_id is not None:
            data['ad_callback_config_id'] = ad_callback_config_id
        if recharge_template_id is not None:
            data['recharge_template_id'] = recharge_template_id
        if media_source is not None:
            data['media_source'] = media_source
        if start_chapter is not None:
            data['start_chapter'] = start_chapter
        if price is not None:
            data['price'] = price
        if pack_strategy_status is not None:
            data['pack_strategy_status'] = pack_strategy_status
        if strategy_config is not None:
            data['strategy_config'] = strategy_config
        if customize_params is not None:
            data['customize_params'] = customize_params
        if wx_video_id is not None:
            data['wx_video_id'] = wx_video_id
        if wx_video_name is not None:
            data['wx_video_name'] = wx_video_name
        if no_need_promotion_http_url is not None:
            data['no_need_promotion_http_url'] = no_need_promotion_http_url
        if custom_params is not None:
            data['custom_params'] = custom_params
        if batch_num is not None:
            data['batch_num'] = batch_num

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(
            ts=ts,
            data=data,
            method=method,
            distributor_id=distributor_id
        )

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            json=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def promotion(
            self,
            book_id=None,
            promotion_id=None,
            begin: int = None,
            end: int = None,

            optimizer_account: str = None,
            optimizer_id: str = None,
            wx_video_id: str = None,

            page: int = 1,
            page_size: int = 100,
            retry_limit=5,
    ):
        """
        2.8 获取推广链接列表
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-TKGndtVYVoimsBxx1dRcD22yngf
        :param book_id: 书籍id
        :param promotion_id: 推广链id
        :param begin: 参考请求参数2.1，时间会转到为yyyy-mm-dd(天维度)
        :param end: 时间会转到为yyyy-mm-dd(天维度)
        :param optimizer_account: 优化师邮箱，仅快应用填写
        :param optimizer_id: 优化师 id，仅快应用填写
        :param wx_video_id: 视频ID（仅视频号场景填写）

        :param page: 页码
        :param page_size: 每页数量
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/promotion/list/v1'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if book_id:
            data['book_id'] = book_id
        if promotion_id:
            data['promotion_id'] = promotion_id
        if not begin:
            begin = int(time.time()) - 86400
        data['begin'] = begin
        if not end:
            end = int(time.time())
        data['end'] = end

        data['offset'] = page_size * (page - 1)
        data['limit'] = page_size

        if optimizer_account is not None:
            data['optimizer_account'] = optimizer_account
        if optimizer_id:
            data['optimizer_id'] = optimizer_id
        if wx_video_id is not None:
            data['wx_video_id'] = wx_video_id

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def book_meta(
            self,
            book_id=None,

            retry_limit=5
    ):
        """
        2.5 获取书籍信息
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-SAgYdXsldoxe4nxUyaCcC84rnOc

        :param book_id: 书籍id
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/content/book_meta/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if book_id is not None:
            data['book_id'] = book_id

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def recharge_template(
            self,
            begin_ts: int = None,
            end_ts: int = None,

            page: int = 1,
            page_size: int = 100,
            retry_limit=5,
    ):
        """
        2.15 获取充值模版信息
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-W2CQdMRGVo4zDQxWvUzcrhBBnKd

        :param begin_ts: 按照创建时间筛选，开始时间戳。时间会转到为yyyy-mm-dd(天维度)
        :param end_ts: 按照创建时间筛选，结束时间戳。时间会转到为yyyy-mm-dd(天维度)

        :param page: 页码，不允许超过1000
        :param page_size: 每页数量，不允许超过100
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/recharge_template/list/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if begin_ts is not None:
            data['begin_ts'] = begin_ts
        if end_ts is not None:
            data['end_ts'] = end_ts

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def get_activity(
            self,
            activity_id: int = None,
            name: str = None,
            distributor_id: int = None,

            page: int = 1,
            page_size: int = 50,
            retry_limit=5,
    ):
        """
        2.20 查询自定义充值活动（微信H5 & 快应用）
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-Lo89dlwH4oy9cqx9rfXc9LAhnWd

        :param activity_id: 充值活动标识
        :param name: 充值活动名称
        :param distributor_id: distributor_id

        :param page: 页码，从0开始
        :param page_size: 每页大小，最大为50条记录
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/distributor/get_activity/v1/'
        method = 'GET'
        data = dict()
        if distributor_id:
            data['distributor_id'] = distributor_id
        else:
            data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if activity_id is not None:
            data['activity_id'] = activity_id
        if name is not None:
            data['name'] = name

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(
            ts=ts,
            data=data,
            method=method
        )

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def wx_get_page_url(
            self,
            retry_limit=5
    ):
        """
        2.21 查询微信h5书城固定页面链接
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-X8fYdRE3WonJWcxvpiBc9Xo1nze

        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/wx/get_page_url/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def chapter_list(
            self,
            book_id,

            retry_limit=5
    ):
        """
        2.23 获取授权书本的章节列表（限前30章节）
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-LleTdaq2mobKyFxRY8ZcPRpynYd
        :param book_id: 查询的具体书本ID

        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/content/chapter_list/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if book_id is not None:
            data['book_id'] = book_id

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def wx_get_package_list(
            self,
            app_type,

            page: int = 1,
            page_size: int = 50,
            retry_limit=5,
    ):
        """
        2.25 获取账户下分包信息V2（快应用|微信H5|小程序）
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-LVB8dP87noSMavxmm3YcDUUmnnb
        :param app_type: 应用业务类型。枚举值，提供该字段则只返回对应渠道分包列表
            - 快应用 = 1
            - 微信h5 = 3
            - 微信付费短剧 = 4
            - 抖音小程序付费短剧 = 7
            - 抖音小程序付费网文 = 8
            - 微信付费网文=12

        :param page: 页码
        :param page_size: 每页数量
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/wx/get_package_list/v2/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if app_type is not None:
            data['app_type'] = app_type

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def wx_get_bound_package_list(
            self,
            app_id,

            page: int = 1,
            page_size: int = 50,
            retry_limit=5,
    ):
        """
        2.26 获取小程序绑定的渠道信息
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-DEEwdaNIOoZGL6xv0U9c821mnEc
        :param app_id: 查询的小程序appid，2.25获取

        :param page: 页码
        :param page_size: 每页数量
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/wx/get_bound_package_list/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if app_id is not None:
            data['app_id'] = app_id

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def book_list(
            self,
            query: str = None,
            creation_status: int = None,
            genre: int = None,
            permission_statuses: str = None,
            delivery_status: int = None,

            page: int = 1,
            page_size: int = 100,
            retry_limit=5,
    ):
        """
        2.34 小说列表
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-O6YrdX92RodMlmxwTtNcTxjMn0f

        :param query: 搜索内容，目前仅支持传入小说ID，传入其它内容将报错
        :param creation_status: 小说筛选条件，小说连载状态，0: 完结，1: 连载中
        :param genre: 小说筛选条件，0: 长篇体裁，8: 短篇体裁；
        :param permission_statuses: 小说筛选条件，针对当前分销商ID的授权类型筛选，可多选（比如: "permission_statuses": "3,4"）；
            2: 无授权；
            3: 独家授权；
            4: 普通授权；
        :param delivery_status: 小说筛选条件，小说投放状态筛选
            0: 不可投放；
            1: 可投放；
            2: 即将下架；

        :param page: 页码，不允许超过1000
        :param page_size: 每页数量，不允许超过100
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/content/book/list/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if query is not None:
            data['query'] = query
        if creation_status is not None:
            data['creation_status'] = creation_status
        if genre is not None:
            data['genre'] = genre
        if permission_statuses is not None:
            data['permission_statuses'] = permission_statuses
        if delivery_status is not None:
            data['delivery_status'] = delivery_status

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )

    def promotion_report(
            self,
            distributor_id: int = None,
            begin: str = None,
            end: str = None,
            book_id: int = None,
            promotion_id: int = None,
            wx_video_id: str = None,
            wx_video_name: str = None,
            channel: int = None,

            page: int = 1,
            page_size: int = 100,
            retry_limit=5,
    ):
        """
        2.35 推广链统计数据查询
        参考文档：https://bytedance.larkoffice.com/docx/doxcnoXWGp3qywnQYC8zVw069Bb#share-KTzVdeHVEojDTNxyQHdcdJGhn4e

        :param distributor_id: 分销商标识
        :param begin: 搜索开始日期
        :param end: 搜索结束日期，日期不传的话，默认近7天数据，最多只支持查180天的数据，注意begin和end之间天数不能超过180天
        :param book_id: 书籍 / 短剧 ID
        :param promotion_id: 推广链 ID
        :param wx_video_id: 视频 ID，视频号场景使用
        :param wx_video_name: 视频名称，视频号场景使用
        :param channel: 渠道类型，当使用视频号ID和视频名称搜索时，需要将channel设置为3，代表视频号场景

        :param page: 页码，不允许超过1000
        :param page_size: 每页数量，不允许超过100
        :param retry_limit: 重试次数
        """
        # --------------------- 签名固定搭配 ---------------------
        url = f'https://{self.host}/novelsale/openapi/promotion/statistic/v1/'
        method = 'GET'
        data = dict()
        data["distributor_id"] = self.distributor_id
        ts = int(time.time())
        # --------------------- 签名固定搭配 ---------------------

        if distributor_id:
            data['distributor_id'] = distributor_id
        if begin is not None:
            data['begin'] = begin
        if end is not None:
            data['end'] = end
        if book_id is not None:
            data['book_id'] = book_id
        if promotion_id is not None:
            data['promotion_id'] = promotion_id
        if wx_video_id is not None:
            data['wx_video_id'] = wx_video_id
        if wx_video_name is not None:
            data['wx_video_name'] = wx_video_name
        if channel is not None:
            data['channel'] = channel

        data['page_index'] = page - 1
        data['page_size'] = page_size

        # --------------------- 签名固定搭配 ---------------------
        sign = self.make_sign(ts=ts, data=data, method=method)

        headers = dict()
        headers["header-ts"] = str(ts)
        headers["header-sign"] = str(sign)
        # --------------------- 签名固定搭配 ---------------------

        return lazyrequests.lazy_requests(
            method=method,
            url=url,
            headers=headers,
            params=data,
            return_json=True,
            retry_limit=retry_limit
        )
