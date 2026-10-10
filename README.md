# Smokingpipes (美国 SP 站) 特价斗草微信监控系统 (DC-JK)

专门监控美国知名烟斗电商 Smokingpipes (SP 站) 特价斗草专区的全自动化监控推送系统。突破 Cloudflare 盾防、突破 `Show More` 按钮隐藏截断、严格按《海关总署第 272 号令》法定基准日自动推算美元汇率、内置近两百款老斗客黑话俗称与口味分类（L草、V草、调味草等），并通过微信服务号实现电脑版与手机版无损图文卡片秒级推送。

---

## 🚀 核心架构与核心特性

1. **严格遵循《海关总署第 272 号令》法定计征汇率算法**：
   - **法定规则**：每月海关计征汇率 = **上个月第三个星期三的中国人民银行人民币汇率中间价**（如遇休市顺延下一个交易日）。
   - **全自动日历推算**：系统内置日历回溯矩阵，自动推算当月法定基准日（如 2026 年 10 月基准日为 `2026-09-16`，央行中间价为 `6.7628`；11 月基准日自动推算为 `2026-10-21` 等）。
   - **权威标注与核算**：推送卡片明确标注法定基准日与核定汇率，每一罐斗草的人民币到手基准价精确换算，绝非市面粗算。

2. **内置圈内黑话俗称与风味分类库 (`tobacco_alias.py`)**：
   - 告别纯英文生硬机翻，收录近两百款国内外老饕经典草名：
     - **FT小白**：`Fribourg & Treyer Cut Virginia Plug (CVP)` ➔ **FT小白 (小白盖 / CVP纯V压饼天花板)**
     - **红法**：`Rattray's Red Rapparee` ➔ **红法 (红毛游击队 / 经典红色巴尔干)**，`McClelland 5100` ➔ **红法 5100 (红蛋糕 / 纯红V)**
     - **三尼姑**：`Bell's Three Nuns` ➔ **三尼姑 (经典硬币/切片神作)**
     - **秋夜 / 闹鬼书店**：`C&D Autumn Evening` ➔ **秋夜 (CD 枫糖香草)**，`Haunted Bookshop` ➔ **闹鬼书店 / 凶宅书店**
     - **马坝全系**：`Mixture Scottish Blend` ➔ **苏格兰混合 (马坝经典口粮)**，`Navy Flake` ➔ **马坝海航切片**，`Virginia No. 1` ➔ **V1**，`Vanilla Cream` ➔ **香草奶油**
     - **老饕名草**：`FVF (全弗吉尼亚切片)`、`睡帽 (Nightcap)`、`早安 (EMP)`、`965`、`大黄盖 (OGS)`、`李子布丁`、`小盾牌 (Escudo)`、`蓝帆船/黄帆船`、`咸狗插件 (Salty Dogs)`、`地窖青蛙`、`E家彭赞斯 (P草)`、`E家巨石阵`、`日耳曼腹黑 (RDF)`、`日耳曼布朗切片`、`大金刚 (鸟眼)`、`神雕 (秃鹰)`、`索拉尼 633/660/779` 等。
   - **风味智能归类**：自动归入 🍂 L草 (英式/拉塔基亚/巴尔干)、🌿 V草 (纯V/VaPer珀草)、🍬 调味草、🌰 白肋草 (Burley/肯塔基DFK) 等。

3. **突破 `Show More` 按钮隐藏截断机制**：
   - SP 站特价主页默认每个品牌只展示 5 款，其余隐藏在 `Show More` 之后。
   - 爬虫联动解析各品牌的专属 Sale 专区（如 `/pipe-tobacco/mac-baren/?special=sale`），拉取该品牌的**全量特价商品**，与主页去重合并，100% 杜绝漏抓。

4. **原生 IPv6 直连穿透 Cloudflare 403 封锁**：
   - 飞牛 NAS / Linux 部署采用 `network_mode: host`，直接利用家庭宽带的高信誉原生 IPv6 协议栈直连 SP 站，**免去翻墙代理，零被封风险**。

5. **全端兼容的微信服务号 Markdown 列表排版**：
   - 采用微信公众号（PushPlus 服务号）模板消息推送，单条支持高达 **40,000 字节**，彻底告别企业微信 2048 字节超长截断的痛点。
   - 严格采用 Markdown 无序列表项渲染，在手机微信、Mac/Windows 电脑版微信上均达成**“一行一个类型”**的极致工整阅读体验。

6. **智能状态流转与静默监听**：
   - 记录每款草的在售状态（`is_active_special`），已下架的特价草自动剔除，下次打折自动识别为【全新特价】；
   - 彻底关闭无意义的每日定时早报骚扰，**只有真正有新草特价、降价或缺货补货时才通知，平时绝不打扰**！

---

