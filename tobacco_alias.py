"""
斗草中文俗称与经典别名库
针对国内烟斗客日常交流习惯，建立品牌与经典调配的中文别名匹配字典
如：Three Nuns -> 三尼姑
    Autumn Evening -> 秋夜
    Mixture Scottish Blend -> 苏格兰混合 (麦包苏格兰)
    Nightcap -> 睡帽
    Navy Flake -> 海军切片
    Full Virginia Flake -> FVF
    Golden Sliced -> 大黄盖 / OGS
"""

import re
from typing import Tuple

# 品牌中文名映射
BRAND_CN_MAP = {
    "mac baren": "麦包 / Mac Baren",
    "cornell & diehl": "C&D / 康奈尔与迪尔",
    "peterson": "彼得森 / Peterson",
    "dunhill": "登喜路 / Dunhill",
    "samuel gawith": "SG / 萨缪尔·高威斯",
    "gawith, hoggarth & co.": "GH / 高威斯·霍加斯",
    "gawith & hoggarth": "GH / 高威斯·霍加斯",
    "rattray's": "雷特雷 / Rattray's",
    "g.l. pease": "GLP / 格利斯",
    "peter stokkebye": "PS / 彼得·斯托克比",
    "erik stokkebye 4th generation": "ES 4代 / 埃里克·斯托克比",
    "seattle pipe club": "SPC / 西雅图烟斗俱乐部",
    "savinelli": "沙芬 / Savinelli",
    "capstan": "帆船 / Capstan",
    "solani": "索拉尼 / Solani",
    "amphora": "双耳土罐 / Amphora",
    "captain black": "黑船长 / Captain Black",
    "lane limited": "兰恩 / Lane Limited",
    "ashton": "阿什顿 / Ashton",
    "w.o. larsen": "拉森 / W.O. Larsen",
    "davidoff": "大卫杜夫 / Davidoff",
    "erinmore": "爱莲摩尔 / Erinmore",
    "bell's": "三尼姑 / Bell's",
    "borkum riff": "BR帆船 / Borkum Riff",
    "chacom": "沙康 / Chacom",
    "robert lewis": "罗伯特·刘易斯",
    "presbyterian": "长老 / Presbyterian",
    "st. bruno": "圣布鲁诺 / St. Bruno"
}

