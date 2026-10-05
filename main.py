import sys
import time
import argparse
import logging
import datetime
from config import Config
from storage import Storage
from scraper import SmokingPipesScraper
from notifier import notify_new_specials, notify_price_drops, notify_restocked, notify_daily_summary

# 配置日志输出格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Main")

def run_check(storage: Storage, scraper: SmokingPipesScraper, is_startup: bool = False):
    logger.info("========== 开始执行特价草检查轮询 ==========")
    try:
        current_items = scraper.fetch_all_specials()
        if not current_items:
            logger.warning("本次未获取到任何特价商品数据，请检查网络或配置")
            return

        # 如果开启了只保留现货
        if Config.ONLY_IN_STOCK:
            items_to_check = [item for item in current_items if item.get("is_in_stock")]
        else:
            items_to_check = current_items

        # 与历史数据做 diff
        new_items, price_drops, restocked_items = storage.diff_and_update(items_to_check)

        logger.info(
            f"Diff 结果 -> 新特价: {len(new_items)} 款 | 降价: {len(price_drops)} 款 | 补货: {len(restocked_items)} 款"
        )

        # 首次启动时的通知逻辑
        if is_startup:
            if Config.NOTIFY_ON_STARTUP and new_items:
                logger.info(f"初次运行，发送当前正在打折的 {len(new_items)} 款斗草清单...")
                notify_new_specials(new_items)
            return

        # 日常轮询有变化时推送
        if new_items:
            logger.info(f"检测到新特价斗草上架，准备发送通知 ({len(new_items)}款)")
            notify_new_specials(new_items)

        if price_drops:
            logger.info(f"检测到特价草降价，准备发送通知 ({len(price_drops)}款)")
            notify_price_drops(price_drops)

        if restocked_items:
            logger.info(f"检测到特价草补货，准备发送通知 ({len(restocked_items)}款)")
            notify_restocked(restocked_items)

    except Exception as e:
        logger.exception(f"执行检查过程中发生未捕获异常: {e}")
    finally:
        logger.info("========== 检查轮询结束 ==========\n")


def main():
    parser = argparse.ArgumentParser(description="Smokingpipes 特价斗草微信监控系统")
    parser.add_argument("--once", action="store_true", help="单次执行检查后立即退出")
    args = parser.parse_args()

    storage = Storage()
    scraper = SmokingPipesScraper(storage)

    if args.once:
        logger.info("以单次运行模式启动 (--once)")
        run_check(storage, scraper, is_startup=False)
        return

    logger.info(f"Smokingpipes 监控服务已启动！监控周期: 每 {Config.CHECK_INTERVAL_MINUTES} 分钟一次")
    # 首次执行
    run_check(storage, scraper, is_startup=True)

    last_daily_report_date = None

    while True:
        try:
            sleep_seconds = Config.CHECK_INTERVAL_MINUTES * 60
            logger.info(f"等待下一次检查，休眠 {Config.CHECK_INTERVAL_MINUTES} 分钟...")
            time.sleep(sleep_seconds)

            # 检查日常报告
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")
            current_time_str = now.strftime("%H:%M")

            if Config.DAILY_REPORT_TIME and current_time_str >= Config.DAILY_REPORT_TIME and last_daily_report_date != today_str:
                logger.info("触发每日特价斗草汇总推送...")
                all_specials = storage.get_all_active_specials()
                notify_daily_summary(all_specials)
                last_daily_report_date = today_str

            run_check(storage, scraper, is_startup=False)

        except KeyboardInterrupt:
            logger.info("接收到退出信号，程序安全退出")
            break
        except Exception as e:
            logger.error(f"主调度循环异常: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
