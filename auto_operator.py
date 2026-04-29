#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麻阳信息网 - AI自动运营主脚本
功能：
  a) 自动生成内容：根据模板生成麻阳本地招聘、租房、二手、拼车信息
  b) 反诈过滤：检测并屏蔽含欺诈关键词的内容
  c) 自动置顶：付费信息自动置顶
  d) 自动清理过期信息（30天前的自动归档）
  e) 生成每日运营报告
"""

import json
import os
import random
import datetime
import shutil
import sys
import hashlib

# ============ 配置 ============
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
POSTS_DIR = os.path.join(DATA_DIR, "posts")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
MESSAGES_DIR = os.path.join(DATA_DIR, "messages")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# 信息过期天数
EXPIRE_DAYS = 30

# 反诈关键词黑名单
BLACKLIST_KEYWORDS = [
    "手工外发", "手工活外发", "刷单", "刷信誉", "刷流水",
    "贷款", "网贷", "借贷", "无抵押贷款",
    "押金", "先交押金", "入职押金", "保证金",
    "传销", "1040", "连锁销售", "资本运作",
    "赌博", "赌场", "博彩", "时时彩",
    "兼职日结", "工资日结", "日赚", "月入过万",
    "轻松赚钱", "在家赚钱", "无需经验",
    "境外", "缅甸", "柬埔寨", "迪拜高薪",
    "投资返利", "理财高收益", "虚拟货币",
]

# ============ 内容模板 ============
TEMPLATES = {
    "招聘": [
        "【麻阳招聘】{shop}招人了！{position}，工资{salary}元/月，要求{requirement}。联系电话：{phone}",
        "【急招】麻阳{area}{position}{count}名，{salary}元/月，包吃住，有意者电联：{phone}",
        "{shop}诚聘{position}，待遇{salary}元/月，{requirement}，地址：麻阳{area}，电话：{phone}",
    ],
    "租房": [
        "【麻阳租房】{area}{layout}，{area_size}平米，{floor}，月租{price}元，拎包入住。看房电话：{phone}",
        "【出租】麻阳{area}好房，{layout}，{area_size}㎡，家电齐全，{price}元/月。联系人：{phone}",
        "{area}房东直租，{layout}{area_size}平米，{price}/月，{floor}，有{wifi_hint}，电话：{phone}",
    ],
    "二手": [
        "【麻阳二手】{item}，{condition}，原价{orig_price}元，现价{price}元，自提。联系：{phone}",
        "【转让】麻阳本地{item}一台，{condition}，价格{price}元，可小刀。电话：{phone}",
        "出{item}，用了{use_time}，{condition}，{price}元，麻阳{area}自提。联系微信同号：{phone}",
    ],
    "拼车": [
        "【麻阳拼车】{date}从麻阳到{dest}，{seat}座，{price}元/人，{car_type}，电话：{phone}",
        "【顺风车】{date}麻阳→{dest}，还剩{seat}个座位，{price}元/人，麻阳老乡联系：{phone}",
        "拼车去{dest}，{date}出发，{seat}座小车，{price}元/人，麻阳城区可接送。电话：{phone}",
    ]
}

# ============ 麻阳本地数据 ============
MAYANG_AREAS = ["高村镇", "锦和镇", "江口墟镇", "岩门镇", "兰里镇", "吕家坪镇",
                "尧市镇", "郭公坪镇", "文昌阁乡", "大桥江乡", "舒家村乡",
                "隆家堡乡", "谭家寨乡", "石羊哨乡", "板栗树乡", "兰村乡",
                "和平溪乡", "黄桑乡"]

SHOP_NAMES = ["麻阳好又多超市", "佳惠超市麻阳店", "麻阳中心商场", "麻阳家电城",
              "麻阳大药房", "麻阳移动营业厅", "麻阳电信营业厅", "麻阳联通营业厅",
              "麻阳快递站", "麻阳物流园", "麻阳建材市场", "麻阳农贸市场",
              "麻阳电商服务中心", "麻阳网络科技", "富华大酒店", "麻阳宾馆"]

POSITIONS = ["营业员", "收银员", "仓管员", "送货员", "快递员",
             "服务员", "厨师", "帮厨", "保洁", "保安",
             "销售员", "业务员", "客服", "前台", "文员",
             "司机", "搬运工", "水电工", "焊工", "普工"]

REQUIREMENTS = ["男女不限，18-45岁", "有经验者优先", "初中以上学历",
                "吃苦耐劳", "会基本电脑操作", "有驾照优先",
                "包食宿，待遇优厚", "工作时间8小时"]

PHONES = ["1877455" + str(random.randint(1000, 9999)) for _ in range(20)]

ITEMS_2ND = {
    "电动车": [800, 3000], "冰箱": [500, 2000], "洗衣机": [300, 1500],
    "空调": [500, 2500], "电视": [200, 1500], "手机": [200, 2000],
    "电脑": [500, 3000], "沙发": [200, 1000], "床": [200, 800],
    "书桌": [50, 300], "婴儿车": [50, 200], "自行车": [100, 500],
}

LAYOUTS = ["一室一厅", "两室一厅", "三室两厅", "单间配套", "两室两厅"]
FLOORS = ["低层", "中层", "高层", "电梯房"]
DESTINATIONS = ["怀化", "吉首", "凤凰", "铜仁", "长沙", "芷江", "辰溪", "泸溪"]

# ============ 工具函数 ============

def ensure_dirs():
    """确保所有数据目录存在"""
    for d in [DATA_DIR, POSTS_DIR, BACKUP_DIR, LOGS_DIR, MESSAGES_DIR, IMAGES_DIR]:
        os.makedirs(d, exist_ok=True)


def log(msg, level="INFO"):
    """写日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    log_file = os.path.join(LOGS_DIR, f"operator_{datetime.date.today().isoformat()}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    print(log_line)


def load_json(filepath, default=None):
    """安全加载JSON文件"""
    if default is None:
        default = {}
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default


def save_json(filepath, data):
    """安全保存JSON文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============ 反诈过滤 ============

def contains_scam(text):
    """检测内容是否包含欺诈/违规关键词"""
    text_lower = text.lower()
    for keyword in BLACKLIST_KEYWORDS:
        if keyword in text:
            return True, keyword
    return False, None


def filter_content(content):
    """
    过滤违规内容
    返回: (is_safe: bool, reason: str)
    """
    is_scam, keyword = contains_scam(content)
    if is_scam:
        return False, f"包含违规关键词: {keyword}"
    return True, "通过"


# ============ 内容生成 ============

def random_phone():
    """生成麻阳本地手机号"""
    return "1877455" + str(random.randint(1000, 9999))


def generate_post(category):
    """
    根据类别生成一条信息
    返回 dict
    """
    templates = TEMPLATES.get(category, [])
    if not templates:
        return None

    template = random.choice(templates)
    area = random.choice(MAYANG_AREAS)
    phone = random_phone()

    # 构建模板变量
    kwargs = {
        "phone": phone,
        "area": area,
        "date": (datetime.date.today() + datetime.timedelta(days=random.randint(0, 3))).strftime("%m月%d日"),
    }

    if category == "招聘":
        kwargs["shop"] = random.choice(SHOP_NAMES)
        kwargs["position"] = random.choice(POSITIONS)
        kwargs["salary"] = random.choice([2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000])
        kwargs["requirement"] = random.choice(REQUIREMENTS)
        kwargs["count"] = random.randint(1, 5)

    elif category == "租房":
        kwargs["layout"] = random.choice(LAYOUTS)
        kwargs["area_size"] = random.randint(40, 150)
        kwargs["price"] = random.choice([500, 600, 800, 1000, 1200, 1500])
        kwargs["floor"] = random.choice(FLOORS)
        kwargs["wifi_hint"] = random.choice(["有WiFi", "无WiFi"])

    elif category == "二手":
        item = random.choice(list(ITEMS_2ND.keys()))
        kwargs["item"] = item
        min_p, max_p = ITEMS_2ND[item]
        kwargs["price"] = random.randint(min_p, max_p)
        kwargs["orig_price"] = kwargs["price"] * random.randint(2, 4)
        kwargs["condition"] = random.choice(["九成新", "八成新", "七成新", "几乎全新", "使用正常"])
        kwargs["use_time"] = random.choice(["半年", "一年", "两年", "三个月"])

    elif category == "拼车":
        kwargs["dest"] = random.choice(DESTINATIONS)
        kwargs["seat"] = random.randint(1, 4)
        kwargs["price"] = random.choice([30, 50, 60, 80, 100, 120])
        kwargs["car_type"] = random.choice(["小轿车", "SUV", "面包车"])

    content = template.format(**kwargs)

    # 过滤
    is_safe, reason = filter_content(content)
    status = "待审核" if is_safe else "被拦截"

    post = {
        "id": generate_id(content),
        "category": category,
        "content": content,
        "area": area,
        "phone": phone,
        "created_at": datetime.datetime.now().isoformat(),
        "status": status,
        "is_paid": False,
        "is_top": False,
        "views": random.randint(10, 200),
        "filter_reason": reason if not is_safe else "",
    }
    return post


def generate_id(content):
    """根据内容生成唯一ID"""
    return hashlib.md5(content.encode()).hexdigest()[:12]


# ============ 自动发布 ============

def auto_generate(count=10):
    """
    自动生成指定数量的信息
    返回生成的帖子列表
    """
    categories = ["招聘", "租房", "二手", "拼车"]
    today_file = os.path.join(POSTS_DIR, f"posts_{datetime.date.today().isoformat()}.json")
    all_posts = load_json(today_file, [])

    new_count = 0
    scam_count = 0
    for _ in range(count):
        cat = random.choice(categories)
        post = generate_post(cat)
        if post["status"] == "被拦截":
            scam_count += 1
            # 记录拦截日志
            log(f"反诈拦截: {post['content'][:50]}... 原因: {post['filter_reason']}", "WARN")
            continue
        all_posts.append(post)
        new_count += 1

    save_json(today_file, all_posts)
    log(f"自动生成完成: 新增{new_count}条, 拦截{scam_count}条")
    return {"new": new_count, "blocked": scam_count, "total": len(all_posts)}


# ============ 自动置顶 ============

def auto_pin():
    """
    自动置顶付费信息
    付费信息 is_paid=True 自动置顶
    """
    today = datetime.date.today().isoformat()
    today_file = os.path.join(POSTS_DIR, f"posts_{today}.json")
    all_posts = load_json(today_file, [])

    pinned = 0
    for post in all_posts:
        if post.get("is_paid") and not post.get("is_top"):
            post["is_top"] = True
            post["top_until"] = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
            pinned += 1

    if pinned > 0:
        save_json(today_file, all_posts)
        log(f"自动置顶: {pinned}条信息已置顶")
    else:
        log("自动置顶: 无可置顶信息")

    return pinned


# ============ 自动清理过期 ============

def auto_cleanup():
    """
    清理过期信息（30天前自动归档）
    """
    cutoff = datetime.date.today() - datetime.timedelta(days=EXPIRE_DAYS)
    archive_file = os.path.join(BACKUP_DIR, f"archive_{cutoff.isoisoformat()}.json")
    archived_posts = []

    cleaned = 0
    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".json"):
            continue
        # 从文件名解析日期
        date_str = fname.replace("posts_", "").replace(".json", "")
        try:
            file_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue

        if file_date < cutoff:
            filepath = os.path.join(POSTS_DIR, fname)
            posts = load_json(filepath, [])
            archived_posts.extend(posts)
            # 移动到备份
            backup_path = os.path.join(BACKUP_DIR, fname)
            shutil.move(filepath, backup_path)
            cleaned += len(posts)
            log(f"归档过期信息: {fname} ({len(posts)}条)")

    # 保存归档索引
    if archived_posts:
        archive_file = os.path.join(BACKUP_DIR, f"archive_{datetime.date.today().isoformat()}.json")
        existing = load_json(archive_file, [])
        existing.extend(archived_posts)
        save_json(archive_file, existing)
        log(f"归档完成: 共{cleaned}条信息已备份到 {archive_file}")

    return cleaned


def auto_cleanup():
    """
    清理过期信息（30天前自动归档）
    """
    cutoff = datetime.date.today() - datetime.timedelta(days=EXPIRE_DAYS)
    archived_posts = []
    cleaned = 0

    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".json"):
            continue
        # 从文件名解析日期: posts_2026-04-01.json
        date_str = fname.replace("posts_", "").replace(".json", "")
        try:
            file_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue

        if file_date < cutoff:
            filepath = os.path.join(POSTS_DIR, fname)
            posts = load_json(filepath, [])
            archived_posts.extend(posts)
            # 移到备份目录
            backup_path = os.path.join(BACKUP_DIR, fname)
            shutil.move(filepath, backup_path)
            cleaned += len(posts)
            log(f"归档过期信息: {fname} ({len(posts)}条)")

    # 保存归档索引
    if archived_posts:
        archive_file = os.path.join(BACKUP_DIR, f"archive_{datetime.date.today().isoformat()}.json")
        existing = load_json(archive_file, [])
        existing.extend(archived_posts)
        save_json(archive_file, existing)
        log(f"归档完成: 共{cleaned}条信息已备份")

    return cleaned


# ============ 生成运营报告 ============

def generate_report():
    """
    生成每日运营报告
    """
    today = datetime.date.today().isoformat()
    today_file = os.path.join(POSTS_DIR, f"posts_{today}.json")
    all_posts = load_json(today_file, [])

    # 统计数据
    total = len(all_posts)
    by_category = {}
    by_status = {}
    paid_count = 0
    top_count = 0
    total_views = 0

    for post in all_posts:
        cat = post.get("category", "其他")
        status = post.get("status", "未知")
        by_category[cat] = by_category.get(cat, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        if post.get("is_paid"):
            paid_count += 1
        if post.get("is_top"):
            top_count += 1
        total_views += post.get("views", 0)

    # 读取今日拦截记录
    today_log = os.path.join(LOGS_DIR, f"operator_{today}.log")
    blocked_count = 0
    if os.path.exists(today_log):
        with open(today_log, "r", encoding="utf-8") as f:
            for line in f:
                if "反诈拦截" in line:
                    blocked_count += 1

    report = {
        "date": today,
        "generated_at": datetime.datetime.now().isoformat(),
        "summary": {
            "total_posts": total,
            "by_category": by_category,
            "by_status": by_status,
            "paid_posts": paid_count,
            "top_posts": top_count,
            "blocked_today": blocked_count,
            "total_views": total_views,
        },
        "performance": {
            "avg_views_per_post": round(total_views / total, 1) if total > 0 else 0,
            "paid_ratio": round(paid_count / total * 100, 1) if total > 0 else 0,
        }
    }

    # 保存报告
    report_file = os.path.join(LOGS_DIR, f"report_{today}.json")
    save_json(report_file, report)
    log(f"运营报告已生成: {report_file}")

    return report


# ============ 主流程 ============

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="麻阳信息网 AI自动运营脚本")
    parser.add_argument("action", nargs="?", default="all",
                        choices=["all", "generate", "pin", "cleanup", "report"],
                        help="执行的操作")
    parser.add_argument("--count", type=int, default=10,
                        help="生成信息数量 (默认10)")

    args = parser.parse_args()
    ensure_dirs()

    results = {}

    if args.action in ("all", "generate"):
        results["generate"] = auto_generate(args.count)

    if args.action in ("all", "pin"):
        results["pin"] = auto_pin()

    if args.action in ("all", "cleanup"):
        results["cleanup"] = auto_cleanup()

    if args.action in ("all", "report"):
        results["report"] = generate_report()

    # 输出JSON结果
    print("\n=== 运营结果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return results


if __name__ == "__main__":
    main()