# 斗草单品经典俗称词典 (关键词小写 -> 中文俗称与别名)
TOBACCO_ALIAS_RULES = [
    # 三尼姑
    (r"three nuns", "三尼姑 (经典硬币/切片)"),

    # Mac Baren 麦包全系
    (r"mixture scottish blend|scottish blend", "苏格兰混合 (麦包经典口粮苏格兰)"),
    (r"mac baren.*navy flake|navy flake.*mac baren", "麦包海航切片 (海军切片)"),
    (r"virginia no\.?\s*1|virginia #1", "V1 (弗吉尼亚1号)"),
    (r"vanilla cream", "香草奶油 (麦包经典香草调味)"),
    (r"mac baren.*virginia flake", "VF (麦包V切片)"),
    (r"plumcake|plum cake", "李子蛋糕 (朗姆酒香)"),
    (r"dark twist", "深色麻花 (黑麻花圆切片)"),
    (r"stockton", "斯托克顿 (硬币圆片)"),
    (r"club blend", "俱乐部调配"),
    (r"roll cake", "蛋糕卷 (圆切片)"),
    (r"hh old dark fired|old dark fired", "ODF (HH 老深火熏肯塔基)"),
    (r"hh pure virginia", "HH 纯V (纯弗吉尼亚切片)"),
    (r"hh latakia flake", "HH 拉塔基亚切片 (L草切片)"),
    (r"hh vintage syrian", "HH 叙利亚原酿 (叙利亚L草绝版)"),
    (r"hh rustica", "HH 鲁斯蒂卡 (高劲道黄花烟草)"),
    (r"hh burley flake", "HH 白肋切片"),
    (r"golden extra", "黄金特级 (金装白肋)"),
    (r"symphony", "交响乐"),
    (r"7 seas regular|seven seas regular", "白七海 (经典原味)"),
    (r"7 seas royal|seven seas royal", "蓝七海 (皇家调香)"),
    (r"7 seas gold|seven seas gold", "金七海 (黄金调香)"),
    (r"7 seas black|seven seas black", "黑七海 (黑卡文迪许)"),

    # Cornell & Diehl (C&D) 全系
    (r"autumn evening", "秋夜 (枫糖香草调味神草)"),
    (r"haunted bookshop", "闹鬼书店 (凶宅书店 / 经典高劲道白肋)"),
    (r"pirate kake", "海盗压饼 (75%重度重口L草压饼)"),
    (r"bayou morning", "海湾清晨 (25%重度珀草VaPer)"),
    (r"star of the east", "东方之星 (50%经典L草压饼)"),
    (r"old joe krantz", "老乔·克兰茨 (高劲道白肋经典)"),
    (r"billy budd", "比利·巴德 (雪茄叶调配)"),
    (r"briar fox", "石楠狐狸 (高密度纯压饼)"),
    (r"opening night", "首演之夜 (纯V压饼)"),
    (r"sunday picnic", "周日野餐 (V草+东方叶+珀草)"),
    (r"black frigate", "黑色护卫舰 (朗姆酒+L草)"),
    (r"sunset harbor flake", "日落港湾切片 (经典巴尔干切片)"),
    (r"pegasus", "飞马 (飞马座)"),
    (r"epiphany", "顿悟 (爱因斯坦最爱原配方复刻)"),
    (r"nutty irishman", "坚果爱尔兰人 (爱尔兰奶油榛子)"),
    (r"da vinci", "达芬奇 (托斯卡纳葡萄酒香)"),
    (r"bow-legged bear", "罗圈腿熊 (重度浓郁大杂烩压饼)"),
    (r"cross-eyed cricket", "斗鸡眼蟋蟀 (朗姆果香L草)"),

    # Peterson 彼得森 / Dunhill 登喜路老配方系列
    (r"nightcap", "睡帽 (经典重度英式泥炭烟熏神草)"),
    (r"early morning pipe", "早安 (晨斗 / 清晨第一斗)"),
    (r"my mixture 965|965", "965 (我的混合965 / 经典英式基石)"),
    (r"standard mixture", "标准调配 (标准混合)"),
    (r"royal yacht", "皇家游艇 (登喜路经典高尼古丁纯V)"),
    (r"elizabethan mixture", "伊丽莎白 (经典VaPer珀草调配)"),
    (r"de luxe navy rolls|navy rolls", "豪华海航铜钱 (海航卷 / 大钱圈)"),
    (r"london mixture", "伦敦混合 (经典东方L草)"),
    (r"university flake", "大学切片 (梅子果香白肋切片)"),
    (r"sherlock holmes", "福尔摩斯 (经典爱尔兰调香)"),
    (r"old dublin", "老都柏林 (爱尔兰经典巴尔干)"),
    (r"irish flake", "爱尔兰切片 (高强度硬核切片)"),
    (r"connoisseur's choice", "行家之选 (热带水果朗姆酒香)"),
    (r"sunset breeze", "落日微风 (阿玛雷托杏仁甜酒调香)"),
    (r"sweet killarney", "甜美基拉尼 (焦糖奶油调香)"),
    (r"balkan delight", "巴尔干之欢"),

    # Samuel Gawith (SG) 萨缪尔高威斯系列
    (r"full virginia flake|fvf", "FVF (全弗吉尼亚切片 / 经典纯V天花板)"),
    (r"st\.?\s*james flake", "圣詹姆斯切片 (经典VaPer珀里克切片)"),
    (r"squadron leader", "中队长 (英式调配空军中队长)"),
    (r"1792 flake", "1792 切片 (顿加豆威士忌重度熏香切片)"),
    (r"best brown flake|bbf", "BBF (最佳褐切片 / 甜醇纯V)"),
    (r"balkan flake", "巴尔干切片 (纯净L草与东方叶切片)"),
    (r"skiff mixture", "小艇混合 (经典东方叶调配)"),
    (r"perfection", "完美 (香草微调香英式L草)"),
    (r"cabbie's flake|cabbies flake", "马车夫切片 (圆硬币VaPer)"),
    (r"golden glow", "金色余晖 (金色干草甜V丝)"),
    (r"grousemoor", "雷鸟 (湖区草本古法香气)"),
    (r"navy flake.*gawith|gawith.*navy flake", "SG 海军切片 (朗姆酒香L切片)"),

    # Gawith Hoggarth (GH) 系列
    (r"bob's chocolate flake", "鲍勃巧克力切片 (可可香草微调L切片)"),
    (r"ennerdale flake", "安纳代尔切片 (湖区神草 / 经典花香调配)"),
    (r"louisiana flake", "路易斯安那切片 (经典VaPer切片)"),
    (r"dark flake unscented", "深色原味切片 (纯肯塔基高烈度切片)"),
    (r"kendal flake", "肯德尔切片 (经典湖区花香)"),
    (r"brown flake unscented", "棕切片原味"),

    # Rattray's 雷特雷系列
    (r"hal o'? the wynd", "风之谷 (经典高糖纯V草神作)"),
    (r"old gowrie", "老高瑞 (圆润甜醇纯V切片)"),
    (r"marlin flake", "马林切片 (经典长条纯V切片)"),
    (r"red rapparee", "红毛游击队 (经典红色巴尔干调配)"),
    (r"black mallory", "黑马洛里 (浓郁深醇苏格兰L草)"),
    (r"bagpiper's dream", "风笛手之梦 (干邑白兰地调香)"),
    (r"buckingham", "白金汉宫"),

    # G.L. Pease 格利斯系列
    (r"quiet nights", "寂静之夜 (安静之夜 / 经典现代重度巴尔干)"),
    (r"westminster", "西敏寺 (最正统伦敦纯正英式L草)"),
    (r"maltese falcon", "马耳他之鹰 (浓郁烟熏熏香L草)"),
    (r"chelsea morning", "切尔西清晨 (早餐茶配草 / 东方微L草)"),
    (r"gaslight", "煤气灯 (浓缩紧压L草大饼)"),
    (r"spark plug", "火花塞 (紧压深色烟饼)"),
    (r"abingdon", "阿宾顿 (大饱满巴尔干调配)"),
    (r"triple play", "三杀 (三重奏紧压插件)"),
    (r"jackknife plug", "折叠刀插件 (纯V与肯塔基硬块)"),
    (r"cumberland", "坎伯兰"),

    # Capstan 帆船系列
    (r"capstan.*navy cut.*blue|capstan.*blue", "蓝帆船 (海军切片原味纯V)"),
    (r"capstan.*navy cut.*gold|capstan.*gold|capstan.*yellow", "黄帆船 (金帆船 / 甜香金黄纯V)"),

    # Orlik 系列
    (r"golden sliced|ogs", "金丝切片 (大黄盖 / OGS / 经典柑橘纯V)"),
    (r"dark strong kentucky", "深色强劲肯塔基"),

    # Escudo
    (r"escudo", "小盾牌 (埃斯库多豪华海航铜钱硬币卷)"),

    # Peter Stokkebye 散草编号
    (r"luxury navy flake|ps400", "PS400 豪华海航切片"),
    (r"luxury bullseye flake|ps403", "PS403 牛眼切片 (带卡文迪许圆心硬币片)"),
    (r"luxury twist flake|ps401", "PS401 麻花切片 (椰香甜V麻花圈)"),
    (r"english luxury|ps17", "PS17 豪华英式"),
    (r"proper english|ps52", "PS52 正宗英式"),
    (r"balkan supreme|ps24", "PS24 巴尔干至尊 (经典散装巴尔干口粮)"),

    # Seattle Pipe Club 西雅图烟斗俱乐部
    (r"plum pudding", "李子布丁 (现代L草调配天花板)"),
    (r"mississippi river", "密西西比河 (经典甜润V/L压饼)"),
    (r"potlatch", "波特拉奇"),

    # Solani 索拉尼系列
    (r"solani.*633|633.*virginia flake", "索拉尼 633 (顶级VaPer蜂蜜切片)"),
    (r"solani.*660|660.*silver flake", "索拉尼 660 (银色切片 / 肯塔基纯V)"),
    (r"solani.*779", "索拉尼 779 (英式奢华调配)"),
    (r"solani.*656", "索拉尼 656 (纯白肋陈年压饼)"),

    # Erik Stokkebye 4th Generation 4代系列
    (r"1855", "1855 (ES4代 经典纯V干草麦香丝)"),
    (r"1882 founder'?s blend|1882", "1882 创始人 (ES4代 经典英式泥炭L草)"),
    (r"1897", "1897 (ES4代 香草蜂蜜香甜调调香草)"),
    (r"1931 flake|1931", "1931 切片 (ES4代 镇店金奖V/白肋切片)"),
    (r"1957", "1957 (ES4代 枫糖香草坚果丝)"),
    (r"1982", "1982 (ES4代 波本威士忌莓果调味)"),
    (r"4 seasons autumn|autumn mixture.*50g", "四季之秋 (ES4代 VaPer切片)"),
    (r"4 seasons spring|spring mixture.*50g", "四季之春 (ES4代 清甜调香草)"),
    (r"4 seasons summer|summer mixture.*50g", "四季之夏 (ES4代 英式L草)"),
    (r"4 seasons winter|winter mixture.*50g", "四季之冬 (ES4代 纯V切片)"),
    (r"heritage collection", "传承纪念版 (年度典藏)"),

    # Lane Limited 兰恩
    (r"lane.*1-q|1-q", "1-Q (全球销量第一香草调香散草)"),
    (r"lane.*rlp-6|rlp-6", "RLP-6 (经典巧克力坚果调配)"),
    (r"lane.*bca|bca", "BCA (双料重度黑卡文迪许)"),

    # Captain Black 黑船长
    (r"captain black regular|captain black original|captain black white", "白船长 (黑船长原味香草白袋)"),
    (r"captain black royal", "蓝船长 (黑船长皇家蓝袋)"),
    (r"captain black gold", "金船长 (黑船长黄金金袋)"),
    (r"captain black dark", "黑船长 (纯黑卡文迪许深黑袋)"),
    (r"captain black cherry", "红船长 (黑船长樱桃红袋)"),

    # Erinmore
    (r"erinmore flake", "菠萝切片 (爱莲摩尔经典水果果香切片)"),
    (r"erinmore mixture", "菠萝混合 (爱莲摩尔混合丝)"),

    # Presbyterian
    (r"presbyterian", "长老混合 (长老草 / 百年经典清润英式)"),

    # Ashton 阿什顿
    (r"artisan'?s blend", "工匠手选 (阿什顿工匠调配 / 重度浓郁L草)"),
    (r"rainy day", "雨天 (坚果威士忌调香)"),
    (r"guilty pleasure", "罪恶快感 (热带芒果柑橘调香)")
]

def get_brand_chinese(brand_raw: str) -> str:
    """获取品牌的中文对照名称"""
    if not brand_raw:
        return ""
    b_lower = brand_raw.lower().strip()
    for k, v in BRAND_CN_MAP.items():
        if k in b_lower:
            return v
    return brand_raw

def get_tobacco_chinese_alias(title: str, brand: str = "") -> str:
    """
    根据标题和品牌，智能匹配斗草在圈内的经典中文俗称/别名
    返回: 中文俗称字符串，如 '苏格兰混合 (麦包苏格兰)'，若无匹配则返回空字符串
    """
    search_str = f"{brand} {title}".lower()

    for pattern, alias in TOBACCO_ALIAS_RULES:
        if re.search(pattern, search_str, re.I):
            return alias

    return ""
