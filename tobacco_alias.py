"""
斗草中文俗称与经典别名全库
针对国内烟斗客日常交流习惯，建立品牌与经典调配的中文别名匹配字典
涵盖 F&T 小白、红法、三尼姑、秋夜、闹鬼书店、睡帽、早安、965、FVF、大黄盖、
李子布丁、小盾牌、蓝帆船、黄帆船、彭赞斯、地窖青蛙等近两百款名草
"""

import re
from typing import Tuple

# 品牌中文名映射 (圈内俗名优先，兼顾原厂英文)
BRAND_CN_MAP = {
    "mac baren": "马坝 (Mac Baren)",
    "cornell & diehl": "CD (Cornell & Diehl)",
    "c&d": "CD (Cornell & Diehl)",
    "fribourg & treyer": "FT (Fribourg & Treyer)",
    "f&t": "FT (Fribourg & Treyer)",
    "peterson": "彼得森 (Peterson)",
    "dunhill": "登喜路 (Dunhill)",
    "samuel gawith": "SG (Samuel Gawith)",
    "gawith, hoggarth & co.": "GH (Gawith Hoggarth)",
    "gawith & hoggarth": "GH (Gawith Hoggarth)",
    "rattray's": "雷特雷 (Rattray's)",
    "g.l. pease": "GLP (G.L. Pease)",
    "peter stokkebye": "PS (Peter Stokkebye)",
    "erik stokkebye 4th generation": "ES4代 (Erik Stokkebye)",
    "erik stokkebye": "ES (Erik Stokkebye)",
    "seattle pipe club": "SPC (Seattle Pipe Club)",
    "savinelli": "沙芬 (Savinelli)",
    "capstan": "帆船 (Capstan)",
    "solani": "索拉尼 (Solani)",
    "dan tobacco": "丹王 (Dan Tobacco)",
    "robert mcconnell": "麦康奈尔 (McConnell)",
    "mcclelland": "麦克林兰 (McClelland)",
    "esoterica": "E家 (Esoterica)",
    "j.f. germain": "日耳曼 (Germain's)",
    "germain": "日耳曼 (Germain's)",
    "amphora": "土罐 (Amphora)",
    "captain black": "黑船长 (Captain Black)",
    "lane limited": "兰恩 (Lane Limited)",
    "ashton": "阿什顿 (Ashton)",
    "w.o. larsen": "拉森 (W.O. Larsen)",
    "davidoff": "大卫杜夫 (Davidoff)",
    "erinmore": "爱莲摩尔 (Erinmore)",
    "bell's": "三尼姑 (Bell's)",
    "borkum riff": "BR帆船 (Borkum Riff)",
    "chacom": "沙康 (Chacom)",
    "robert lewis": "罗伯特·刘易斯",
    "presbyterian": "长老 (Presbyterian)",
    "st. bruno": "圣布鲁诺 (St. Bruno)",
    "condor": "神雕 (Condor)",
    "orlik": "欧力克 (Orlik)",
    "cult": "邪教 (Cult)",
    "sutliff": "萨特利夫 (Sutliff)"
}

