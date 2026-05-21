#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGRMS 个人全局规则管理系统 - 自动化集成测试脚本 (第二轮迭代版)
"""

import os
import sys
import json
import shutil
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pgrms import run_binding, run_touching, scan_repository
from compiler import run_compilation, get_rule_body_content
from utils import METADATA_FILE, safe_write_json, read_file_safely


class TestPGRMSSystem(unittest.TestCase):

    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.temp_project_dir = os.path.join(self.root_dir, "temp_test_project")
        self.metadata_file = METADATA_FILE

        if os.path.exists(self.temp_project_dir):
            shutil.rmtree(self.temp_project_dir)
        os.makedirs(self.temp_project_dir, exist_ok=True)

        self.metadata_backup = None
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata_backup = f.read()

    def tearDown(self):
        if os.path.exists(self.temp_project_dir):
            shutil.rmtree(self.temp_project_dir)

        if self.metadata_backup:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                f.write(self.metadata_backup)

        override_file = os.path.join(self.root_dir, "source", "registry", "cr20085361", "antigravity-", "override.md")
        if os.path.exists(override_file):
            try:
                os.remove(override_file)
            except Exception:
                pass

    def test_1_smart_binding_with_ide_preference(self):
        """测试自适应绑定与 IDE 偏好"""
        print("\n=== 测试 1：自适应智能绑定 + IDE 偏好 ===")
        pkg_data = {
            "name": "mock-frontend",
            "dependencies": {"react": "^18.2.0", "tailwindcss": "^3.0.0"}
        }
        with open(os.path.join(self.temp_project_dir, "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg_data, f, indent=2)
        os.makedirs(os.path.join(self.temp_project_dir, ".git"), exist_ok=True)

        run_binding(self.temp_project_dir, force=True, preferred_ide="windsurf")

        config_path = os.path.join(self.temp_project_dir, ".pgrms.json")
        self.assertTrue(os.path.exists(config_path))

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        tags = config_data.get("tags", [])
        self.assertIn("react", tags)
        self.assertIn("tailwind", tags)
        self.assertIn("git", tags)
        self.assertEqual(config_data.get("preferred_ide"), "windsurf")
        print(f"标签: {tags}, 首选IDE: {config_data['preferred_ide']}")
        print("=== 测试 1 通过 ===")

    def test_2_override_merge(self):
        """测试双层 override.md 追加合并功能"""
        print("\n=== 测试 2：Override.md 追加合并 ===")
        rule_dir = os.path.join(self.root_dir, "source", "registry", "cr20085361", "antigravity-")
        self.assertTrue(os.path.exists(rule_dir))

        override_file = os.path.join(rule_dir, "override.md")
        with open(override_file, "w", encoding="utf-8") as f:
            f.write("### 测试特调指令\n个人特调参数 X = True。")

        body = get_rule_body_content("source/registry/cr20085361/antigravity-")

        self.assertIn("个人专属修正 (User Personal Override)", body)
        self.assertIn("测试特调指令", body)
        print("=== 测试 2 通过 ===")

    def test_3_adaptive_filtering_now_filters_custom_rules(self):
        """测试修正后的过滤逻辑：有明确 tags 的原创规则也会被过滤"""
        print("\n=== 测试 3：原创规则也参与标签过滤 ===")
        binding_info = {
            "bound_at": "2026-05-20 13:00:00",
            "project_path": self.temp_project_dir.replace("\\", "/"),
            "tags": ["matlab"],
            "preferred_ide": "cursor"
        }
        config_path = os.path.join(self.temp_project_dir, ".pgrms.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(binding_info, f, indent=2)

        run_compilation(target="cursor", project_path=self.temp_project_dir)

        cursorrules_path = os.path.join(self.temp_project_dir, ".cursorrules")
        self.assertTrue(os.path.exists(cursorrules_path))

        with open(cursorrules_path, "r", encoding="utf-8") as f:
            content = f.read()

        # matlab 原创规则应包含
        self.assertIn("matlab", content.lower())
        # general 标签的规则（如 chinese-output-constraint）应包含
        self.assertIn("chinese-output-constraint", content)
        # frontend-design 的 tags 是 ["react","vue","css","javascript","tailwind"]，与 ["matlab"] 无交集，应被过滤
        self.assertNotIn("frontend-design", content, "frontend-design 应被过滤但未被过滤！")
        # slack-gif-creator 的 tags 是 ["general"]，应放行
        self.assertIn("slack-gif-creator", content)

        print("=== 测试 3 通过 ===")

    def test_4_touch_with_atomic_write(self):
        """测试使用频次自增 + 原子写入（应产生 .bak 备份）"""
        print("\n=== 测试 4：使用频次自增 + 原子写入 ===")
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("matlab", data["rules"])
        original_count = data["rules"]["matlab"].get("usage_count", 0)

        run_touching("matlab")

        # 验证 .bak 备份文件是否产生
        bak_file = self.metadata_file + ".bak"
        self.assertTrue(os.path.exists(bak_file), "原子写入未产生 .bak 备份文件！")

        with open(self.metadata_file, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        new_count = updated_data["rules"]["matlab"].get("usage_count", 0)
        self.assertEqual(new_count, original_count + 1)
        print(f"使用统计: {original_count} -> {new_count}, .bak 备份已生成")
        print("=== 测试 4 通过 ===")

    def test_5_ide_preference_in_compilation(self):
        """测试直推模式下 preferred_ide 仅输出单一格式"""
        print("\n=== 测试 5：IDE 偏好直推 ===")
        binding_info = {
            "bound_at": "2026-05-20 13:00:00",
            "project_path": self.temp_project_dir.replace("\\", "/"),
            "tags": ["general"],
            "preferred_ide": "windsurf"
        }
        config_path = os.path.join(self.temp_project_dir, ".pgrms.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(binding_info, f, indent=2)

        # 执行 target=all，但 preferred_ide=windsurf 应只输出 windsurf
        run_compilation(target="all", project_path=self.temp_project_dir)

        self.assertTrue(os.path.exists(os.path.join(self.temp_project_dir, ".windsurfrules")),
                        "首选 IDE 文件未生成！")
        self.assertFalse(os.path.exists(os.path.join(self.temp_project_dir, ".cursorrules")),
                         ".cursorrules 不应生成（不是首选IDE）！")
        self.assertFalse(os.path.exists(os.path.join(self.temp_project_dir, ".clinerules")),
                         ".clinerules 不应生成（不是首选IDE）！")

        print("=== 测试 5 通过 ===")

    def test_6_safe_write_json_rollback(self):
        """测试 safe_write_json 的备份机制"""
        print("\n=== 测试 6：原子写入备份验证 ===")
        test_file = os.path.join(self.temp_project_dir, "test_atomic.json")

        # 第一次写入
        safe_write_json(test_file, {"version": 1})
        self.assertTrue(os.path.exists(test_file))

        # 第二次写入应产生 .bak
        safe_write_json(test_file, {"version": 2})
        bak_file = test_file + ".bak"
        self.assertTrue(os.path.exists(bak_file))

        with open(bak_file, "r", encoding="utf-8") as f:
            bak_data = json.load(f)
        self.assertEqual(bak_data["version"], 1, ".bak 应保存上一版本内容")

        with open(test_file, "r", encoding="utf-8") as f:
            cur_data = json.load(f)
        self.assertEqual(cur_data["version"], 2, "当前文件应是最新版本")

        print("=== 测试 6 通过 ===")


if __name__ == "__main__":
    unittest.main()
