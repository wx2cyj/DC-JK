import time
import logging
import requests
from typing import List, Dict
from config import Config
from currency import CurrencyConverter
from flavor_classifier import translate_cut
from tobacco_alias import get_brand_chinese, get_tobacco_chinese_alias

logger = logging.getLogger("Notifier")

class WeComNotifier:
    _access_token = None
    _token_expires_at = 0

    @classmethod
    def _get_app_access_token(cls) -> str:
        """获取企业微信自建应用 access_token"""
        now = time.time()
        if cls._access_token and now < cls._token_expires_at - 120:
            return cls._access_token

        url = f"{Config.WECOM_PROXY_URL}/cgi-bin/gettoken"
        params = {
            "corpid": Config.WECOM_CORP_ID,
            "corpsecret": Config.WECOM_CORP_SECRET
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if data.get("errcode") == 0:
                cls._access_token = data.get("access_token")
                cls._token_expires_at = now + data.get("expires_in", 7200)
                logger.info("企业微信应用 Access Token 获取成功")
                return cls._access_token
            else:
                logger.error(f"获取企微 Token 失败: {data}")
        except Exception as e:
            logger.error(f"请求企微 Token 异常: {e}")
        return ""

    @classmethod
    def send_wecom_app_text(cls, content: str) -> bool:
        """通过企业微信自建应用发送 Text 消息 (完美兼容电脑微信与手机微信)"""
        token = cls._get_app_access_token()
        if not token:
            return False

        url = f"{Config.WECOM_PROXY_URL}/cgi-bin/message/send?access_token={token}"
        payload = {
            "touser": Config.WECOM_TO_USER,
            "msgtype": "text",
            "agentid": Config.WECOM_AGENT_ID,
            "text": {
                "content": content
            },
            "enable_duplicate_check": 0
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            data = r.json()
            if data.get("errcode") == 0:
                logger.info("企业微信自建应用消息推送成功！")
                return True
            else:
                logger.error(f"企业微信应用消息推送失败: {data}")
        except Exception as e:
            logger.error(f"推送异常: {e}")
        return False

    @classmethod
    def send_wecom_webhook_markdown(cls, content: str) -> bool:
        """通过企业微信群机器人 Webhook 发送 Markdown 消息"""
        if not Config.WECOM_WEBHOOK_URL:
            return False
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            r = requests.post(Config.WECOM_WEBHOOK_URL, json=payload, timeout=10)
            data = r.json()
            if data.get("errcode") == 0:
                logger.info("企业微信群机器人消息推送成功！")
                return True
            else:
                logger.error(f"企业微信群机器人推送失败: {data}")
        except Exception as e:
            logger.error(f"机器人推送异常: {e}")
        return False

    @classmethod
    def send_pushplus(cls, title: str, content: str) -> bool:
        """通过 PushPlus 发送个人微信推送"""
        if not Config.PUSHPLUS_TOKEN:
            return False
        try:
            payload = {
                "token": Config.PUSHPLUS_TOKEN,
                "title": title,
                "content": content,
                "template": "markdown"
            }
            r = requests.post("https://www.pushplus.plus/send", json=payload, timeout=10)
            data = r.json()
            if data.get("code") == 200:
                logger.info("PushPlus 微信推送成功！")
                return True
            else:
                logger.error(f"PushPlus 推送失败: {data}")
        except Exception as e:
            logger.error(f"PushPlus 推送异常: {e}")
        return False

    @classmethod
    def dispatch_notification(cls, title: str, text_content: str, markdown_content: str):
        """统一分发通知到已配置的所有渠道"""
        sent = False
        # 1. 企微自建应用 (使用 text 消息类型，确保电脑端和手机端微信均能完美显示)
        if Config.WECOM_CORP_ID and Config.WECOM_CORP_SECRET:
            sent = cls.send_wecom_app_text(text_content) or sent

        # 2. 企微群机器人 (支持 markdown)
        if Config.WECOM_WEBHOOK_URL:
            sent = cls.send_wecom_webhook_markdown(markdown_content) or sent

        # 3. PushPlus (支持 markdown)
        if Config.PUSHPLUS_TOKEN:
            sent = cls.send_pushplus(title, markdown_content) or sent

        if not sent:
            logger.info("【本地预览】未配置或未成功发送通知，消息内容预览如下:")
            print("\n" + "="*50)
            print(f"【{title}】")
            print(text_content)
            print("="*50 + "\n")


def build_card_text_formatted(item: Dict) -> str:
    """格式化单款斗草的文本内容（兼容所有端）"""
    title = item.get("title", "未知品名")
    brand = item.get("brand", "SP")
    brand_cn = get_brand_chinese(brand)
    alias = get_tobacco_chinese_alias(title, brand)

    flavor = item.get("flavor_category", "综合调配")
    flavor_desc = item.get("flavor_desc", "")

    cut = item.get("cut_cn")
    if not cut or cut == "未知裁切":
        cut = translate_cut(item.get("cut", ""), title)

    sale_usd = float(item.get("sale_price_usd", 0.0) or 0.0)
    reg_usd = float(item.get("regular_price_usd", 0.0) or 0.0)

    # 动态补齐人民币汇率换算，避免为 ¥0.00
    sale_cny = item.get("sale_price_cny")
    if sale_cny is None or (sale_cny == 0.0 and sale_usd > 0):
        sale_cny = CurrencyConverter.to_cny(sale_usd)

    in_stock = item.get("is_in_stock", True)
    url = item.get("url", "https://www.smokingpipes.com")
    discount_msg = item.get("discount_msg", "")

    discount_ratio = round((sale_usd / reg_usd) * 10, 1) if reg_usd > 0 and sale_usd > 0 else 0
    discount_str = f" ({discount_ratio}折)" if discount_ratio > 0 and discount_ratio < 10 else ""
    stock_str = "✅ 现货在售" if in_stock else "⚠️ 暂时缺货"

    brand_header = brand_cn if brand_cn else brand
    lines = [f"【{brand_header}】{title}"]
    if alias:
        lines.append(f"• 圈内俗称: 🏷️ {alias}")

    lines.append(f"• 口味类型: {flavor}")
    if flavor_desc:
        lines.append(f"• 风味特点: {flavor_desc}")
    if cut:
        lines.append(f"• 裁切规格: {cut}")

    if sale_usd > 0:
        lines.append(f"• 特价价格: ${sale_usd:.2f} (原价 ${reg_usd:.2f}{discount_str})")
        lines.append(f"• 折合RMB: ¥{sale_cny:.2f}")
    else:
        if reg_usd > 0:
            lines.append(f"• 原价参考: ${reg_usd:.2f} (缺货待补)")
        else:
            lines.append(f"• 价格状态: 缺货暂未标价")

    lines.append(f"• 库存状态: {stock_str}")
    if discount_msg:
        lines.append(f"• 活动信息: {discount_msg}")

    lines.append(f"• 直达购买: <a href=\"{url}\">点击前往SP购买</a>\n")
    return "\n".join(lines)


def build_card_markdown_formatted(item: Dict) -> str:
    """格式化单款斗草的 Markdown 内容（供机器人与网页使用）"""
    title = item.get("title", "未知品名")
    brand = item.get("brand", "SP")
    brand_cn = get_brand_chinese(brand)
    alias = get_tobacco_chinese_alias(title, brand)

    flavor = item.get("flavor_category", "综合调配")
    flavor_desc = item.get("flavor_desc", "")

    cut = item.get("cut_cn")
    if not cut or cut == "未知裁切":
        cut = translate_cut(item.get("cut", ""), title)

    sale_usd = float(item.get("sale_price_usd", 0.0) or 0.0)
    reg_usd = float(item.get("regular_price_usd", 0.0) or 0.0)

    # 动态补齐人民币汇率换算，避免为 ¥0.00
    sale_cny = item.get("sale_price_cny")
    if sale_cny is None or (sale_cny == 0.0 and sale_usd > 0):
        sale_cny = CurrencyConverter.to_cny(sale_usd)

    in_stock = item.get("is_in_stock", True)
    url = item.get("url", "https://www.smokingpipes.com")
    discount_msg = item.get("discount_msg", "")

    discount_ratio = round((sale_usd / reg_usd) * 10, 1) if reg_usd > 0 and sale_usd > 0 else 0
    discount_str = f" ({discount_ratio}折)" if discount_ratio > 0 and discount_ratio < 10 else ""
    stock_badge = '<font color="info">✅ 现货在售</font>' if in_stock else '<font color="comment">⚠️ 暂时缺货</font>'

    brand_header = brand_cn if brand_cn else brand
    lines = [f"### [{brand_header}] {title}"]
    if alias:
        lines.append(f"> **圈内俗称**: 🏷️ **{alias}**")

    lines.append(f"> **口味类型**: {flavor}")
    if flavor_desc:
        lines.append(f"> **风味特点**: <font color=\"comment\">{flavor_desc}</font>")
    if cut:
        lines.append(f"> **裁切规格**: {cut}")

    if sale_usd > 0:
        lines.append(f"> **特价价格**: **${sale_usd:.2f}** (原价 ${reg_usd:.2f}{discount_str})")
        lines.append(f"> **折合RMB**: <font color=\"warning\">**¥{sale_cny:.2f}**</font>")
    else:
        if reg_usd > 0:
            lines.append(f"> **原价参考**: ${reg_usd:.2f} (缺货待补)")
        else:
            lines.append(f"> **价格状态**: 缺货暂未标价")

    lines.append(f"> **库存状态**: {stock_badge}")
    if discount_msg:
        lines.append(f"> **活动信息**: {discount_msg}")

    lines.append(f"> [👉 点击前往SP站直达购买]({url})\n")
    return "\n".join(lines)


def chunk_items_by_bytes(items: List[Dict], max_bytes: int = 1800) -> List[List[Dict]]:
    """按企业微信 2048 字节限制智能动态分批，确保任何客户端绝不截断"""
    batches = []
    current_batch = []
    # 预留表头和标题字符约 350 字节
    current_bytes = 350

    for item in items:
        card_text = build_card_text_formatted(item)
        card_b = len(card_text.encode("utf-8"))

        if current_batch and (current_bytes + card_b > max_bytes):
            batches.append(current_batch)
            current_batch = [item]
            current_bytes = 350 + card_b
        else:
            current_batch.append(item)
            current_bytes += card_b

    if current_batch:
        batches.append(current_batch)

    return batches


def notify_new_specials(items: List[Dict]):
    """推送新上架特价斗草（智能动态分批，彻底杜绝单条超过2048字节被截断）"""
    if not items:
        return

    rate_desc = ""
    if items and items[0].get("rate_desc"):
        rate_desc = items[0]["rate_desc"]
    if not rate_desc:
        rate_desc = CurrencyConverter.get_source_desc()

    total_count = len(items)
    title = f"🔥 SP站特价上新：发现 {total_count} 款特价斗草！"

    # 按现货在前排序
    sorted_items = sorted(items, key=lambda x: (not x.get("is_in_stock", False), x.get("brand", "")))

    # 智能字节级分批 (单条限 1800 字节，远低于企微 2048 字节阈值)
    batches = chunk_items_by_bytes(sorted_items, max_bytes=1800)

    for idx, batch in enumerate(batches):
        batch_num_str = f" (第 {idx+1}/{len(batches)} 批)" if len(batches) > 1 else ""

        # 1. 文本版本（电脑+手机微信全兼容）
        text_lines = [
            f"🔥【SP站特价上新通知】{batch_num_str}",
            f"更新数量: 发现 {total_count} 款特价草 (本批 {len(batch)} 款)",
            f"汇率基准: {rate_desc}",
            f"特价专区: <a href=\"https://www.smokingpipes.com/specials.cfm?specials=pipe-tobaccos\">点击查看SP特价专区</a>",
            "----------------------------------------"
        ]
        for it in batch:
            text_lines.append(build_card_text_formatted(it))
        text_content = "\n".join(text_lines)

        # 2. Markdown 版本
        md_lines = [
            f"## 🔥 SP站特价上新通知{batch_num_str}",
            f"> **更新数量**: 发现 **{total_count}** 款特价草 (本批 {len(batch)} 款)",
            f"> **汇率基准**: {rate_desc}",
            f"> **监控主页**: [点击查看SP特价专区](https://www.smokingpipes.com/specials.cfm?specials=pipe-tobaccos)\n",
            "---"
        ]
        for it in batch:
            md_lines.append(build_card_markdown_formatted(it))
        md_content = "\n".join(md_lines)

        WeComNotifier.dispatch_notification(f"{title}{batch_num_str}", text_content, md_content)
        if idx < len(batches) - 1:
            time.sleep(1.0)


def notify_price_drops(items: List[Dict]):
    """推送进一步降价商品"""
    if not items:
        return
    title = f"📉 SP站降价提醒：{len(items)} 款斗草价格进一步下调！"

    text_lines = [
        f"📉【SP站特价进一步降价！】",
        f"发现 {len(items)} 款特价斗草价格下调：",
        "----------------------------------------"
    ]
    md_lines = [
        f"## 📉 SP站特价进一步降价！",
        f"> 发现 **{len(items)}** 款特价斗草价格下调\n",
        "---"
    ]

    for it in items:
        old_p = it.get("old_price_usd", 0.0)
        new_p = it.get("sale_price_usd", 0.0)
        cny = it.get("sale_price_cny", 0.0)
        url = it.get("url", "")
        text_lines.append(
            f"【{it.get('brand')}】{it.get('title')}\n"
            f"• 降价前: ${old_p:.2f} ➔ 现特价: ${new_p:.2f} (折合 ¥{cny:.2f})\n"
            f"• 口味: {it.get('flavor_category')}\n"
            f"• 直达购买: <a href=\"{url}\">点击前往SP购买</a>\n"
        )
        md_lines.append(
            f"### [{it.get('brand')}] {it.get('title')}\n"
            f"> **降价前**: ${old_p:.2f} ➔ **现特价**: **${new_p:.2f}** (折合 ¥{cny:.2f})\n"
            f"> **口味**: {it.get('flavor_category')}\n"
            f"> [👉 直达链接]({url})\n"
        )

    WeComNotifier.dispatch_notification(title, "\n".join(text_lines), "\n".join(md_lines))


def notify_restocked(items: List[Dict]):
    """推送补货提醒（智能分批）"""
    if not items:
        return
    total_count = len(items)
    title = f"📦 SP站特价补货：{total_count} 款斗草恢复现货！"
    batches = chunk_items_by_bytes(items, max_bytes=1800)

    for idx, batch in enumerate(batches):
        batch_num_str = f" (第 {idx+1}/{len(batches)} 批)" if len(batches) > 1 else ""
        text_lines = [
            f"📦【SP站特价补货到货！】{batch_num_str}",
            f"原先缺货的 {total_count} 款特价草已恢复库存：",
            "----------------------------------------"
        ]
        md_lines = [
            f"## 📦 SP站特价补货到货！{batch_num_str}",
            f"> 原先缺货的 **{total_count}** 款特价草已恢复库存：\n",
            "---"
        ]
        for it in batch:
            text_lines.append(build_card_text_formatted(it))
            md_lines.append(build_card_markdown_formatted(it))

        WeComNotifier.dispatch_notification(f"{title}{batch_num_str}", "\n".join(text_lines), "\n".join(md_lines))
        if idx < len(batches) - 1:
            time.sleep(1.0)


def notify_daily_summary(all_items: List[Dict]):
    """推送全量在售特价总览"""
    if not all_items:
        return

    rate_desc = ""
    if all_items and all_items[0].get("rate_desc"):
        rate_desc = all_items[0]["rate_desc"]
    if not rate_desc:
        rate_desc = CurrencyConverter.get_source_desc()

    title = f"📋 SP站特价每日总览：在售 {len(all_items)} 款特价斗草"

    in_stock_items = [i for i in all_items if i.get("is_in_stock")]
    out_stock_items = [i for i in all_items if not i.get("is_in_stock")]

    text_lines = [
        f"📋【SP站每日特价斗草清单】",
        f"特价总量: 共 {len(all_items)} 款 (现货: {len(in_stock_items)} 款 / 缺货: {len(out_stock_items)} 款)",
        f"汇率基准: {rate_desc}",
        "----------------------------------------"
    ]
    md_lines = [
        f"## 📋 SP站每日特价斗草清单",
        f"> **特价总量**: 共 **{len(all_items)}** 款 (现货: {len(in_stock_items)} 款 / 缺货: {len(out_stock_items)} 款)",
        f"> **汇率基准**: {rate_desc}\n",
        "---"
    ]

    for it in in_stock_items[:12]:
        text_lines.append(build_card_text_formatted(it))
        md_lines.append(build_card_markdown_formatted(it))

    if len(in_stock_items) > 12:
        rem = len(in_stock_items) - 12
        text_lines.append(f"(更多 {rem} 款现货未全部展开，详见SP网站)")
        md_lines.append(f"> *(更多 {rem} 款现货未全部展开，详见SP网站)*\n")

    WeComNotifier.dispatch_notification(title, "\n".join(text_lines), "\n".join(md_lines))
