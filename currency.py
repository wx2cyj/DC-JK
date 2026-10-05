import time
import logging
import requests
from config import Config

logger = logging.getLogger("Currency")

class CurrencyConverter:
    _cached_rate = None
    _last_fetched = 0
    _source_desc = ""

    @classmethod
    def get_usd_to_cny_rate(cls) -> float:
        """获取美元兑人民币汇率"""
        # 1. 优先使用用户配置的固定单月海关计征汇率
        if Config.CUSTOMS_USD_RATE > 0:
            cls._cached_rate = Config.CUSTOMS_USD_RATE
            cls._source_desc = f"海关月度计征汇率 ({Config.CUSTOMS_USD_RATE:.4f})"
            return cls._cached_rate

        # 2. 如果已有缓存且在 6 小时内，直接使用
        now = time.time()
        if cls._cached_rate and (now - cls._last_fetched < 21600):
            return cls._cached_rate

        # 3. 在线获取基准汇率
        endpoints = [
            ("https://open.er-api.com/v6/latest/USD", lambda r: r.json()["rates"]["CNY"]),
            ("https://api.exchangerate-api.com/v4/latest/USD", lambda r: r.json()["rates"]["CNY"])
        ]

        for url, parser in endpoints:
            try:
                proxies = {"http": Config.HTTP_PROXY, "https": Config.HTTP_PROXY} if Config.HTTP_PROXY else None
                resp = requests.get(url, timeout=10, proxies=proxies)
                if resp.status_code == 200:
                    rate = float(parser(resp))
                    if rate > 0:
                        cls._cached_rate = round(rate, 4)
                        cls._last_fetched = now
                        cls._source_desc = f"实时基准汇率 ({cls._cached_rate:.4f})"
                        logger.info(f"成功获取 USD/CNY 汇率: {cls._cached_rate}")
                        return cls._cached_rate
            except Exception as e:
                logger.warning(f"获取汇率失败 ({url}): {e}")

        # 4. 兜底汇率
        if not cls._cached_rate:
            cls._cached_rate = 7.20
            cls._source_desc = "默认预设汇率 (7.2000)"
            logger.warning("无法获取最新汇率，使用兜底汇率 7.20")
        return cls._cached_rate

    @classmethod
    def get_source_desc(cls) -> str:
        if not cls._source_desc:
            cls.get_usd_to_cny_rate()
        return cls._source_desc

    @classmethod
    def to_cny(cls, usd_amount: float) -> float:
        """将美元转换为人民币"""
        rate = cls.get_usd_to_cny_rate()
        return round(usd_amount * rate, 2)
