import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # 监控地址
    SPECIALS_URL = os.getenv(
        "SPECIALS_URL",
        "https://www.smokingpipes.com/specials.cfm?specials=pipe-tobaccos"
    )

    # 检查周期（分钟，默认 30 分钟）
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))

    # 海关美元计征汇率（如果为空，系统会自动在线获取当前基准汇率）
    # 例如填: 7.2150
    CUSTOMS_USD_RATE = float(os.getenv("CUSTOMS_USD_RATE", "0"))

    # 是否仅通知有现货的特价商品（True 则忽略 Out of Stock）
    ONLY_IN_STOCK = os.getenv("ONLY_IN_STOCK", "false").lower() in ("true", "1", "yes")

    # 首次启动是否发送当前全部特价草概览通知（默认 True）
    NOTIFY_ON_STARTUP = os.getenv("NOTIFY_ON_STARTUP", "true").lower() in ("true", "1", "yes")

    # 每日定时发送一次在售特价总清单的时间（格式 HH:MM，如 09:00，留空则不发送）
    DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "09:00")

    # 企业微信 API 代理地址 (如果 NAS 没有固定 IPv4，可使用 VPS 上的企微代理，如 http://140.245.40.253:56789)
    # 留空则默认直接请求官方地址 https://qyapi.weixin.qq.com
    WECOM_PROXY_URL = os.getenv("WECOM_PROXY_URL", "https://qyapi.weixin.qq.com").strip().rstrip("/")
    if not WECOM_PROXY_URL:
        WECOM_PROXY_URL = "https://qyapi.weixin.qq.com"

    # 企业微信应用推送 (推荐，微信内以应用消息形式接收)
    WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "").strip()
    WECOM_CORP_SECRET = os.getenv("WECOM_CORP_SECRET", "").strip()
    WECOM_AGENT_ID = os.getenv("WECOM_AGENT_ID", "").strip()
    WECOM_TO_USER = os.getenv("WECOM_TO_USER", "@all").strip()

    # 企业微信群机器人 Webhook (群内接收)
    WECOM_WEBHOOK_URL = os.getenv("WECOM_WEBHOOK_URL", "").strip()

    # PushPlus Token (备用纯个人微信推送通道)
    PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "").strip()

    # 代理设置 (如果在国内 NAS 部署可填如 http://192.168.1.x:7890，海外 VPS 留空)
    HTTP_PROXY = os.getenv("HTTP_PROXY", "").strip()

    # 数据存储目录
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "sp_monitor.db"

Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
