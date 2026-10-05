"""
斗草口味与类型智能分类器
针对烟斗爱好者习惯，将英文 Family、Components、Cut 智能映射为中文：
L草 (拉塔基亚/英式/巴尔干)
V草 (弗吉尼亚纯草 / VaPer 珀草调配)
调味草 (Aromatic 调香)
白肋草 / 肯塔基 (Burley / DFK)
雪茄叶调配 (Cigar Leaf) 等
"""

from typing import Dict, Tuple

CUT_TRANSLATIONS = {
    "ribbon": "细切丝 (Ribbon)",
    "flake": "切片 (Flake)",
    "broken flake": "碎切片 (Broken Flake)",
    "ready rubbed": "预揉碎切片 (Ready Rubbed)",
    "plug": "紧压烟块 (Plug)",
    "rope": "草绳麻花 (Rope)",
    "twist": "草绳麻花 (Twist)",
    "coin": "硬币圆切片 (Coin Cut)",
    "curly cut": "圆切片 (Curly Cut)",
    "shag": "细发丝 (Shag)",
    "crumble kake": "压饼 (Crumble Kake)",
    "kake": "压饼 (Kake)",
    "cake": "压饼 (Cake)",
    "cube cut": "立方体切 (Cube Cut)"
}

def translate_cut(cut_raw: str, title: str = "") -> str:
    if cut_raw:
        cut_lower = cut_raw.lower().strip()
        for k, v in CUT_TRANSLATIONS.items():
            if k in cut_lower:
                return v
        return cut_raw
    # 如果 cut 为空，尝试从标题推断
    t_lower = (title or "").lower()
    for k, v in CUT_TRANSLATIONS.items():
        if k in t_lower:
            return v
    if "pouch" in t_lower:
        return "袋装丝 (Ribbon)"
    return "详见规格"

def classify_flavor(family: str = "", components: str = "", title: str = "") -> Tuple[str, str]:
    """
    根据 Family、Components 和 Title 智能判定口味大类
    返回: (口味标签例如 '🍂 L草 (英式/拉塔基亚)', 详细特点/成分说明)
    """
    fam = (family or "").lower().strip()
    comp = (components or "").lower().strip()
    tit = (title or "").lower().strip()

    # 1. 优先检测是否为 L草 (Latakia) / 英式 / 巴尔干
    # 只要成分含有 Latakia，或者家族属于 English / Balkan / Scottish
    if "latakia" in comp or any(k in fam for k in ["english", "balkan", "scottish", "latakia"]):
        if "balkan" in fam or "balkan" in tit:
            return "🍂 L草 (巴尔干调配 / Balkan)", "重度浓郁烟熏拉塔基亚与东方叶配比"
        elif "scottish" in fam or "scottish" in tit:
            return "🍂 L草 (苏格兰调配 / Scottish)", "圆润平衡，含L草、V草与白肋"
        return "🍂 L草 (英式调配 / English)", "以拉塔基亚与东方叶为主的经典烟熏泥炭香"

    # 2. 检测雪茄叶调配
    if "cigar" in comp or "cigar" in fam or "cigar" in tit:
        return "🪵 雪茄叶调配 (Cigar Leaf)", "融入雪茄烟叶，香气醇厚深沉"

    # 3. 检测调味草 (Aromatic)
    if "aromatic" in fam or any(k in comp for k in ["cavendish", "black cavendish"]) and "virginia" not in fam:
        return "🍬 调味草 (Aromatic / 调香)", "香气甜美突出，室韵极佳"

    # 4. 检测 V草 (Virginia / VaPer)
    if "virginia" in fam or "vaper" in tit or ("virginia" in comp and not any(k in comp for k in ["latakia", "burley"])):
        # 细分是否为 VaPer (含有 Perique 珀里克)
        if "perique" in comp or "vaper" in tit or "perique" in fam:
            return "🌿 V草 (VaPer 珀草调配)", "弗吉尼亚甜醇搭配珀里克酸甜与胡椒辛香"
        return "🌿 V草 (弗吉尼亚纯草 / V调配)", "以清甜、干草麦香为特色的经典V草"

    # 5. 检测白肋草 / 肯塔基 (Burley / DFK)
    if "burley" in fam or "kentucky" in fam or "dark fired" in comp or "kentucky" in comp:
        return "🌰 白肋草 (Burley / 肯塔基DFK)", "坚果可可香气，劲道扎实饱满"

    # 6. 如果家族包含 Aromatic
    if "aromatic" in fam:
        return "🍬 调味草 (Aromatic)", "调香型风味"

    # 7. 备用兜底判定
    if fam:
        return f"📦 其他调配 ({family})", components or "详见商品规格"

    return "📦 综合调配", components or "未知配方"
