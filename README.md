# Smokingpipes (美国 SP 站) 特价斗草微信监控系统

专门监控美国 Smokingpipes (SP站) 特价斗草专区的自动化监控推送系统。解决 Cloudflare 反爬、突破 `Show More` 按钮隐藏截断、自动折算单月海关汇率人民币价格、智能识别口味分类（L草、V草、调味草等），并在特价上新、降价、补货时第一时间推送到微信。

---

## 🎯 方案选型说明：为什么选择企业微信应用而非小程序？

| 对比维度 | 微信小程序 | 企业微信自建应用 / 机器人（推荐） |
| :--- | :--- | :--- |
| **主动推送能力** | ❌ 无法主动给用户推送（受限于微信“一次性订阅消息”，用户点一次才能推一条） | ✅ 随时主动推送，手机锁屏即时弹出通知 |
| **微信接收体验** | 需常驻后台或手动打开查看 | ✅ 开启“微信插件”后，**直接在个人普通微信聊天列表接收**，无需下载企微 App |
| **行业类目合规** | ❌ **烟草属于微信严重违规类目**，个人/企业小程序均无法通过审核 | ✅ 自建私有应用，仅供个人/群组内部通知使用，**无审核限制，永不封禁** |
| **开发与维护成本** | 需配置前端、域名备案、小程序服务器合规等 | ✅ 纯后端脚本，一个 Docker 容器直接跑在 VPS 或 NAS 上 |

> 💡 **核心体验**：在企业微信管理后台绑定“微信插件”（微信扫码关注）后，所有特价草卡片消息都会**直接推送到你的个人普通微信**中，点击消息即可一键直达 SP 站商品购买页面！

---

## 🚀 核心技术与特性

1. **突破 `Show More` 截断机制**：
   - SP 站特价主页默认每个品牌只展示 5 款，其余隐藏在 `Show More` 之后。
   - 本系统自动解析各特价品牌的专属 Sale 专区（如 `/pipe-tobacco/erik-stokkebye/?special=sale`），拉取该品牌的**全部特价商品**（如 20 款全量获取），并与首页去重合并，100% 杜绝漏抓。
2. **穿透 Cloudflare 403 防护**：
   - 采用 `curl_cffi` 模拟现代 Chrome TLS/JA3 指纹，避免普通爬虫被拦截。
3. **单月海关汇率折算**：
   - 支持在 `.env` 中配置固定的海关单月计征汇率（如 `7.2150`）；
   - 若未配置，自动在线拉取最新基准汇率实时换算。
4. **斗草口味智能分类**：
   - **🍂 L草 (英式调配 / English / 巴尔干 / 苏格兰)**：识别 Latakia、Oriental、Balkan 等成分与家族。
   - **🌿 V草 (弗吉尼亚纯草 / VaPer 珀草调配)**：识别纯 V、VaPer 等。
   - **🍬 调味草 (Aromatic / 调香)**：识别香草、可可、酒香调味。
   - **🌰 白肋草 / 肯塔基 (Burley / DFK)**：坚果醇厚调配。
   - **裁切规格中文化**：细切丝 (Ribbon)、切片 (Flake)、碎切片 (Broken Flake) 等。
5. **智能 Diff 告警引擎**：
   - 内置 SQLite 数据库，记录每款斗草的价格与在库历史；
   - 区分【特价上新】、【进一步降价】、【缺货补货到货】；
   - 避免重复推送同一款已在售特价草骚扰。

---

## 📦 项目结构

```text
sp-tobacco-monitor/
├── .env.example              # 配置文件模板
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像构建文件
├── docker-compose.yml        # Docker Compose 编排文件
├── config.py                 # 配置加载
├── currency.py               # 海关汇率计算器
├── flavor_classifier.py      # 口味智能分类器
├── storage.py                # SQLite 持久化与 Diff 引擎
├── scraper.py                # 穿透 Cloudflare 的 SP 爬虫
├── notifier.py               # 微信通知格式化与推送
└── main.py                   # 调度主程序
```

