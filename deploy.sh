#!/usr/bin/env bash
# PGRMS (个人全局规则管理系统) - macOS/Linux 平台一键自动部署脚本
# 请在终端执行 'chmod +x deploy.sh && ./deploy.sh' 来生效配置

set -e

# 定义终端控制台色彩输出
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色恢复

echo -e "${CYAN}=========================================================================${NC}"
echo -e "${CYAN}🚀 开始执行 PGRMS 个人全局规则管理系统 - 一键自动化部署 (macOS/Linux)${NC}"
echo -e "${CYAN}=========================================================================${NC}"

# 1. 规则库扫描重建索引
echo -e "\n${YELLOW}[步骤 1/5] 正在启动本地通用规则库扫描...${NC}"
if command -v python3 &>/dev/null; then
    python3 scripts/pgrms.py scan
elif command -v python &>/dev/null; then
    python scripts/pgrms.py scan
else
    echo -e "${RED}错误：未找到 Python 运行环境，无法运行 CLI 引擎！${NC}"
    exit 1
fi

# 2. 规则多目标全平台编译
echo -e "\n${YELLOW}[步骤 2/5] 正在启动多主流 IDE 规则适配编译器...${NC}"
if command -v python3 &>/dev/null; then
    python3 scripts/pgrms.py compile --target all
else
    python scripts/pgrms.py compile --target all
fi

# 3. 部署 Antigravity 全局技能 (Skills)
echo -e "\n${YELLOW}[步骤 3/5] 正在同步部署 Antigravity 全局智能技能包...${NC}"
GLOBAL_SKILL_DIRS=(
    "$HOME/.agent/skills"
    "$HOME/.agents/skills"
)

# 强力拷贝覆盖编译好的技能
if [ -d "dist/antigravity/skills" ]; then
    for GLOBAL_SKILLS_DIR in "${GLOBAL_SKILL_DIRS[@]}"; do
        if [ ! -d "$GLOBAL_SKILLS_DIR" ]; then
            echo -e " -> 未检测到技能配置目录，正在为您自动创建: $GLOBAL_SKILLS_DIR"
            mkdir -p "$GLOBAL_SKILLS_DIR"
        fi
        cp -r dist/antigravity/skills/* "$GLOBAL_SKILLS_DIR/"
        echo -e "${GREEN} -> 成功！已将所有已编译激活的全局技能复制覆盖至: $GLOBAL_SKILLS_DIR${NC}"
    done
else
    echo -e "${RED} -> 错误：未找到编译好的 Antigravity 全局技能，请确认编译是否成功。${NC}"
fi

# 4. 部署 Git 全局忽略配置文件 (.gitignore_global)
echo -e "\n${YELLOW}[步骤 4/5] 正在部署 Git 全局忽略配置文件...${NC}"
GLOBAL_GIT_IGNORE="$HOME/.gitignore_global"

if [ -f ".gitignore_global" ]; then
    cp ".gitignore_global" "$GLOBAL_GIT_IGNORE"
    echo -e "${GREEN} -> 成功！已将 .gitignore_global 复制并覆盖至: $GLOBAL_GIT_IGNORE${NC}"
    
    # 运行 Git 命令使其在全局生效
    echo -e " -> 正在将该忽略规则配置注入您的全局 Git 环境中..."
    git config --global core.excludesfile "$HOME/.gitignore_global"
    echo -e "${GREEN} -> 成功！全局 Git 忽略规则已成功激活生效。${NC}"
else
    echo -e "${RED} -> 未找到 .gitignore_global 配置文件，跳过此步骤。${NC}"
fi

# 5. 部署全局对话规则配置 (GEMINI.md)
echo -e "\n${YELLOW}[步骤 5/5] 正在部署全局 AI 对话约束规则 (GEMINI.md)...${NC}"
GLOBAL_GEMINI_DIR="$HOME/.gemini"
GLOBAL_GEMINI_FILE="$GLOBAL_GEMINI_DIR/GEMINI.md"

# 确认并创建 .gemini 目录
if [ ! -d "$GLOBAL_GEMINI_DIR" ]; then
    mkdir -p "$GLOBAL_GEMINI_DIR"
fi

if [ -f "GEMINI.md" ]; then
    cp "GEMINI.md" "$GLOBAL_GEMINI_FILE"
    echo -e "${GREEN} -> 成功！已将全局对话规则复制覆盖至: $GLOBAL_GEMINI_FILE${NC}"
    echo -e "${GREEN} -> 您的全局 AI 交互（包括中英文偏好、思考过程文字等约束）已成功生效！${NC}"
else
    echo -e "${RED} -> 未找到 GEMINI.md 配置文件，跳过此步骤。${NC}"
fi

if command -v python3 &>/dev/null; then
    python3 scripts/pgrms.py sync-vscode
else
    python scripts/pgrms.py sync-vscode
fi

echo -e "\n${CYAN}=========================================================================${NC}"
echo -e "${GREEN}🎉 恭喜！PGRMS 全局规则与技能部署圆满成功！${NC}"
echo -e "所有的主流 IDE 规则适配成果已就绪，位于 dist/ 目录下："
echo -e "  👉 Cursor 专属规则位于: dist/cursor/.cursorrules"
echo -e "  👉 Windsurf 专属规则位于: dist/windsurf/.windsurfrules"
echo -e "  👉 Cline 专属规则位于: dist/cline/.clinerules"
echo -e "  👉 规则智能看板已同步刷新，可直接双击项目根目录下的: dashboard.html"
echo -e "=========================================================================${NC}"
