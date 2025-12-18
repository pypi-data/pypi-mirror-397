# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  qlv-helper
# FileName:     out_ticket.py
# Description:  出票控制器
# Author:       ASUS
# CreateDate:   2025/12/17
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import inspect
from logging import Logger
from datetime import datetime
from typing import Callable, Any, cast, Dict
import qlv_helper.config.url_const as url_const
from qlv_helper.po.order_detail_page import OrderDetailPage
from playwright.async_api import Page, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from qlv_helper.controller.order_report_fill import order_locked, order_unlock, fill_procurement_info, fill_itinerary


async def open_order_detail_page(
        *, page: Page, logger: Logger, qlv_protocol: str, qlv_domain: str, order_id: int, timeout: float = 20.0
) -> None:
    url_prefix = f"{qlv_protocol}://{qlv_domain}"
    current_dtstr: str = datetime.now().strftime("%Y%m%d%H%M%S")
    order_detail_url_suffix = url_const.order_detail_url.format(order_id, current_dtstr)
    order_detail_url = url_prefix + order_detail_url_suffix
    await page.goto(order_detail_url)

    order_detail_po = OrderDetailPage(page=page, url=order_detail_url)
    await order_detail_po.url_wait_for(url=order_detail_url, timeout=timeout)
    logger.info(f"即将劲旅订单详情页面，页面URL<{order_detail_url}>")


async def order_out_ticket(
        *, page: Page, logger: Logger, qlv_protocol: str, qlv_domain: str, order_id: int, out_ticket_platform_type: str,
        out_ticket_platform: str, out_ticket_account: str, purchase_account_type: str, purchase_account: str,
        ceair_user_id: str, ceair_password: str, payment_id: str, platform_out_ticket_callback: Callable,
        timeout: float = 20.0, **kwargs: Any
) -> None:
    await open_order_detail_page(
        page=page, logger=logger, qlv_protocol=qlv_protocol, qlv_domain=qlv_domain, order_id=order_id, timeout=timeout
    )
    order_detail_po = cast(OrderDetailPage, page)
    try:
        await order_locked(logger=logger, page=order_detail_po, order_id=order_id, timeout=timeout)
        logger.info(f"订单<{order_id}>，阶段一：【锁单】已完成，")
    except (PlaywrightError, PlaywrightTimeoutError, RuntimeError, Exception) as e:
        logger.error(f"订单<{order_id}>，阶段一：【锁单】失败，原因：{e}")
        raise
    try:
        if inspect.iscoroutinefunction(platform_out_ticket_callback):
            platform_order_id, payment_amout = await platform_out_ticket_callback(logger=logger, **kwargs)
        else:
            platform_order_id, payment_amout = platform_out_ticket_callback(logger=logger, **kwargs)
        logger.info(f"订单<{order_id}>，阶段二：【预订、支付】已完成，")
    except (PlaywrightError, PlaywrightTimeoutError, RuntimeError, Exception) as e:
        logger.error(f"订单<{order_id}>，阶段二：【预订、支付】失败，原因：{e}")
        await order_unlock(logger=logger, page=order_detail_po, order_id=order_id, timeout=timeout, remark=str(e))
        logger.info(f"订单<{order_id}>，已完成解锁")
        raise

    try:
        await fill_procurement_info(
            logger=logger, page=order_detail_po, order_id=order_id, timeout=timeout,
            out_ticket_platform_type=out_ticket_platform_type, out_ticket_platform=out_ticket_platform,
            out_ticket_account=out_ticket_account, purchase_account_type=purchase_account_type,
            purchase_account=purchase_account, purchase_amount=payment_amout, ceair_user_id=ceair_user_id,
            ceair_password=ceair_password, payment_id=payment_id, platform_order_id=platform_order_id
        )
        logger.info(f"订单<{order_id}>，阶段三：【采购信息回填】")
    except (PlaywrightError, PlaywrightTimeoutError, RuntimeError, Exception) as e:
        logger.error(f"订单<{order_id}>，阶段三：【采购信息回填】失败，原因：{e}")
        raise


async def order_fill_itinerary(
        *, page: Page, logger: Logger, qlv_protocol: str, qlv_domain: str, order_id: int,
        passengers_itinerary: Dict[str, Any], timeout: float = 20.0, **kwargs: Any
) -> None:
    await open_order_detail_page(
        page=page, logger=logger, qlv_protocol=qlv_protocol, qlv_domain=qlv_domain, order_id=order_id, timeout=timeout
    )
    order_detail_po = cast(OrderDetailPage, page)
    await fill_itinerary(
        logger=logger, page=order_detail_po, order_id=order_id, timeout=timeout,
        passengers_itinerary=passengers_itinerary
    )
    logger.info(f"订单<{order_id}>，票号回填成功")
    await order_unlock(logger=logger, page=order_detail_po, order_id=order_id, timeout=timeout, remark="")
    logger.info(f"订单<{order_id}>，订单解锁成功")
