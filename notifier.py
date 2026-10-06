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
    """通知分发引擎 (主通道 PushPlus 微信服务号，支持企微机器人备用)"""

    @classmethod
    def send_pushplus(cls, title: str, content: str) -> bool:
        """通过 PushPlus 发送个人微信推送"""
        if not Config.PUSHPLUS_TOKEN:
            logger.warning("未配置 PUSHPLUS_TOKEN，跳过推送")
            return False
        try:
            payload = {
                "token": Config.PUSHPLUS_TOKEN,
                "title": title,
                "content": content,
                "template": "markdown"
            }
            r = requests.post("https://www.pushplus.plus/send", json=payload, timeout=12)
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
    def send_wecom_webhook_markdown(cls, content: str) -> bool:
        """通过企业微信群机器人 Webhook 发送 Markdown 消息（选填备用）"""
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
    def dispatch_notification(cls, title: str, text_content: str, markdown_content: str):
        """统一分发通知到已启用的通知渠道"""
        sent = False
        # 1. 优先推送 PushPlus 微信公众号（主通道）
        if Config.PUSHPLUS_TOKEN:
            sent = cls.send_pushplus(title, markdown_content) or sent

        # 2. 企微群机器人备用（若有配置）
        if Config.WECOM_WEBHOOK_URL:
            sent = cls.send_wecom_webhook_markdown(markdown_content) or sent

        if not sent:
            logger.info("【本地预览】未配置或未成功发送通知，消息内容预览如下:")
            print("\n" + "="*50)
            print(f"【{title}】")
            print(markdown_content)
            print("="*50 + "\n")


def build_card_markdown_formatted(item: Dict) -> str:
    """格式化单款斗草的 Markdown 内容（严格一行一个类型，列表式工整排版）"""
    title = item.get("title", "未知品名")
    brand = item.get("brand", "SP")
    brand_cn = get_brand_chinese(brand) or brand
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
    stock_badge = '<font color="#2e7d32"><b>✅ 现货在售</b></font>' if in_stock else '<font color="#d32f2f"><b>⚠️ 暂时缺货待补</b></font>'

    lines = [f"### 【{brand_cn}】{title}"]
    if alias:
        lines.append(f"* **圈内俗称**: 🏷️ {alias}")
    lines.append(f"* **口味类型**: {flavor}")
    if flavor_desc:
        lines.append(f"* **风味特点**: {flavor_desc}")
    if cut:
        lines.append(f"* **裁切规格**: {cut}")

    if sale_usd > 0:
        lines.append(f"* **特价价格**: **${sale_usd:.2f}** (原价 ${reg_usd:.2f}{discount_str})")
        lines.append(f"* **折合RMB**: <font color=\"#e53935\"><b>¥{sale_cny:.2f}</b></font>")
    else:
        if reg_usd > 0:
            lines.append(f"* **原价参考**: ${reg_usd:.2f} (缺货待补)")
        else:
            lines.append(f"* **价格状态**: 缺货暂未标价")

    lines.append(f"* **库存状态**: {stock_badge}")
    if discount_msg:
        lines.append(f"* **活动信息**: {discount_msg}")

    lines.append(f"* **直达购买**: [👉 点击前往 SP 站购买]({url})\n")
    return "\n".join(lines)


def build_card_text_formatted(item: Dict) -> str:
    """格式化单款斗草纯文本内容"""
    return build_card_markdown_formatted(item)


def notify_new_specials(items: List[Dict]):
    """推送新上架特价斗草（PushPlus 单条支持 40KB，完整聚合呈现）"""
    if not items:
        return

    rate_desc = ""
    if items and items[0].get("rate_desc"):
        rate_desc = items[0]["rate_desc"]
    if not rate_desc:
        rate_desc = CurrencyConverter.get_source_desc()

    total_count = len(items)
    in_stock_cnt = len([i for i in items if i.get("is_in_stock")])
    out_stock_cnt = total_count - in_stock_cnt

    title = f"🔥 SP站特价上新通知：在售 {total_count} 款特价斗草"

    # 按现货在前排序
    sorted_items = sorted(items, key=lambda x: (not x.get("is_in_stock", False), x.get("brand", "")))

    md_lines = [
        f"# 🔥 SP站特价斗草实时清单",
        f"> **在售数量**: 共 **{total_count}** 款 (现货: {in_stock_cnt}款 / 缺货待补: {out_stock_cnt}款)",
        f"> **汇率基准**: {rate_desc}",
        f"> **特价主页**: [点击进入美国 SP 特价专区](https://www.smokingpipes.com/specials.cfm?specials=pipe-tobaccos)",
        f"\n---\n"
    ]

    for it in sorted_items:
        md_lines.append(build_card_markdown_formatted(it))

    md_content = "\n".join(md_lines)
    WeComNotifier.dispatch_notification(title, md_content, md_content)


def notify_price_drops(items: List[Dict]):
    """推送进一步降价商品"""
    if not items:
        return
    title = f"📉 SP站降价提醒：{len(items)} 款斗草价格进一步下调！"

    md_lines = [
        f"# 📉 SP站特价进一步降价！",
        f"> 发现 **{len(items)}** 款特价斗草价格进一步下调：\n",
        "---"
    ]

    for it in items:
        brand = it.get("brand", "")
        brand_cn = get_brand_chinese(brand) or brand
        alias = get_tobacco_chinese_alias(it.get("title", ""), brand)
        alias_str = f" (🏷️ {alias})" if alias else ""
        old_p = it.get("old_price_usd", 0.0)
        new_p = it.get("sale_price_usd", 0.0)
        cny = it.get("sale_price_cny") or CurrencyConverter.to_cny(new_p)
        url = it.get("url", "")
        md_lines.append(
            f"### 【{brand_cn}】{it.get('title')}{alias_str}\n"
            f"* **降价前**: ${old_p:.2f} ➔ **现特价**: **${new_p:.2f}**\n"
            f"* **折合RMB**: <font color=\"#e53935\"><b>¥{cny:.2f}</b></font>\n"
            f"* **口味**: {it.get('flavor_category')}\n"
            f"* [👉 点击直达购买]({url})\n"
        )

    md_content = "\n".join(md_lines)
    WeComNotifier.dispatch_notification(title, md_content, md_content)


def notify_restocked(items: List[Dict]):
    """推送补货提醒"""
    if not items:
        return
    total_count = len(items)
    title = f"📦 SP站特价补货：{total_count} 款斗草恢复现货！"
    md_lines = [
        f"# 📦 SP站特价补货到货！",
        f"> 原先缺货的 **{total_count}** 款特价草已恢复库存：\n",
        "---"
    ]
    for it in items:
        md_lines.append(build_card_markdown_formatted(it))

    md_content = "\n".join(md_lines)
    WeComNotifier.dispatch_notification(title, md_content, md_content)


def notify_daily_summary(all_items: List[Dict]):
    """推送全量在售特价总览"""
    notify_new_specials(all_items)
