#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGRMS (个人全局规则管理系统) - 智能打分、生命周期评估与规则淘汰引擎
"""

import os
import sys
import json
import shutil
import time
import urllib.request
from datetime import datetime

from utils import (
    ROOT_DIR, METADATA_FILE, ARCHIVE_DIR,
    read_file_safely, safe_write_json,
    cli_success, cli_warning, cli_error, cli_info, cli_summary
)


def run_evaluation():
    """
    对索引库中的所有规则进行 10 分制健康打分评估并保存
    """
    t0 = time.time()
    cli_info("启动规则健康度评估引擎...")

    if not os.path.exists(METADATA_FILE):
        cli_error("索引库文件 metadata.json 不存在！请先运行 scan 命令。")
        return

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        cli_error(f"读取索引库失败: {str(e)}")
        return

    rules = data.get("rules", {})
    if not rules:
        cli_warning("当前系统无任何已注册的规则，打分中止。")
        return

    cli_info(f"检测到 {len(rules)} 条已注册规则，正在进行智能多维打分...")

    for r_id, r_info in rules.items():
        print(f"\n[评估中] 规则标识: {r_id} ({r_info['title']})")
        score = 10.0

        if r_info["source_type"] == "custom":
            # --- 个人原创规则评分逻辑 ---
            local_full_path = os.path.join(ROOT_DIR, r_info["path"], "RULE.md")
            if os.path.exists(local_full_path):
                mtime = os.path.getmtime(local_full_path)
                last_mod_date = datetime.fromtimestamp(mtime)
                days_since_mod = (datetime.now() - last_mod_date).days

                if days_since_mod > 300 and r_info.get("usage_count", 0) == 0:
                    decay = min(2.0, (days_since_mod - 300) / 100)
                    score -= decay
                    cli_warning(f"原创规则已闲置 {days_since_mod} 天未更新且无使用频次，扣减 {decay:.2f} 分。")

        else:
            # --- 第三方引入规则评分逻辑 (三维打分) ---
            reg_info = r_info.get("registry_info", {})
            repo = reg_info.get("repository", "")

            score_community = 1.5  # 默认保守分（修正：无 repo 时不再给满分）
            score_freshness = 3.0
            score_tech = 4.0

            # 1.1 社区活跃度打分
            if repo:
                try:
                    req = urllib.request.Request(
                        f"https://api.github.com/repos/{repo}",
                        headers={'User-Agent': 'PGRMS-Client-Engine'}
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        repo_data = json.loads(response.read().decode('utf-8'))

                    stars = repo_data.get("stargazers_count", 0)
                    if stars >= 1000:
                        score_community = 3.0
                    elif stars >= 500:
                        score_community = 2.5
                    elif stars >= 100:
                        score_community = 2.0
                    else:
                        score_community = 1.2
                    print(f" -> GitHub 社区指标: Star {stars}，打分: {score_community:.1f}/3.0")
                except Exception:
                    cli_warning("GitHub API 访问受限（使用降级基础分 2.2）")
                    score_community = 2.2
            else:
                cli_warning("缺少 GitHub 仓库信息，社区打分降级至 1.5/3.0")

            # 1.2 规则时效性打分
            ingest_str = reg_info.get("ingestion_date", "")
            if ingest_str:
                try:
                    ingest_date = datetime.strptime(ingest_str, "%Y-%m-%d")
                    days_since_ingest = (datetime.now() - ingest_date).days
                    if days_since_ingest > 180:
                        score_freshness = max(1.0, 3.0 - (days_since_ingest - 180) / 90)
                        print(f" -> 时效性指标: 已导入 {days_since_ingest} 天，打分: {score_freshness:.1f}/3.0")
                except:
                    pass

            # 1.3 技术栈生命力评估
            body_full_path = os.path.join(ROOT_DIR, r_info["path"], "RULE.md")
            if os.path.exists(body_full_path):
                try:
                    with open(body_full_path, "r", encoding="utf-8") as f:
                        text = f.read().lower()

                    deprecated_kws = {
                        "deprecated libraries": ["deprecated", "obsolete", "react-native-wechat", "angularjs", "python2", "python 2."],
                        "old config": ["webpack v3", "tailwind v1", "tailwind v2", "vue2", "vue 2."]
                    }

                    hits = 0
                    for category_kw, kw_list in deprecated_kws.items():
                        for kw in kw_list:
                            if kw in text:
                                hits += 1

                    if hits > 0:
                        score_tech = max(0.5, 4.0 - hits * 1.5)
                        cli_warning(f"扫描到 {hits} 处老旧技术关键字，技术打分: {score_tech:.1f}/4.0")
                    else:
                        score_tech = 4.0
                except:
                    pass

            score = score_community + score_freshness + score_tech

        # 2. 结合本地使用频次进行评分微调
        usage = r_info.get("usage_count", 0)
        if usage > 20:
            score = min(10.0, score + 1.0)
            print(f" -> 使用加分: 高频使用 ({usage} 次)，+1.0")
        elif usage > 0:
            score = min(10.0, score + 0.3)

        score = max(0.0, min(10.0, score))
        r_info["score"] = round(score, 2)
        cli_success(f"最终综合健康得分: {r_info['score']:.2f} / 10.0")

    # 原子化安全写入
    try:
        safe_write_json(METADATA_FILE, data)

        try:
            from dashboard import generate_html_dashboard
            generate_html_dashboard()
        except Exception as err:
            cli_warning(f"评估后自动刷新看板失败: {str(err)}")

        elapsed = time.time() - t0
        cli_summary(f"健康评估完成 | {len(rules)} 条规则 | 耗时 {elapsed:.2f}s")
    except Exception as e:
        cli_error(f"保存打分元数据失败: {str(e)}")


def run_pruning(auto_yes=False, dry_run=False):
    """
    规则自动淘汰与替换逻辑。
    支持 --yes 自动确认、--dry-run 仅预览。
    """
    if dry_run:
        cli_info("启动规则淘汰引擎（预览模式，不执行任何操作）...")
    elif auto_yes:
        cli_info("启动规则淘汰引擎（自动确认模式）...")
    else:
        cli_info("启动规则智能淘汰与优化替换引擎...")

    if not os.path.exists(METADATA_FILE):
        cli_error("规则索引库不存在，请先执行 scan 和 evaluate 命令。")
        return

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        cli_error(f"读取索引库失败: {str(e)}")
        return

    rules = data.get("rules", {})
    unhealthy_rules = []

    for r_id, r_info in rules.items():
        if r_info.get("score", 10.0) < 5.0:
            unhealthy_rules.append(r_info)

    if not unhealthy_rules:
        cli_success("恭喜！所有规则健康度均良好（评分 >= 5.0），无需清理。")
        return

    cli_warning(f"发现 {len(unhealthy_rules)} 条规则健康评分低于 5.0 阈值！")

    archived_count = 0
    for rule in unhealthy_rules:
        r_id = rule["name"]
        print("\n" + "-" * 80)
        print(f"🚫 亚健康规则: [{rule['category']}] {r_id} | 评分: {rule['score']:.2f}")
        print(f"📋 功能描述: {rule['description']}")
        print(f"📁 路径: {rule['path']}")
        print("-" * 80)

        if dry_run:
            cli_info("(预览模式) 该规则将被标记为归档候选。")
            continue

        should_archive = False
        if auto_yes:
            should_archive = True
            cli_info("(自动确认) 正在归档...")
        else:
            archive_confirm = input(f"是否确认将此规则归档并停用？(y/n, 默认 y): ").strip().lower()
            should_archive = archive_confirm in ["", "y", "yes"]

        if should_archive:
            src_dir = os.path.join(ROOT_DIR, rule["path"])
            dst_dir = os.path.join(ARCHIVE_DIR, rule["source_type"], os.path.basename(rule["path"]))

            os.makedirs(os.path.dirname(dst_dir), exist_ok=True)

            try:
                if os.path.exists(src_dir):
                    if os.path.exists(dst_dir):
                        shutil.rmtree(dst_dir)
                    shutil.move(src_dir, dst_dir)
                    cli_success(f"已移入归档: {dst_dir}")
                else:
                    cli_warning("未在本地路径找到规则源，可能已被手动清理。")

                data["rules"][r_id]["status"] = "disabled"
                data["rules"][r_id]["score"] = 0.0
                archived_count += 1
            except Exception as e:
                cli_error(f"移入归档失败: {str(e)}")

        # 替代方案推荐
        print(f"\n💡 推荐替代操作：")
        print(f"   python scripts/pgrms.py fetch --url <最新高星规则仓库URL> --category {rule['category']}")
        print("-" * 80 + "\n")

    if not dry_run and archived_count > 0:
        try:
            safe_write_json(METADATA_FILE, data)

            try:
                from dashboard import generate_html_dashboard
                generate_html_dashboard()
            except Exception:
                pass

            cli_summary(f"淘汰清理完成 | 归档 {archived_count} 条规则")
        except Exception as e:
            cli_error(f"同步索引库失败: {str(e)}")
    elif dry_run:
        cli_summary(f"预览完成 | {len(unhealthy_rules)} 条规则待清理（未执行任何操作）")


if __name__ == "__main__":
    run_evaluation()
