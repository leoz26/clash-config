#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 overrides.ini 里的个性化改动，打到最新的上游 metafenliu.ini 上。

上游每次更新都是「整文件覆盖」，直接改 metafenliu.ini 会被覆盖丢改动，
所以上游原版和个人改动彻底分开：

    upstream.ini     上游原版（sync.yml / sync.sh 自动下载，不要手改）
    overrides.ini    你的个性化改动（在 GitHub 网页上就能改）
    metafenliu.ini   成品 ← OpenClash「自定义模板地址」订阅这个

产物没变化时不会重写文件，避免 GitHub Actions 产生空提交。
"""
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "upstream.ini"      # 上游原版
OVR = ROOT / "overrides.ini"     # 我的改动
OUT = ROOT / "metafenliu.ini"    # 成品

UPSTREAM_URL = ("https://raw.githubusercontent.com/"
                "usbog232/clashmetadingyue/main/metafenliu.ini")

VERBS = ("set", "sub", "drop", "append", "after", "before")

HELP = """\
overrides.ini 每行一条改动，; 或 # 开头是注释。支持 6 种写法：

  set <关键字> => <新的整行>      把「包含关键字」的整行替换成新内容
  sub <关键字> => <新文本>        在「包含关键字」的行里，把关键字换成新文本
  drop <关键字>                   删除所有包含关键字的行
  append <新的整行>               在文件末尾追加一行
  after <关键字> => <新的整行>    在最后一个包含关键字的行之后插入一行
  before <关键字> => <新的整行>   在第一个包含关键字的行之前插入一行

关键字是「包含匹配」，不用写整行，写你能认出的那一小段就行。
例：
  ; 把测速地址换成 cloudflare
  sub https://www.gstatic.com/generate_204 => http://cp.cloudflare.com/generate_204
  ; 屏蔽 Disney+
  set ruleset=🟥 Adobe,[]GEOSITE,adobe => ruleset=🎬 Disney,[]GEOSITE,disney
  ; 在「漏网之鱼」之前插入一条规则
  before ruleset=🐟 漏网之鱼,[]FINAL => ruleset=DIRECT,[]GEOSITE,category-games@cn
"""


def parse_overrides(path):
    rules = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        verb, _, rest = line.partition(" ")
        verb, rest = verb.strip().lower(), rest.strip()
        if verb not in VERBS:
            sys.exit(f"[错误] overrides.ini 第 {lineno} 行：不认识的指令 “{verb}”\n{HELP}")
        if verb in ("drop", "append"):
            if not rest:
                sys.exit(f"[错误] overrides.ini 第 {lineno} 行：{verb} 后面缺内容")
            rules.append((verb, rest, None, lineno))
            continue
        key, sep, val = rest.partition("=>")
        if not sep:
            sys.exit(f"[错误] overrides.ini 第 {lineno} 行：少了 “=>”\n{HELP}")
        key, val = key.strip(), val.strip()
        if not key or not val:
            sys.exit(f"[错误] overrides.ini 第 {lineno} 行：=> 两边都不能为空\n{HELP}")
        rules.append((verb, key, val, lineno))
    return rules


def find(lines, key):
    return [i for i, l in enumerate(lines) if key in l]


def apply_rules(lines, rules):
    report = []
    for verb, key, val, lineno in rules:
        tag = f"overrides.ini:{lineno}"

        if verb == "append":
            lines.append(key)
            report.append(("ok", tag, f"末尾追加：{key[:60]}"))

        elif verb == "drop":
            hits = find(lines, key)
            if not hits:
                report.append(("miss", tag, f"drop 没找到含 “{key}” 的行"))
            else:
                for i in reversed(hits):
                    del lines[i]
                report.append(("ok", tag, f"删除 {len(hits)} 行（含 “{key}”）"))

        elif verb == "set":
            hits = find(lines, key)
            if not hits:
                report.append(("miss", tag, f"set 没找到含 “{key}” 的行"))
            else:
                for i in hits:
                    lines[i] = val
                report.append(("ok", tag, f"替换 {len(hits)} 行为：{val[:60]}"))

        elif verb == "sub":
            hits = find(lines, key)
            if not hits:
                report.append(("miss", tag, f"sub 没找到含 “{key}” 的行"))
            else:
                for i in hits:
                    lines[i] = lines[i].replace(key, val)
                report.append(("ok", tag, f"“{key}” → “{val}”（{len(hits)} 处）"))

        elif verb == "after":
            hits = find(lines, key)
            if not hits:
                report.append(("miss", tag, f"after 没找到含 “{key}” 的行"))
            else:
                lines.insert(hits[-1] + 1, val)
                report.append(("ok", tag, f"在其后插入：{val[:60]}"))

        elif verb == "before":
            hits = find(lines, key)
            if not hits:
                report.append(("miss", tag, f"before 没找到含 “{key}” 的行"))
            else:
                lines.insert(hits[0], val)
                report.append(("ok", tag, f"在其前插入：{val[:60]}"))
    return lines, report


def main():
    if not SRC.exists():
        sys.exit(f"[错误] 找不到 {SRC.name}，先跑 ./sync.sh 或等 Actions 下载上游")
    if not OVR.exists():
        sys.exit(f"[错误] 找不到 {OVR.name}")

    lines = SRC.read_text(encoding="utf-8").splitlines()
    rules = parse_overrides(OVR)
    lines, report = apply_rules(lines, rules)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    banner = [
        "; ==========================================================",
        f"; 本文件自动生成于 {stamp}，不要直接改",
        f"; 来源：{UPSTREAM_URL}",
        "; 个性化改动见 overrides.ini；改完在 GitHub 上手动跑一次 Actions",
        "; ==========================================================",
        "",
    ]
    new_text = "\n".join(banner + lines) + "\n"

    changed = not OUT.exists() or OUT.read_text(encoding="utf-8") != new_text
    if changed:
        OUT.write_text(new_text, encoding="utf-8")

    ok = [r for r in report if r[0] == "ok"]
    miss = [r for r in report if r[0] == "miss"]
    print(f"    上游原版 {len(SRC.read_text(encoding='utf-8').splitlines())} 行，"
          f"应用 {len(rules)} 条改动 → 成品 {len(lines)} 行"
          f"{'（有变化，已写入）' if changed else '（无变化，未重写）'}")
    for _, tag, msg in ok:
        print(f"      ✅ {msg}")
    for _, tag, msg in miss:
        print(f"      ⚠️  [{tag}] {msg}")
    if miss:
        print("    ─────────────────────────────────────────────")
        print(f"    ⚠️  有 {len(miss)} 条改动没匹配上：上游把这行改了或删了。")
        print("        打开 metafenliu.ini 找到对应位置，更新 overrides.ini 里的关键字。")
    # 有未生效改动时返回 1，让 Actions 显式失败（方便收到通知）
    return 1 if miss else 0


if __name__ == "__main__":
    sys.exit(main())
