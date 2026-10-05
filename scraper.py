import re
import time
import logging
from urllib.parse import urljoin
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from curl_cffi import requests

from config import Config
from storage import Storage
from flavor_classifier import classify_flavor, translate_cut
from currency import CurrencyConverter

logger = logging.getLogger("Scraper")

class SmokingPipesScraper:
    BASE_URL = "https://www.smokingpipes.com"

    def __init__(self, storage: Storage):
        self.storage = storage
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.smokingpipes.com/",
        }
        self.proxies = {"http": Config.HTTP_PROXY, "https": Config.HTTP_PROXY} if Config.HTTP_PROXY else None

    def _get_html(self, url: str) -> Optional[str]:
        """使用 curl_cffi 发送请求并伪装 Chrome TLS 指纹穿透 Cloudflare"""
        try:
            resp = requests.get(
                url,
                impersonate="chrome120",
                headers=self.headers,
                proxies=self.proxies,
                timeout=25
            )
            if resp.status_code == 200:
                return resp.text
            else:
                logger.error(f"请求失败 [{resp.status_code}]: {url}")
                return None
        except Exception as e:
            logger.error(f"网络异常 [{url}]: {e}")
            return None

    def fetch_all_specials(self) -> List[Dict]:
        """
        抓取全部特价斗草。
        突破 'Show More' 截断策略：
        1. 访问 specials.cfm?specials=pipe-tobaccos 主页
        2. 提取所有特价品牌的专属 sale 专区链接（如 /pipe-tobacco/erik-stokkebye/?special=sale）
        3. 遍历访问各品牌 sale 专区，SP 站会在此页面输出该品牌的【全部】特价斗草（无5款折叠限制）
        4. 聚合主页及各品牌专区所有商品，按 product_id 去重合并
        """
        logger.info(f"开始抓取 SP 特价专区: {Config.SPECIALS_URL}")
        main_html = self._get_html(Config.SPECIALS_URL)
        if not main_html:
            logger.error("无法获取特价主页内容")
            return []

        soup = BeautifulSoup(main_html, "html.parser")
        products_dict: Dict[str, Dict] = {}

        # 1. 解析主页上现有的所有商品卡片
        self._parse_cards_from_soup(soup, products_dict)

        # 2. 提取各个特价品牌的专属 Sale 链接
        brand_sale_urls = []
        wraps = soup.find_all("div", class_="products-grouped-grid-wrap")
        for wrap in wraps:
            cat_div = wrap.find("div", class_="catTitle")
            if cat_div:
                a_tag = cat_div.find("a")
                if a_tag and a_tag.get("href"):
                    brand_url = urljoin(self.BASE_URL, a_tag["href"])
                    brand_sale_urls.append((a_tag.get_text(strip=True), brand_url))

        logger.info(f"在特价主页发现 {len(brand_sale_urls)} 个特价品牌专区: {[b[0] for b in brand_sale_urls]}")

        # 3. 逐个请求各品牌的 sale 专区获取全量商品（解决 Show More 隐藏）
        for brand_name, b_url in brand_sale_urls:
            time.sleep(1.0) # 礼貌延时
            logger.info(f"正在抓取品牌全量特价: {brand_name} -> {b_url}")
            b_html = self._get_html(b_url)
            if b_html:
                b_soup = BeautifulSoup(b_html, "html.parser")
                count_before = len(products_dict)
                self._parse_cards_from_soup(b_soup, products_dict)
                logger.info(f"该品牌获取完成，新增/更新商品: {len(products_dict) - count_before} 件")

        all_products = list(products_dict.values())
        logger.info(f"全网特价抓取完成，共获得 {len(all_products)} 款特价斗草")

        # 4. 补全口味、成分等规格信息
        for item in all_products:
            self._enrich_tobacco_details(item)

        return all_products

    def _parse_cards_from_soup(self, soup: BeautifulSoup, results: Dict[str, Dict]):
        cards = soup.find_all("article", class_="product-card")
        for card in cards:
            pid = card.get("data-productid")
            if not pid:
                # 尝试从 URL 或 a 标签提取
                url_attr = card.get("data-url", "")
                m = re.search(r"product_id/(\d+)", url_attr)
                if m:
                    pid = m.group(1)
                else:
                    continue

            # 标题与链接
            title_a = card.find("h3", class_="product-card-title")
            title = ""
            sku = ""
            rel_url = card.get("data-url", "")
            if title_a:
                a_tag = title_a.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    if not rel_url:
                        rel_url = a_tag.get("href", "")
                sku_div = title_a.find("div", class_="product-card-sku")
                if sku_div:
                    sku = sku_div.get_text(strip=True)

            if not title:
                # 降级尝试找 img alt
                img = card.find("img")
                if img and img.get("alt"):
                    title = img["alt"]

            # 品牌
            brand_div = card.find("div", class_="product-card-catname")
            brand = brand_div.get_text(strip=True) if brand_div else ""

            # 图片
            img = card.find("img")
            img_url = ""
            if img:
                img_url = img.get("src") or img.get("data-src") or ""

            # 折扣活动描述 (如 20% Off Mac Baren Tinned Pipe Tobacco)
            discount_div = card.find("div", class_="product-card-discount-msg")
            discount_msg = discount_div.get_text(strip=True) if discount_div else ""

            # 库存与价格
            nostock = card.find(class_=re.compile("nostock|outofstock", re.I))
            nostock_text = card.find(string=re.compile(r"out of stock", re.I))
            is_in_stock = not (bool(nostock) or bool(nostock_text))

            sale_price = 0.0
            regular_price = 0.0

            # 抓取价格文本
            base_price_el = card.find("span", class_="product-card-base-price")
            if base_price_el:
                price_match = re.search(r"\$([\d\.]+)", base_price_el.get_text())
                if price_match:
                    sale_price = float(price_match.group(1))

            strike_price_el = card.find("span", class_="product-card-strike-price")
            if strike_price_el:
                reg_match = re.search(r"\$([\d\.]+)", strike_price_el.get_text())
                if reg_match:
                    regular_price = float(reg_match.group(1))

            # 卡片上自带的 Family 与 Cut 信息
            family = ""
            cut = ""
            addtnl = card.find("div", class_="product-card-addtnl-details")
            if addtnl:
                addtnl_text = addtnl.get_text(separator="\n", strip=True)
                for line in addtnl_text.splitlines():
                    if "Family:" in line:
                        family = line.split("Family:", 1)[1].strip()
                    elif "Cut:" in line:
                        cut = line.split("Cut:", 1)[1].strip()

            full_url = urljoin(self.BASE_URL, rel_url)

            results[str(pid)] = {
                "product_id": str(pid),
                "sku": sku,
                "brand": brand,
                "title": title,
                "url": full_url,
                "image_url": img_url,
                "sale_price_usd": sale_price,
                "regular_price_usd": regular_price or sale_price,
                "is_in_stock": is_in_stock,
                "discount_msg": discount_msg,
                "family": family,
                "components": "",
                "cut": cut
            }

    def _enrich_tobacco_details(self, item: Dict):
        """补全斗草的成分、口味分类、人民币计算等"""
        pid = item["product_id"]

        # 先查本地持久化缓存
        cached = self.storage.get_detail_cache(pid)
        if cached:
            if not item.get("family"):
                item["family"] = cached.get("family", "")
            if not item.get("cut"):
                item["cut"] = cached.get("cut", "")
            item["components"] = cached.get("components", "")
            item["strength"] = cached.get("strength", "")
            item["taste"] = cached.get("taste", "")
            item["room_note"] = cached.get("room_note", "")
        else:
            # 仅当卡片上连 family 都没有时，才尝试爬取一次详情页
            if not item.get("family"):
                details = self._fetch_product_detail(item["url"])
                if details:
                    item["family"] = details.get("Family", "")
                    if not item.get("cut"):
                        item["cut"] = details.get("Cut", "")
                    item["components"] = details.get("Components", "")
                    item["strength"] = details.get("Strength", "")
                    item["taste"] = details.get("Taste", "")
                    item["room_note"] = details.get("Room Note", "")
                    self.storage.save_detail_cache(pid, details)
                time.sleep(1.0)

        # 智能口味分类 (L草, V草, 调味草等)
        flavor_cat, flavor_desc = classify_flavor(
            family=item.get("family", ""),
            components=item.get("components", ""),
            title=item.get("title", "")
        )
        item["flavor_category"] = flavor_cat
        item["flavor_desc"] = flavor_desc
        item["cut_cn"] = translate_cut(item.get("cut", ""), item.get("title", ""))

        # 人民币换算
        item["sale_price_cny"] = CurrencyConverter.to_cny(item["sale_price_usd"])
        item["regular_price_cny"] = CurrencyConverter.to_cny(item["regular_price_usd"])
        item["rate_desc"] = CurrencyConverter.get_source_desc()

    def _fetch_product_detail(self, detail_url: str) -> Dict[str, str]:
        """抓取单个商品详情页的属性表"""
        html = self._get_html(detail_url)
        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")
        details = {}

        # 提取 components / family / cut
        comp_ul = soup.find("ul", class_="detailsPage-components")
        if comp_ul:
            for li in comp_ul.find_all("li"):
                d = li.find("span", class_="detail")
                v = li.find("span", class_="value")
                if d and v:
                    details[d.get_text(strip=True).rstrip(":")] = v.get_text(strip=True)

        # 提取 Strength, Taste, Room Note
        for rc in soup.find_all("div", class_="detailPage-ratingcontainer"):
            label_div = rc.find("div", class_="detailPage-rating")
            val_div = rc.find("div", class_="detailPage-rating-text")
            if label_div and val_div:
                details[label_div.get_text(strip=True).rstrip(":")] = val_div.get_text(strip=True)

        return details
