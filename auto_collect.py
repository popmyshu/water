#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麻阳信息网 - 自动采集脚本
功能：
  a) 模拟采集麻阳本地招聘信息（使用预设数据）
  b) 模拟采集租房信息
  c) 模拟采集二手交易
  d) 过滤重复内容
  e) 自动配图（使用预设图片URL）
"""

import json
import os
import datetime
import random
import hashlib
import sys

# ============ 配置 ============
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
POSTS_DIR = os.path.join(DATA_DIR, "posts")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# ============ 预设图片URL ============
PRESET_IMAGES = {
    "招聘": [
        "https://img.icons8.com/fluency/96/job.png",
        "https://img.icons8.com/color/96/hiring.png",
        "https://img.icons8.com/fluency/96/recruitment.png",
    ],
    "租房": [
        "https://img.icons8.com/color/96/real-estate.png",
        "https://img.icons8.com/fluency/96/apartment.png",
        "https://img.icons8.com/color/96/house.png",
    ],
    "二手": [
        "https://img.icons8.com/color/96/sale.png",
        "https://img.icons8.com/fluency/96/garage-sale.png",
        "https://img.icons8.com/color/96/trade.png",
    ],
    "拼车": [
        "https://img.icons8.com/color/96/car.png",
        "https://img.icons8.com/fluency/96/car-sharing.png",
        "https://img.icons8.com/color/96/taxi.png",
    ],
}

# ============ 预设采集数据（麻阳本地真实感） ============

PRESET_JOBS = [
    {
        "title": "麻阳佳惠超市招聘收银员",
        "company": "佳惠超市麻阳店",
        "position": "收银员",
        "salary": "2800-3500元/月",
        "requirement": "女性，18-40岁，会基本电脑操作",
        "address": "麻阳县高村镇建设路",
        "phone": "18774551234",
        "source": "麻阳本地招聘网",
    },
    {
        "title": "麻阳申通快递招快递员",
        "company": "麻阳申通快递",
        "position": "快递员",
        "salary": "4000-6000元/月",
        "requirement": "男性，45岁以下，有三轮车驾照",
        "address": "麻阳县高村镇五一西路",
        "phone": "18774555678",
        "source": "麻阳信息网",
    },
    {
        "title": "麻阳富华大酒店招聘服务员",
        "company": "富华大酒店",
        "position": "服务员/保洁",
        "salary": "2500-3000元/月",
        "requirement": "男女不限，50岁以下，包吃住",
        "address": "麻阳县锦和镇",
        "phone": "18774559012",
        "source": "麻阳人才市场",
    },
    {
        "title": "麻阳建筑工地招小工",
        "company": "麻阳建筑公司",
        "position": "建筑小工",
        "salary": "180-220元/天",
        "requirement": "男性，60岁以下，身体健康",
        "address": "麻阳县岩门镇",
        "phone": "18774553456",
        "source": "麻阳招聘群",
    },
    {
        "title": "麻阳移动营业厅招营业员",
        "company": "麻阳移动营业厅",
        "position": "营业员",
        "salary": "3000-4500元/月",
        "requirement": "女性，35岁以下，会电脑",
        "address": "麻阳县高村镇步行街",
        "phone": "18774557890",
        "source": "麻阳信息网",
    },
]

PRESET_RENTALS = [
    {
        "title": "麻阳高村镇两室一厅出租",
        "layout": "两室一厅",
        "area_size": 85,
        "floor": "中层（3楼）",
        "price": 800,
        "address": "麻阳县高村镇城南路12号",
        "phone": "18774552345",
        "source": "麻阳租房网",
    },
    {
        "title": "麻阳锦和镇单间配套出租",
        "layout": "单间配套",
        "area_size": 35,
        "floor": "低层（1楼）",
        "price": 350,
        "address": "麻阳县锦和镇农贸市场旁",
        "phone": "18774556789",
        "source": "麻阳58同城",
    },
    {
        "title": "麻阳江口墟镇三室两厅整租",
        "layout": "三室两厅",
        "area_size": 120,
        "floor": "高层（5楼）",
        "price": 1000,
        "address": "麻阳县江口墟镇新街",
        "phone": "18774550123",
        "source": "麻阳信息网",
    },
    {
        "title": "麻阳尧市镇门面出租",
        "layout": "门面",
        "area_size": 60,
        "floor": "1楼",
        "price": 1500,
        "address": "麻阳县尧市镇中心街",
        "phone": "18774554567",
        "source": "麻阳本地群",
    },
    {
        "title": "麻阳高村镇单间月租",
        "layout": "单间",
        "area_size": 25,
        "floor": "中层（4楼）",
        "price": 300,
        "address": "麻阳县高村镇老车站附近",
        "phone": "18774558901",
        "source": "麻阳租房网",
    },
]

PRESET_SECONDHAND = [
    {
        "title": "九成新电动车转让",
        "item": "电动车",
        "condition": "九成新",
        "orig_price": 3800,
        "price": 1800,
        "address": "麻阳县高村镇",
        "phone": "18774553456",
        "source": "麻阳二手市场",
    },
    {
        "title": "家用冰箱一台转让",
        "item": "冰箱",
        "condition": "八成新，制冷效果很好",
        "orig_price": 2500,
        "price": 800,
        "address": "麻阳县兰里镇",
        "phone": "18774557890",
        "source": "麻阳信息网",
    },
    {
        "title": "实木沙发一套便宜出",
        "item": "实木沙发",
        "condition": "七成新",
        "orig_price": 3000,
        "price": 600,
        "address": "麻阳县高村镇",
        "phone": "18774551234",
        "source": "麻阳58同城",
    },
    {
        "title": "儿童自行车一辆",
        "item": "儿童自行车",
        "condition": "几乎全新",
        "orig_price": 350,
        "price": 100,
        "address": "麻阳县吕家坪镇",
        "phone": "18774555678",
        "source": "麻阳二手群",
    },
    {
        "title": "iPhone 12 手机一部",
        "item": "iPhone 12",
        "condition": "八成新，电池健康85%",
        "orig_price": 6799,
        "price": 1800,
        "address": "麻阳县高村镇",
        "phone": "18774559012",
        "source": "麻阳信息网",
    },
]

PRESET_RIDES = [
    {
        "title": "麻阳到怀化拼车",
        "dest": "怀化",
        "date": "明天早上8点",
        "seats": 3,
        "price": 50,
        "car_type": "小轿车",
        "phone": "18774552345",
        "source": "麻阳拼车群",
    },
    {
        "title": "麻阳到长沙顺风车",
        "dest": "长沙",
        "date": "后天",
        "seats": 2,
        "price": 120,
        "car_type": "SUV",
        "phone": "18774556789",
        "source": "麻阳信息网",
    },
    {
        "title": "麻阳到凤凰古城拼车",
        "dest": "凤凰",
        "date": "今天下午2点",
        "seats": 4,
        "price": 30,
        "car_type": "面包车",
        "phone": "18774550123",
        "source": "麻阳拼车群",
    },
    {
        "title": "麻阳到铜仁拼车",
        "dest": "铜仁",
        "date": "明天下午3点",
        "seats": 3,
        "price": 60,
        "car_type": "小轿车",
        "phone": "18774554567",
        "source": "麻阳本地群",
    },
    {
        "title": "麻阳到吉首拼车",
        "dest": "吉首",
        "date": "每天早上7点",
        "seats": 4,
        "price": 40,
        "car_type": "SUV",
        "phone": "18774558901",
        "source": "麻阳信息网",
    },
]

# 已经采集过的内容ID集合（用于去重）
COLLECTED_IDS_FILE = os.path.join(DATA_DIR, "collected_ids.json")


# ============ 工具函数 ============

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] [采集] {msg}"
    log_file = os.path.join(LOGS_DIR, f"collect_{datetime.date.today().isoformat()}.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    print(log_line)


def load_json(filepath, default=None):
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
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_content_id(item):
    """根据内容生成唯一ID用于去重"""
    # 招聘
    if "title" in item:
        raw = item["title"] + item.get("phone", "")
    elif "item" in item:
        raw = item["item"] + item.get("phone", "")
    else:
        raw = str(item)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ============ 重复检测 ============

def is_duplicate(content_id, collected_ids):
    """检查内容是否已被采集"""
    return content_id in collected_ids


def load_collected_ids():
    """加载已采集的ID集合"""
    return load_json(COLLECTED_IDS_FILE, [])


def save_collected_ids(ids):
    """保存已采集的ID集合"""
    save_json(COLLECTED_IDS_FILE, ids)


# ============ 采集函数 ============

def collect_jobs():
    """采集招聘信息"""
    collected = []
    collected_ids = load_collected_ids()

    for item in PRESET_JOBS:
        content_id = get_content_id(item)
        if is_duplicate(content_id, collected_ids):
            log(f"跳过重复招聘: {item['title']}", "SKIP")
            continue

        post = {
            "id": content_id,
            "category": "招聘",
            "title": item["title"],
            "content": f"【麻阳招聘】{item['company']}招{item['position']}，工资{item['salary']}，{item['requirement']}。地址：{item['address']}，电话：{item['phone']}",
            "company": item["company"],
            "position": item["position"],
            "salary": item["salary"],
            "requirement": item["requirement"],
            "address": item["address"],
            "phone": item["phone"],
            "source": item["source"],
            "images": random.sample(PRESET_IMAGES["招聘"], 1),
            "collected_at": datetime.datetime.now().isoformat(),
            "status": "待审核",
            "is_paid": False,
        }
        collected.append(post)
        collected_ids.append(content_id)

    save_collected_ids(collected_ids)
    log(f"采集招聘: 新增{len(collected)}条")
    return collected


def collect_rentals():
    """采集租房信息"""
    collected = []
    collected_ids = load_collected_ids()

    for item in PRESET_RENTALS:
        content_id = get_content_id(item)
        if is_duplicate(content_id, collected_ids):
            log(f"跳过重复租房: {item['title']}", "SKIP")
            continue

        post = {
            "id": content_id,
            "category": "租房",
            "title": item["title"],
            "content": f"【麻阳租房】{item['title']}，{item['area_size']}平米，{item['floor']}，月租{item['price']}元。地址：{item['address']}，电话：{item['phone']}",
            "layout": item["layout"],
            "area_size": item["area_size"],
            "floor": item["floor"],
            "price": item["price"],
            "address": item["address"],
            "phone": item["phone"],
            "source": item["source"],
            "images": random.sample(PRESET_IMAGES["租房"], 1),
            "collected_at": datetime.datetime.now().isoformat(),
            "status": "待审核",
            "is_paid": False,
        }
        collected.append(post)
        collected_ids.append(content_id)

    save_collected_ids(collected_ids)
    log(f"采集租房: 新增{len(collected)}条")
    return collected


def collect_secondhand():
    """采集二手信息"""
    collected = []
    collected_ids = load_collected_ids()

    for item in PRESET_SECONDHAND:
        content_id = get_content_id(item)
        if is_duplicate(content_id, collected_ids):
            log(f"跳过重复二手: {item['title']}", "SKIP")
            continue

        post = {
            "id": content_id,
            "category": "二手",
            "title": item["title"],
            "content": f"【麻阳二手】{item['title']}，原价{item['orig_price']}元，现价{item['price']}元，{item['condition']}。地址：{item['address']}，电话：{item['phone']}",
            "item": item["item"],
            "condition": item["condition"],
            "orig_price": item["orig_price"],
            "price": item["price"],
            "address": item["address"],
            "phone": item["phone"],
            "source": item["source"],
            "images": random.sample(PRESET_IMAGES["二手"], 1),
            "collected_at": datetime.datetime.now().isoformat(),
            "status": "待审核",
            "is_paid": False,
        }
        collected.append(post)
        collected_ids.append(content_id)

    save_collected_ids(collected_ids)
    log(f"采集二手: 新增{len(collected)}条")
    return collected


def collect_rides():
    """采集拼车信息"""
    collected = []
    collected_ids = load_collected_ids()

    for item in PRESET_RIDES:
        content_id = get_content_id(item)
        if is_duplicate(content_id, collected_ids):
            log(f"跳过重复拼车: {item['title']}", "SKIP")
            continue

        post = {
            "id": content_id,
            "category": "拼车",
            "title": item["title"],
            "content": f"【麻阳拼车】{item['title']}，{item['date']}出发，剩{item['seats']}座，{item['price']}元/人，{item['car_type']}。电话：{item['phone']}",
            "dest": item["dest"],
            "depart_date": item["date"],
            "seats": item["seats"],
            "price": item["price"],
            "car_type": item["car_type"],
            "phone": item["phone"],
            "source": item["source"],
            "images": random.sample(PRESET_IMAGES["拼车"], 1),
            "collected_at": datetime.datetime.now().isoformat(),
            "status": "待审核",
            "is_paid": False,
        }
        collected.append(post)
        collected_ids.append(content_id)

    save_collected_ids(collected_ids)
    log(f"采集拼车: 新增{len(collected)}条")
    return collected


# ============ 保存采集数据 ============

def save_collected(posts, category):
    """将采集到的信息保存到当天的帖子文件"""
    today = datetime.date.today().isoformat()
    filepath = os.path.join(POSTS_DIR, f"posts_{today}.json")
    all_posts = load_json(filepath, [])
    all_posts.extend(posts)
    save_json(filepath, all_posts)
    return len(posts)


# ============ 主函数 ============

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="麻阳信息网 自动采集脚本")
    parser.add_argument("category", nargs="?", default="all",
                        choices=["all", "招聘", "租房", "二手", "拼车"],
                        help="采集类别")
    parser.add_argument("--dedup", action="store_true", default=True,
                        help="启用重复检测 (默认开启)")

    args = parser.parse_args()

    all_collected = []

    if args.category in ("all", "招聘"):
        all_collected.extend(collect_jobs())
    if args.category in ("all", "租房"):
        all_collected.extend(collect_rentals())
    if args.category in ("all", "二手"):
        all_collected.extend(collect_secondhand())
    if args.category in ("all", "拼车"):
        all_collected.extend(collect_rides())

    # 保存到当天帖子文件
    saved_count = save_collected(all_collected, args.category)

    result = {
        "category": args.category,
        "collected": len(all_collected),
        "saved": saved_count,
        "total_ids": len(load_collected_ids()),
        "time": datetime.datetime.now().isoformat(),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    log(f"采集完成: 类别={args.category}, 新增={len(all_collected)}条, 已保存={saved_count}条")

    return result


if __name__ == "__main__":
    main()
