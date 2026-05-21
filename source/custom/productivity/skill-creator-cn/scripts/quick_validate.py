#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "未找到 SKILL.md"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "未找到 YAML frontmatter"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "frontmatter 格式无效"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "frontmatter 必须是 YAML 字典"
    except yaml.YAMLError as e:
        return False, f"frontmatter 中 YAML 无效：{e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"SKILL.md frontmatter 中有意外的键：{', '.join(sorted(unexpected_keys))}。"
            f"允许的属性为：{', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "frontmatter 缺少 'name'"
    if 'description' not in frontmatter:
        return False, "frontmatter 缺少 'description'"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"name 必须是字符串，实际为 {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name '{name}' 应为 kebab-case（仅小写字母、数字和连字符）"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"name '{name}' 不能以连字符开头/结尾，也不能包含连续连字符"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"name 过长（{len(name)} 字符）。上限为 64 字符。"

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"description 必须是字符串，实际为 {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "description 不能包含尖括号（< 或 >）"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"description 过长（{len(description)} 字符）。上限为 1024 字符。"

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"compatibility 必须是字符串，实际为 {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"compatibility 过长（{len(compatibility)} 字符）。上限为 500 字符。"

    return True, "Skill 校验通过！"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)