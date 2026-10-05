import sqlite3
import datetime
from typing import Dict, List, Tuple, Optional
from config import Config

class Storage:
    def __init__(self, db_path=Config.DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            # 记录历史特价与当前状态
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tobacco_specials (
                product_id TEXT PRIMARY KEY,
                sku TEXT,
                brand TEXT,
                title TEXT,
                sale_price_usd REAL,
                regular_price_usd REAL,
                is_in_stock INTEGER,
                discount_msg TEXT,
                family TEXT,
                components TEXT,
                cut TEXT,
                flavor_category TEXT,
                url TEXT,
                image_url TEXT,
                first_seen_at TIMESTAMP,
                last_seen_at TIMESTAMP,
                notified_at TIMESTAMP
            )
            """)

            # 斗草规格属性永久缓存（Family、Components、Cut 等）
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tobacco_details_cache (
                product_id TEXT PRIMARY KEY,
                family TEXT,
                components TEXT,
                cut TEXT,
                strength TEXT,
                taste TEXT,
                room_note TEXT,
                updated_at TIMESTAMP
            )
            """)
            conn.commit()

    def get_detail_cache(self, product_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM tobacco_details_cache WHERE product_id = ?",
                (str(product_id),)
            ).fetchone()
            if row:
                return dict(row)
        return None

    def save_detail_cache(self, product_id: str, details: dict):
        with self._get_conn() as conn:
            now = datetime.datetime.now().isoformat()
            conn.execute("""
            INSERT OR REPLACE INTO tobacco_details_cache
            (product_id, family, components, cut, strength, taste, room_note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(product_id),
                details.get("Family", ""),
                details.get("Components", ""),
                details.get("Cut", ""),
                details.get("Strength", ""),
                details.get("Taste", ""),
                details.get("Room Note", ""),
                now
            ))
            conn.commit()

    def diff_and_update(self, current_items: List[dict]) -> Tuple[List[dict], List[dict], List[dict]]:
        """
        对比当前扫描到的特价商品与数据库历史
        返回: (new_items: 新增特价, price_drops: 降价商品, restocked_items: 缺货转现货)
        """
        new_items = []
        price_drops = []
        restocked_items = []
        now = datetime.datetime.now().isoformat()

        with self._get_conn() as conn:
            for item in current_items:
                pid = str(item["product_id"])
                row = conn.execute(
                    "SELECT * FROM tobacco_specials WHERE product_id = ?",
                    (pid,)
                ).fetchone()

                if not row:
                    # 全新特价商品
                    new_items.append(item)
                    conn.execute("""
                    INSERT INTO tobacco_specials
                    (product_id, sku, brand, title, sale_price_usd, regular_price_usd, is_in_stock,
                     discount_msg, family, components, cut, flavor_category, url, image_url,
                     first_seen_at, last_seen_at, notified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pid, item.get("sku", ""), item.get("brand", ""), item.get("title", ""),
                        item.get("sale_price_usd", 0.0), item.get("regular_price_usd", 0.0),
                        1 if item.get("is_in_stock") else 0, item.get("discount_msg", ""),
                        item.get("family", ""), item.get("components", ""), item.get("cut", ""),
                        item.get("flavor_category", ""), item.get("url", ""), item.get("image_url", ""),
                        now, now, now
                    ))
                else:
                    # 已有记录，检查价格与库存状态变动
                    old_price = row["sale_price_usd"]
                    old_in_stock = bool(row["is_in_stock"])
                    curr_price = item.get("sale_price_usd", 0.0)
                    curr_in_stock = bool(item.get("is_in_stock"))

                    # 1. 价格更低了
                    if curr_price > 0 and curr_price < old_price - 0.01:
                        item["old_price_usd"] = old_price
                        price_drops.append(item)

                    # 2. 原先缺货现在补货到货了
                    if not old_in_stock and curr_in_stock:
                        restocked_items.append(item)

                    # 更新记录
                    conn.execute("""
                    UPDATE tobacco_specials
                    SET sale_price_usd = ?, regular_price_usd = ?, is_in_stock = ?,
                        discount_msg = ?, family = ?, components = ?, cut = ?,
                        flavor_category = ?, last_seen_at = ?
                    WHERE product_id = ?
                    """, (
                        curr_price, item.get("regular_price_usd", 0.0), 1 if curr_in_stock else 0,
                        item.get("discount_msg", ""), item.get("family", ""), item.get("components", ""),
                        item.get("cut", ""), item.get("flavor_category", ""), now, pid
                    ))

            conn.commit()

        return new_items, price_drops, restocked_items

    def get_all_active_specials(self) -> List[dict]:
        """获取最近活跃的全部特价商品"""
        with self._get_conn() as conn:
            rows = conn.execute("""
            SELECT * FROM tobacco_specials
            WHERE datetime(last_seen_at) >= datetime('now', '-2 days')
            ORDER BY is_in_stock DESC, brand ASC, title ASC
            """).fetchall()
            return [dict(r) for r in rows]