## 📦 项目结构

```text
sp-tobacco-monitor/
├── .env.example              # 环境变量配置模板
├── requirements.txt          # Python 核心依赖 (curl_cffi, bs4, requests, python-dotenv)
├── Dockerfile                # 基于 python:3.11-slim，内置 OCI 元数据
├── docker-compose.yml        # Docker Compose 生产编排文件 (GHCR 镜像)
├── config.py                 # 全局配置加载
├── currency.py               # 海关总署第272号令月度法定汇率引擎 (CustomsRateManager)
├── flavor_classifier.py      # 斗草口味智能分类器 (L草/V草/VaPer/调味/白肋)
├── tobacco_alias.py          # 圈内经典黑话俗称与品牌简称全量库
├── storage.py                # SQLite 本地持久化与下架状态追踪引擎
├── scraper.py                # 穿透 Cloudflare 与突破 Show More 爬虫
├── notifier.py               # 微信服务号单行列表排版通知分发引擎
└── main.py                   # 调度主程序 (默认 30 分钟轮询)
```

---

## ⚙️ 快速配置说明

在项目目录复制环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
# 1. 监控基础设置
SPECIALS_URL=https://www.smokingpipes.com/specials.cfm?specials=pipe-tobaccos
CHECK_INTERVAL_MINUTES=30

# 单月海关美元计征汇率 (海关总署第272号令：每月计征汇率=上月第三个周三央行汇率中间价)
# 可直接填入当月核定汇率（如 2026年10月为 6.7628）；若填 0 或留空，系统会自动根据海关法定算法联网获取基准日中间价
CUSTOMS_USD_RATE=6.7628

# 是否仅提醒有现货的特价斗草（true: 忽略缺货 / false: 缺货也提醒）
ONLY_IN_STOCK=false

# 首次启动程序时，是否发送当前在售全部特价草清单
NOTIFY_ON_STARTUP=true

# 每日定时汇总推送时间 (格式 HH:MM，留空则不推送；默认留空避免每日重复打扰)
DAILY_REPORT_TIME=

# 2. 微信推送配置 (PushPlus 微信服务号推送，零门槛、无字数截断)
# 微信关注公众号「push+ 推送加」(www.pushplus.plus) 复制个人 token 填入即可：
PUSHPLUS_TOKEN=你的Token
```

---

## 🐳 飞牛 NAS / Linux 部署运行方式 (推荐 GHCR 官方镜像)

### 1. 使用 Docker Compose 一键拉取启动

`docker-compose.yml` 推荐配置如下：

```yaml
services:
  sp-monitor:
    image: ghcr.io/wx2cyj/dc-jk:latest
    container_name: sp-tobacco-monitor
    restart: unless-stopped
    network_mode: host # 关键：使用 Host 网络模式，直接利用家宽公网 IPv6 直连 SP 站
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=Asia/Shanghai
```

在飞牛 NAS 终端直接执行：

```bash
# 1. 拉取最新官方镜像
docker compose pull

# 2. 后台启动容器
docker compose up -d

# 3. 查看实时运行日志
docker logs -f sp-tobacco-monitor
```

---

## 📱 微信推送实测效果预览

```markdown
# 🔥 SP站特价斗草实时清单
> 在售数量: 共 5 款 (现货: 3款 / 缺货待补: 2款)
> 汇率基准: 2026年10月海关计征汇率 (6.7628 / 基准日: 2026-09-16)
> 特价主页: 点击进入美国 SP 特价专区

---

### 【马坝 (Mac Baren)】Mixture Scottish Blend 3.5oz
* 圈内俗称: 🏷️ 苏格兰混合 (马坝经典口粮苏格兰)
* 口味类型: 🍬 调味草 (Aromatic / 调香)
* 风味特点: 香气甜美突出，室韵极佳
* 裁切规格: 碎切片 (Broken Flake)
* 特价价格: $16.28 (原价 $20.35 (8.0折))
* 折合RMB: ¥110.10
* 库存状态: ✅ 现货在售
* 活动信息: 20% Off Mac Baren Tinned Pipe Tobacco
* 直达购买: 👉 点击前往 SP 站购买

### 【马坝 (Mac Baren)】Navy Flake 3.5oz
* 圈内俗称: 🏷️ 马坝海航切片 (海军切片)
* 口味类型: 🌰 白肋草 (Burley / 肯塔基 DFK)
* 风味特点: 坚果可可香气，劲道扎实饱满
* 裁切规格: 切片 (Flake)
* 特价价格: $25.36 (原价 $31.70 (8.0折))
* 折合RMB: ¥171.50
* 库存状态: ✅ 现货在售
* 活动信息: 20% Off Mac Baren Tinned Pipe Tobacco
* 直达购买: 👉 点击前往 SP 站购买
```