# 斗草单品经典俗称词典 (关键词正则 -> 中文俗称与别名)
TOBACCO_ALIAS_RULES = [
    # 1. Fribourg & Treyer (F&T) / FT 小白系列
    (r"cut virginia plug|cvp", "FT小白 (小白盖 / CVP纯V压饼天花板)"),
    (r"special brown flake", "FT棕切片 (特别褐切片)"),
    (r"vintage flake", "FT年份切片 (复古切片)"),
    (r"blackjack", "FT二十一点 (黑杰克)"),
    (r"golden mixture", "FT金色混合"),
    (r"wingate mixture", "FT温盖特混合"),

    # 2. 三尼姑 (Three Nuns)
    (r"three nuns", "三尼姑 (经典硬币/切片神作)"),

    # 3. 雷特雷 (Rattray's) 红法 / 风之谷 / 老高瑞
    (r"red rapparee", "红法 (红毛游击队 / 红色游击队 / 经典红色巴尔干)"),
    (r"hal o'? the wynd", "风之谷 (经典高糖纯V大名神作)"),
    (r"old gowrie", "老高瑞 (清甜纯V切片)"),
    (r"marlin flake", "马林切片 (经典长条纯V切片)"),
    (r"black mallory", "黑马洛里 (浓郁苏格兰L草)"),
    (r"bagpiper's dream", "风笛手之梦 (干邑白兰地调香)"),
    (r"7 reserve", "7号储备 (七号储备调配)"),
    (r"jocks blend", "苏格兰骑兵 (乔克混合)"),
    (r"accountant's mixture", "会计师混合"),
    (r"professional mixture", "专业混合"),
    (r"stirling flake", "斯特林切片"),
    (r"wallace flake", "华莱士切片"),
    (r"distinguished gentleman", "尊贵绅士"),

    # 4. 麦克林兰 (McClelland) 青蛙系列与红蛋糕 (红法)
    (r"frog morton's cellar|frog morton cellar", "地窖青蛙 (酒香青蛙 / 威士忌桶酿L草)"),
    (r"frog morton on the bayou", "海湾青蛙 (珀草青蛙 / VaPer+L草)"),
    (r"frog morton on the town", "小镇青蛙 (巴尔干青蛙)"),
    (r"frog morton across the pond", "跨界青蛙 (叙利亚青蛙)"),
    (r"frog morton", "大青蛙 (原味青蛙 / 绝版传奇神草)"),
    (r"5100|red cake", "红法 5100 (红蛋糕 / 麦克林兰经典纯红V)"),
    (r"dark star", "暗星 (黑星 / 深度陈化纯V熟草天花板)"),
    (r"blackwoods flake", "黑木切片 (经典黑木纯V)"),
    (r"st\.?\s*james woods", "圣詹姆斯森林 (经典浓郁VaPer)"),
    (r"christmas cheer", "圣诞欢歌 (年度绝版年份纯V)"),
    (r"beacon", "灯塔 (高糖V草)"),
    (r"tudor castle", "都铎城堡"),

    # 5. E家 (Esoterica) 彭赞斯 / 巨石阵
    (r"penzance", "E家彭赞斯 (P草 / 天花板重度英式L草压饼)"),
    (r"stonehaven", "E家巨石阵 (石避风港 / 水果酒香黑切片)"),
    (r"peacehaven", "E家和平港 (纯V金丝切片)"),
    (r"tilbury", "E家蒂尔伯里"),
    (r"margate", "E家马盖特"),
    (r"dorchester", "E家多切斯特"),
    (r"dunbar", "E家邓巴"),
    (r"and so to bed", "E家就寝安睡"),

    # 5.1 日耳曼 (J.F. Germain & Son) 腹黑 / 中切 / 1820 / 巴尔干 / 布朗切片
    (r"rich dark flake|rdf", "日耳曼腹黑 (RDF / 深色浓郁切片 / 顶级黑切片)"),
    (r"germain.*medium flake|medium flake.*germain", "日耳曼中切 (经典中度切片)"),
    (r"eighteen twenty|1820", "日耳曼1820 (1820切片)"),
    (r"balkan sobranie", "日耳曼巴尔干 (巴尔干沙芬草 / 传奇名草)"),
    (r"germain.*brown flake|brown flake.*germain", "日耳曼布朗切片 (梅花切片 / 经典纯V)"),
    (r"germain.*special flake|special flake.*germain", "日耳曼特殊切片"),
    (r"royal jersey", "日耳曼皇家泽西 (经典泽西切片)"),
    (r"uncle tom", "日耳曼汤姆叔叔"),
    (r"king charles", "日耳曼查尔斯国王"),
    (r"bridge mixture", "日耳曼桥牌混合"),
    (r"hampton flake|hampton", "日耳曼汉普顿"),

    # 6. 丹王 (Dan Tobacco / DT) 蓝调 / 魔鬼假日 / 咸狗 / 汉堡舵手
    (r"blue note", "蓝调 (蓝狗 / 经典水果香草调味大名神草)"),
    (r"devil'?s holiday", "魔鬼假日 (蓝莓野莓浓香调味神草)"),
    (r"hamborger veermaster", "汉堡舵手 (四桅帆船 / 纯金黄V切片)"),
    (r"salty dogs", "咸狗插件 (Salty Dogs Plug / 朗姆酒VaPer小方块)"),
    (r"timm'?s london blend", "蒂姆伦敦混合"),
    (r"sweet dublin", "甜美都柏林 (爱尔兰威士忌调味)"),
    (r"milonga", "米隆加 (香草焦糖调配)"),
    (r"patriot flake", "爱国者切片"),

    # 7. 麦康奈尔 (Robert McConnell) 红星 / 纯古巴
    (r"scottish cake", "苏格兰蛋糕 (红星 / 经典红V苏格兰调配)"),
    (r"red virginia", "红法纯红V (红弗吉尼亚)"),
    (r"pure cuba", "纯古巴 (古巴雪茄叶调配)"),
    (r"black parrot", "黑鹦鹉 (经典高阶VaPer切片)"),
    (r"paddington", "帕丁顿 (复刻皇家游艇)"),
    (r"regent street", "摄政街 (复刻登喜路切片)"),
    (r"piccadilly circus", "皮卡迪利广场 (复刻伦敦混合)"),
    (r"boutique blend", "精品调配 (复刻965)"),
    (r"night flight", "夜间飞行 (复刻睡帽)"),
    (r"early bird", "早鸟 (复刻早安晨斗)"),

    # 8. Mac Baren 马坝全系
    (r"mixture scottish blend|scottish blend", "苏格兰混合 (马坝经典口粮苏格兰)"),
    (r"mac baren.*navy flake|navy flake.*mac baren", "马坝海航切片 (海军切片)"),
    (r"virginia no\.?\s*1|virginia #1", "V1 (弗吉尼亚1号)"),
    (r"vanilla cream", "香草奶油 (马坝经典香草调味)"),
    (r"mac baren.*virginia flake", "VF (马坝V切片)"),
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

    # 9. Cornell & Diehl (CD) 全系
    (r"autumn evening", "秋夜 (CD 枫糖香草调味神草)"),
    (r"haunted bookshop", "闹鬼书店 / 凶宅书店 (CD 经典高劲道白肋)"),
    (r"pirate kake", "海盗压饼 (CD 75%重度重口L草压饼)"),
    (r"bayou morning", "海湾清晨 (CD 25%重度珀草VaPer)"),
    (r"star of the east", "东方之星 (CD 50%经典L草压饼)"),
    (r"old joe krantz|ojk", "老乔·克兰茨 (CD 高劲道白肋经典)"),
    (r"billy budd", "比利·巴德 (CD 雪茄叶调配)"),
    (r"briar fox", "石楠狐狸 (CD 高密度纯压饼)"),
    (r"opening night", "首演之夜 (CD 纯V压饼)"),
    (r"sunday picnic", "周日野餐 (CD V草+东方叶+珀草)"),
    (r"black frigate", "黑色护卫舰 (CD 朗姆酒+L草)"),
    (r"sunset harbor flake", "日落港湾切片 (CD 经典巴尔干切片)"),
    (r"pegasus", "飞马 (飞马座)"),
    (r"epiphany", "顿悟 (CD 爱因斯坦最爱原配方复刻)"),
    (r"nutty irishman", "坚果爱尔兰人 (CD 爱尔兰奶油榛子)"),
    (r"da vinci", "达芬奇 (CD 托斯卡纳葡萄酒香)"),
    (r"bow-legged bear", "罗圈腿熊 (CD 重度浓郁大杂烩压饼)"),
    (r"cross-eyed cricket", "斗鸡眼蟋蟀 (CD 朗姆果香L草)"),
    (r"bijou", "碧珠 (CD 蜂蜜沉香陈化纯V)"),
    (r"chenet'?s cask", "雪奈木桶 (CD 35%重度珀里克VaPer)"),
    (r"red odessa", "红色敖德萨 (CD 红法调配)"),
    (r"engine #?99", "99号机车"),
    (r"exhausted rooster", "疲倦的公鸡"),
    (r"dreams of kadath", "卡达斯之梦 (克苏鲁神话系列)"),

    # 10. Peterson 彼得森 / Dunhill 登喜路老配方系列
    (r"nightcap", "睡帽 (经典重度英式泥炭烟熏神草)"),
    (r"early morning pipe|emp", "早安 (晨斗 / 清晨第一斗)"),
    (r"my mixture 965|965", "965 (我的混合965 / 经典英式基石)"),
    (r"standard mixture", "标准调配 (标准混合)"),
    (r"royal yacht", "皇家游艇 (登喜路经典高尼古丁纯V)"),
    (r"elizabethan mixture", "伊丽莎白 (经典VaPer珀草调配)"),
    (r"de luxe navy rolls|navy rolls", "豪华海航铜钱 (海航卷 / 大钱圈)"),
    (r"peterson.*flake|dunhill.*flake", "小白盖 (登喜路/彼得森经典纯V切片)"),
    (r"london mixture", "伦敦混合 (经典东方L草)"),
    (r"university flake", "大学切片 (梅子果香白肋切片)"),
    (r"sherlock holmes", "福尔摩斯 (经典爱尔兰调香纯V)"),
    (r"old dublin", "老都柏林 (爱尔兰经典巴尔干)"),
    (r"irish flake", "爱尔兰切片 (高强度硬核切片)"),
    (r"connoisseur's choice", "行家之选 (热带水果朗姆酒香)"),
    (r"sunset breeze", "落日微风 (阿玛雷托杏仁甜酒调香)"),
    (r"sweet killarney", "甜美基拉尼 (焦糖奶油调香)"),
    (r"balkan delight", "巴尔干之欢"),

    # 11. Samuel Gawith (SG) 萨缪尔高威斯系列
    (r"full virginia flake|fvf", "FVF (全弗吉尼亚切片 / 经典纯V天花板)"),
    (r"st\.?\s*james flake", "圣詹姆斯切片 (经典VaPer珀里克切片)"),
    (r"squadron leader", "中队长 (英式调配空军中队长)"),
    (r"1792 flake|1792", "1792 (顿加豆威士忌重度熏香切片)"),
    (r"best brown flake|bbf", "BBF (最佳褐切片 / 甜醇纯V)"),
    (r"balkan flake", "巴尔干切片 (纯净L草与东方叶切片)"),
    (r"skiff mixture", "小艇混合 (经典东方叶调配)"),
    (r"perfection", "完美 (香草微调香英式L草)"),
    (r"cabbie's flake|cabbies flake", "马车夫切片 (圆硬币VaPer)"),
    (r"golden glow", "金色余晖 (金色干草甜V丝)"),
    (r"grousemoor", "雷鸟 (湖区草本古法香气)"),
    (r"navy flake.*gawith|gawith.*navy flake", "SG 海军切片 (朗姆酒香L切片)"),
    (r"black xx", "黑绞线 (大黑绳 / 极高烈度生烟绳)"),
    (r"brown no\.?\s*4", "棕色4号草绳 (棕绳 / 纯正强劲烟绳)"),
    (r"bothy flake", "石屋切片 (麦芽威士忌L切片)"),
    (r"fire dance flake", "火之舞切片 (黑莓白兰地调香)"),
    (r"celtic talisman", "凯尔特护身符 (樱桃香草调味)"),
    (r"commonwealth", "英联邦混合 (50%V+50%L直球调配)"),

    # 12. Gawith Hoggarth (GH) 系列
    (r"bob's chocolate flake", "鲍勃巧克力切片 (可可香草微调L切片)"),
    (r"ennerdale flake", "安纳代尔切片 (湖区神草 / 经典肥皂花香天花板)"),
    (r"louisiana flake", "路易斯安那切片 (经典VaPer切片)"),
    (r"dark flake unscented", "深色原味切片 (纯肯塔基高烈度切片)"),
    (r"dark flake scented", "深色加香切片 (湖区花香加香肯塔基)"),
    (r"kendal flake", "肯德尔切片 (纯正湖区花香纯V)"),
    (r"dark bird'?s eye", "深色鸟眼 (大金刚 / 极细切丝高劲道肯塔基)"),
    (r"happy .*bogie|brown bogie", "快乐小车 (黑粗绳 / 高烈度)"),
    (r"rum flake", "朗姆酒切片"),
    (r"coniston cut plug", "科尼斯顿切块 (高烈度硬核)"),
    (r"bosun cut plug", "水手长切块 (丁香薄荷微调香)"),

    # 13. G.L. Pease (GLP) 格利斯系列
    (r"quiet nights", "寂静之夜 (安静之夜 / 经典现代重度巴尔干)"),
    (r"westminster", "西敏寺 (最正统伦敦纯正英式L草)"),
    (r"maltese falcon", "马耳他之鹰 (浓郁烟熏熏香L草)"),
    (r"chelsea morning", "切尔西清晨 (早餐茶配草 / 东方微L草)"),
    (r"gaslight", "煤气灯 (浓缩紧压L草大饼)"),
    (r"spark plug", "火花塞 (紧压深色烟饼)"),
    (r"abingdon", "阿宾顿 (大饱满巴尔干调配)"),
    (r"triple play", "三杀 (三重奏紧压插件)"),
    (r"jackknife plug", "折叠刀插件 (纯V与肯塔基硬块)"),
    (r"haddo'?s delight", "哈多的喜悦 (经典复杂白兰地VaPer)"),
    (r"cairo", "开罗 (东方叶甜V草)"),
    (r"telegraph hill", "电报山 (雾系列经典VaPer)"),
    (r"fillmore", "菲尔莫尔 (雾系列重度VaPer切片)"),
    (r"embarcadero", "内河码头 (纯V+东方叶压饼)"),
    (r"key largo", "基拉戈 (雪茄叶调配)"),
    (r"windjammer", "大帆船 (朗姆酒海军切片)"),

    # 14. Capstan 帆船系列
    (r"capstan.*navy cut.*blue|capstan.*blue", "蓝帆船 (航海帆船原味纯V切片)"),
    (r"capstan.*navy cut.*gold|capstan.*gold|capstan.*yellow", "黄帆船 (金帆船 / 甜香金黄纯V切片)"),

    # 15. Orlik 欧力克系列
    (r"golden sliced|ogs", "金丝切片 (大黄盖 / OGS / 经典柑橘纯V)"),
    (r"dark strong kentucky", "深色强劲肯塔基 (大黑盒)"),

    # 16. Escudo
    (r"escudo", "小盾牌 (埃斯库多豪华海航铜钱卷)"),

    # 17. Peter Stokkebye 散草编号
    (r"luxury navy flake|ps400", "PS400 豪华海航切片"),
    (r"luxury bullseye flake|ps403", "PS403 牛眼切片 (带卡文迪许圆心硬币片)"),
    (r"luxury twist flake|ps401", "PS401 麻花切片 (椰香甜V麻花圈)"),
    (r"english luxury|ps17", "PS17 豪华英式"),
    (r"proper english|ps52", "PS52 正宗英式"),
    (r"balkan supreme|ps24", "PS24 巴尔干至尊 (经典散装巴尔干口粮)"),

    # 18. Seattle Pipe Club 西雅图烟斗俱乐部
    (r"plum pudding", "李子布丁 (现代L草调配天花板)"),
    (r"mississippi river", "密西西比河 (经典甜润V/L压饼)"),
    (r"potlatch", "波特拉奇"),

    # 19. Solani 索拉尼系列
    (r"solani.*633|633.*virginia flake", "索拉尼 633 (顶级蜂蜜VaPer切片)"),
    (r"solani.*660|660.*silver flake", "索拉尼 660 (银色切片 / 肯塔基纯V)"),
    (r"solani.*779", "索拉尼 779 (英式奢华调配)"),
    (r"solani.*656", "索拉尼 656 (纯白肋陈年压饼)"),
    (r"solani.*369", "索拉尼 369 (甜蜜之谜)"),

    # 20. Savinelli 沙芬
    (r"140th anniversary", "沙芬 140周年 (红茶落神花纯V压饼)"),
    (r"doblone d'?oro", "沙芬金币 (豪华金币切片)"),

    # 21. Erik Stokkebye 4th Generation 4代系列
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

    # 22. Lane Limited 兰恩
    (r"lane.*1-q|1-q", "1-Q (全球销量第一香草调香散草)"),
    (r"lane.*rlp-6|rlp-6", "RLP-6 (经典巧克力坚果调配)"),
    (r"lane.*bca|bca", "BCA (双料重度黑卡文迪许)"),

    # 23. Captain Black 黑船长
    (r"captain black regular|captain black original|captain black white", "白船长 (黑船长原味香草白袋)"),
    (r"captain black royal", "蓝船长 (黑船长皇家蓝袋)"),
    (r"captain black gold", "金船长 (黑船长黄金金袋)"),
    (r"captain black dark", "黑船长 (纯黑卡文迪许深黑袋)"),
    (r"captain black cherry", "红船长 (黑船长樱桃红袋)"),

    # 24. Erinmore / St. Bruno / Condor
    (r"erinmore flake", "菠萝切片 (爱莲摩尔经典热带水果切片)"),
    (r"erinmore mixture", "菠萝混合 (爱莲摩尔混合丝)"),
    (r"st\.?\s*bruno flake", "圣布鲁诺切片 (经典英格兰老味道)"),
    (r"condor", "秃鹰 (神雕切片 / 极强劲度古典香气)"),

    # 25. Presbyterian
    (r"presbyterian", "长老混合 (长老草 / 百年经典清润英式)"),

    # 26. Ashton
    (r"artisan'?s blend", "工匠手选 (阿什顿工匠调配 / 重度浓郁L草)"),
    (r"rainy day", "雨天 (坚果威士忌调香)"),
    (r"guilty pleasure", "罪恶快感 (热带芒果柑橘调香)"),

    # 27. Davidoff
    (r"flake medallions", "大卫杜夫 铜钱切片 (金币圆片 / 纯V+珀草+黑心)"),
    (r"royalty", "大卫杜夫 皇家特选 (优雅英式调配)")
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