---

## ⚙️ 快速配置指南

复制环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```ini
# 1. 检查频率（分钟，推荐 15-30 分钟）
CHECK_INTERVAL_MINUTES=30

# 2. 单月海关美元计征汇率（如当月海关核定汇率为 7.2150；留空则自动联网获取最新汇率）
CUSTOMS_USD_RATE=7.2150

# 3. 是否仅提醒有现货的斗草（true: 忽略缺货；false: 缺货也提醒）
ONLY_IN_STOCK=false

# ================= 微信通知配置（二选一即可） =================

# 方式一：企业微信自建应用（推荐，直接推送到个人普通微信）
WECOM_CORP_ID=ww1234567890abcdef
WECOM_CORP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WECOM_AGENT_ID=1000002
WECOM_TO_USER=@all

# 如果部署在家里/公司 NAS（无固定公网 IPv4），可配置 SGW1 企微代理接口，绕过白名单限制：
WECOM_PROXY_URL=http://140.245.40.253:56789

# 方式二：企业微信群机器人（最简单，几秒钟搞定，无需任何代理与固定 IP）
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx-xxxx-xxxx

# 方式三：PushPlus 个人微信推送（备选）
PUSHPLUS_TOKEN=
```

### 如何获取企业微信自建应用凭证？
1. 电脑访问 [企业微信管理后台](https://work.weixin.qq.com/)，免费注册或登录。
2. 点击 **“应用管理”** ➔ **“自建”** ➔ **“创建应用”**：
   - 应用名称：`SP特价斗草监控`
   - 可见范围：选择你自己（或整个公司）
   - 创建后可获得 **`AgentId`** 和 **`Secret`**。
3. 点击 **“我的企业”** ➔ 最下方获取 **`企业ID (CorpId)`**。
4. **让消息直接在个人普通微信显示**：
   - 在企业微信后台点击 **“协作”** 或 **“微信插件”**，用个人微信扫描二维码关注即可。

---

## 🐳 部署运行方式

### 方式 1：Docker Compose 部署（推荐：飞牛NAS / Unraid / VPS）

#### 选项 A：使用本地源码构建运行（已验证推荐）
在项目目录下直接构建启动：
```bash
docker compose up -d --build
```

#### 选项 B：使用 GitHub Actions 自动构建的预编译镜像
如果不需要本地编译，可直接拉取由 GitHub Actions 自动发布的 GHCR 镜像：
```yaml
services:
  sp-monitor:
    image: ghcr.io/wx2cyj/dc-jk:latest
    container_name: sp-tobacco-monitor
    restart: unless-stopped
    network_mode: host
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=Asia/Shanghai
```
启动命令：
```bash
docker compose up -d
```

查看实时日志：
```bash
docker compose logs -f
```

停止容器：
```bash
docker compose down
```

### 方式 2：本地 Python 直接运行

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 单次测试运行（立即扫描一次特价并测试推送）
python main.py --once

# 后台持续监控运行
python main.py
```

---

## 📱 微信推送效果示例

```markdown
🔥 SP站特价上新通知 (第 1/3 批)
> 更新数量: 发现 25 款特价草 (本批 8 款)
> 汇率基准: 海关月度计征汇率 (7.2150)
> 监控主页: 点击查看SP特价专区

---
### [Erik Stokkebye 4th Generation] 1882 Founder's Blend 1.76oz
> 口味类型: 🍂 L草 (英式调配 / English)
> 风味特点: 以拉塔基亚与东方叶为主的经典烟熏泥炭香
> 裁切规格: 细切丝 (Ribbon)
> 特价价格: $12.46 (原价 $13.85 (9.0折))
> 折合RMB: ¥89.90
> 库存状态: ✅ 现货在售
> 👉 点击前往SP站直达购买 (带直达链接)
```
