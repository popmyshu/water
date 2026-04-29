#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麻阳信息网 - AI自动客服脚本
功能：
  a) 根据用户留言内容自动回复
  b) 回复风格：麻阳本地口语、接地气、简洁
  c) 规则匹配：分类处理用户常见问题
"""

import json
import os
import datetime
import random
import re
import sys

# ============ 配置 ============
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MESSAGES_DIR = os.path.join(DATA_DIR, "messages")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

# ============ 回复模板（麻阳本地口语风格） ============

REPLIES = {
    "how_to_post": [
        "老乡你好！要发信息很简单嘞，点下面的链接填个表单，把内容写好发过来，我这边审核通过了就帮你发出去 👍",
        "发信息啊？简单得很！你直接把要发的内容发给我，或者填这个表单，我审核好就帮你挂上去 😊",
        "想发信息是吧？来来来，把内容发给我（文字+图片都行），我审完就给你发布，免费的！",
    ],
    "price": [
        "置顶信息30块7天，商家入驻一年才399块，实惠得很！要搞不？😎",
        "价格如下：置顶30元/7天，商家入驻399元/年。麻阳本地最划算的信息平台！",
        "老乡，置顶30块一个星期，商家入驻399一整年，算下来一天一块多钱，划算得很！",
    ],
    "is_ai": [
        "是的呢，我是AI自动运营的小助手，24小时在线，随叫随到！有啥事直接跟我说就行 😄",
        "对头，我是AI客服，全天候在线，麻阳信息网的小管家！有啥问题直接问～",
        "嘿嘿被你发现了，我是AI自动运营的，不过你放心，我反应快得很，24小时都在！",
    ],
    "outsider": [
        "不好意思哈老乡，麻阳信息网只服务麻阳本地的朋友，暂时不接待外地信息哦 🙏",
        "抱歉啦，我们只做麻阳本地的信息，外地的不接哈，理解一下～",
        "老乡对不住，我们这小平台只服务麻阳本地，外地朋友去别处问问看哈 🙏",
    ],
    "default": [
        "好嘞收到！你的消息我记下了，有需要直接说哈 😊",
        "收到收到！有什么需要帮助的尽管说，麻阳小助手在线～",
        "嗯呢，我看到了！你是要发信息还是想问啥？直接跟我说就行 👍",
        "收到你的消息了！有啥事尽管吩咐，麻阳信息网24小时为你服务 😊",
    ],
    "greeting": [
        "老乡你好！我是麻阳信息网的小助手，有啥需要帮忙的吗？发信息、找信息都行！😊",
        "你好呀！麻阳信息网AI小助手上线，有什么可以帮你的？",
        "欢迎来到麻阳信息网！我是AI小管家，发招聘、找房子、淘二手、约拼车，找我准没错！",
    ],
    "info_confirm": [
        "收到你的信息了，我这边审核一下，没问题马上帮你发布！稍等片刻哈 😊",
        "好嘞，内容收到了！我审核完就发出去，麻阳老乡的信息必须安排上！",
        "信息收到了，我先过一眼，没问题立马发布！搞好了通知你哈 👍",
    ],
    "info_rejected": [
        "老乡，你这个信息好像有点问题，我先帮你拦下来了。你看看是不是哪里写错了？重新发一个给我看看？",
        "不好意思哈，你这条信息没通过审核，可能内容有点违规。你改改再发给我试试？",
    ],
}

# ============ 意图识别关键词 ============

INTENT_PATTERNS = {
    "how_to_post": [
        r"怎么发", r"发布", r"发信息", r"发帖", r"怎么发信息",
        r"如何发布", r"我要发", r"想发", r"发个信息", r"发个帖",
        r"发布信息", r"怎么弄", r"怎么操作",
    ],
    "price": [
        r"多少钱", r"价格", r"收费", r"费用", r"怎么收费",
        r"置顶.*钱", r"多少钱.*置顶", r"入驻.*钱", r"会员.*钱",
        r"30块", r"30元", r"399", r"怎么算钱",
    ],
    "is_ai": [
        r"是人工", r"是真人", r"是机器人", r"是AI", r"是不是人",
        r"是不是AI", r"人工客服", r"转人工", r"找人工",
        r"你是不是机器人", r"真人在吗",
    ],
    "outsider": [
        r"外地", r"外省", r"不在麻阳", r"不是麻阳", r"外地人",
        r"别的地方", r"其他城市",
    ],
    "greeting": [
        r"你好", r"您好", r"在吗", r"在不在", r"hi", r"hello",
        r"嗨", r"哈喽", r"老乡", r"有人吗",
    ],
    "info_confirm": [
        r"发.*招聘", r"招人", r"招工", r"招.*人",
        r"出租", r"租房", r"出租房",
        r"转让", r"二手", r"卖.*东西",
        r"拼车", r"顺风车",
        r"帮我发", r"帮我发布",
    ],
}


def classify_intent(message):
    """
    根据用户消息识别意图
    返回意图名称列表（按匹配度排序）
    """
    message_lower = message.lower()
    matched_intents = []

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message):
                matched_intents.append(intent)
                break  # 一个意图匹配一个关键词即可

    return matched_intents


def generate_reply(message, user_id=None):
    """
    根据用户消息生成自动回复
    返回回复文本
    """
    intents = classify_intent(message)

    # 优先级处理
    # 1. 外地用户优先拒绝
    if "outsider" in intents:
        return random.choice(REPLIES["outsider"])

    # 2. 检查发送内容 - 包含具体信息内容
    if "info_confirm" in intents:
        # 检查是否包含违规内容
        from auto_operator import contains_scam
        try:
            is_scam, keyword = contains_scam(message)
            if is_scam:
                return random.choice(REPLIES["info_rejected"])
        except ImportError:
            pass
        return random.choice(REPLIES["info_confirm"])

    # 3. 按意图回复
    if "how_to_post" in intents:
        return random.choice(REPLIES["how_to_post"])

    if "price" in intents:
        return random.choice(REPLIES["price"])

    if "is_ai" in intents:
        return random.choice(REPLIES["is_ai"])

    if "greeting" in intents:
        return random.choice(REPLIES["greeting"])

    # 4. 默认回复
    return random.choice(REPLIES["default"])


# ============ 留言管理 ============

def load_messages():
    """加载所有未处理的留言"""
    today = datetime.date.today().isoformat()
    filepath = os.path.join(MESSAGES_DIR, f"messages_{today}.json")
    return load_json(filepath, [])


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


def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] [客服] {msg}"
    log_file = os.path.join(LOGS_DIR, f"service_{datetime.date.today().isoformat()}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    print(log_line)


# ============ 处理所有未回复留言 ============

def process_unreplied():
    """
    处理所有未回复的留言
    返回处理统计
    """
    messages = load_messages()
    processed = 0
    replied = []

    for msg in messages:
        if msg.get("replied"):
            continue

        user_message = msg.get("message", "")
        user_id = msg.get("user_id", "unknown")

        # 生成回复
        reply = generate_reply(user_message, user_id)

        # 标记已回复
        msg["replied"] = True
        msg["reply"] = reply
        msg["replied_at"] = datetime.datetime.now().isoformat()
        msg["reply_method"] = "auto"

        processed += 1
        replied.append({
            "user_id": user_id,
            "message": user_message[:50],
            "reply": reply[:50],
        })
        log(f"自动回复 [{user_id}]: \"{user_message[:30]}...\" → \"{reply[:30]}...\"")

    # 保存更新
    if processed > 0:
        today = datetime.date.today().isoformat()
        filepath = os.path.join(MESSAGES_DIR, f"messages_{today}.json")
        save_json(filepath, messages)

    return {
        "processed": processed,
        "total_messages": len(messages),
        "replied": replied,
    }


def add_message(user_id, message, source="weixin"):
    """
    添加一条新留言
    """
    today = datetime.date.today().isoformat()
    filepath = os.path.join(MESSAGES_DIR, f"messages_{today}.json")
    messages = load_json(filepath, [])

    msg = {
        "id": len(messages) + 1,
        "user_id": user_id,
        "message": message,
        "source": source,
        "created_at": datetime.datetime.now().isoformat(),
        "replied": False,
        "reply": "",
        "replied_at": "",
    }
    messages.append(msg)
    save_json(filepath, messages)
    log(f"新留言 [{user_id}]: {message[:50]}")
    return msg


# ============ 主函数 ============

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="麻阳信息网 AI自动客服脚本")
    parser.add_argument("action", nargs="?", default="process",
                        choices=["process", "add", "stats"],
                        help="执行操作")
    parser.add_argument("--user", default="test_user", help="用户ID")
    parser.add_argument("--message", default="你好，我想发个信息", help="留言内容")

    args = parser.parse_args()

    if args.action == "add":
        result = add_message(args.user, args.message)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "process":
        result = process_unreplied()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "stats":
        messages = load_messages()
        total = len(messages)
        replied = sum(1 for m in messages if m.get("replied"))
        unreplied = total - replied
        print(json.dumps({
            "total": total,
            "replied": replied,
            "unreplied": unreplied,
            "date": datetime.date.today().isoformat(),
        }, ensure_ascii=False, indent=2))

    return result if "result" in dir() else None


if __name__ == "__main__":
    main()
