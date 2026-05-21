# PGRMS 规则编写规格说明书 (SPEC.md)

本说明书定义了 **个人全局规则管理系统 (PGRMS)** 中规则源文件（Rule Source）的标准组织格式、文件结构与元数据声明规范。所有新编写的个人原创规则，以及从第三方拉取并标准化的规则，均必须严格遵守本规格，以便 CLI 编译引擎和智能评估引擎能够正确识别、处理与分发。

---

## 📂 1. 目录与文件组织规范

规则源文件统一放置于 `source/` 目录下，并按照以下层级进行归档：

### 1.1 个人原创规则 (`source/custom/`)
个人原创的规则必须且仅能放置于以下三个预设的功能子目录中：
* `engineering/`：用于存放编程语言（如 Python, MATLAB）、开发框架、系统设计、调试测试等纯技术性的规则约束。
* `design/`：用于存放 UI/UX 样式、前端页面设计（如 CSS 规范、Tailwind 样式）、平面设计（如 Canvas 海报）、动图创作及算法艺术类规则。
* `productivity/`：用于存放日常办公文档处理（如 Word, Excel, PDF 规则）、内部沟通写作指引、合著工作流等效率工具规则。

**目录结构示例**：
```text
source/custom/engineering/my-python-rule/
└── RULE.md
```

### 1.2 第三方引入规则 (`source/registry/`)
从外部 GitHub 仓库或其他公开源拉取的第三方规则，必须存放在以**原作者/组织 GitHub 账号**命名的二级目录中，并建立独立的规则子目录。

**目录结构示例**：
```text
source/registry/patrickjs/awesome-cursorrules/
├── RULE.md        # 标准化后的规则正文
└── metadata.yml   # 引入时的第三方元数据记录
```

---

## 📄 2. 规则源文件结构 (`RULE.md`)

每个规则子目录下必须包含一个核心正文文件 `RULE.md`。该文件由顶部的 **YAML 元数据前言 (YAML Frontmatter)** 与底部的 **Markdown 格式规则正文** 组成。

### 2.1 文件模板与格式：
```markdown
---
name: python-clean-code              # [必须] 规则的全局唯一ID（仅限小写字母、数字和连字符）
title: Python 干净代码约束           # [必须] 规则的人类可读标题
description: 编写符合 PEP 8 规范的高可读性 Python 代码的指导原则。 # [必须] 简短功能描述
category: engineering                 # [必须] 功能分类 (engineering / design / productivity)
tags: [python, clean-code, pep8]      # [必须] 规则检索标签列表
status: active                       # [可选] 规则状态 (active / disabled / deprecated)
score: 10.0                          # [自动/手动] 规则的实时健康度打分（10分制）
---

# 规则正文标题

此处编写具体的规则约束内容...
```

### 2.2 YAML 元数据字段说明：
1. **`name`** (String): 规则的唯一标识符。系统在合并编译规则（例如生成单文件 `.cursorrules`）时，以此 ID 作为前置作用域。
2. **`title`** (String): 规则的主题标题。
3. **`description`** (String): 描述该规则具体适用于什么开发或写作场景。评估引擎在通过网络搜索判别其时效性时，会使用此描述作为检索关键词的一部分。
4. **`category`** (String): 指定所属分类。必须是 `engineering`、`design` 或 `productivity` 之一。
5. **`tags`** (Array of Strings): 便于做依赖匹配与条件过滤的标签（如：`react`, `tailwind` 等）。
6. **`status`** (String): 默认为 `active`（激活状态）。若为 `disabled`（停用）或 `deprecated`（已过时），编译器在构建 dist 时将自动忽略该规则。
7. **`score`** (Float): 10 分制健康度得分。新规则初始默认为 10.0 分。

---

## ⚙️ 3. 第三方随附元数据 (`metadata.yml`)

对于放置在 `source/registry/` 下的第三方规则，除了其核心 `RULE.md` 之外，必须在同级目录下提供一个 `metadata.yml` 文件，以便评估引擎拉取社区热度并进行版本核验。

### 3.1 `metadata.yml` 模板：
```yaml
original_url: https://github.com/patrickjs/awesome-cursorrules/blob/main/rules/python.md
repository: patrickjs/awesome-cursorrules
author: patrickjs
ingestion_date: 2026-05-20
commit_hash: a1c2e3f4b5d6e7f8
```

### 3.2 字段说明：
* **`original_url`**: 该规则在互联网上的原始出处 URL。
* **`repository`**: 原 GitHub 仓库的 `owner/repo` 路径（供 GitHub API 检索 Star 数、最后更新时间使用）。
* **`author`**: 原作者的 GitHub 账号名。
* **`ingestion_date`**: 规则被拉取导入系统的本地日期。
* **`commit_hash`**: 导入时对应的 Git 提交哈希，用于检测源文件在网络上是否已发布更新。

---

## 🛡️ 4. 个人专属覆盖图层规范 (override.md)

为了支持对拉取的第三方规则进行“防覆盖”个性化定制，PGRMS 引入了双层 Override 合并机制：
1. **文件创建**：对于任何放置在 `source/registry/` 名下的第三方规则，若您需要针对其进行细节微调（例如追加个人特调指令），应在该规则目录下新建一个 `override.md`。
2. **文件命名与结构**：`override.md` 不需要带有 YAML 前言。它直接以纯 Markdown 编写。
3. **编译合并机制**：编译器在处理该规则时，会读取原始 `RULE.md`，并在尾部追加 `override.md` 的全部正文。追加时会自动补充统一的二级标题 `## 🛠️ 个人专属修正 (User Personal Override)` 进行内容分隔，确保不破坏原规则架构。

---

## 🏷️ 5. 项目技术栈标签与智能绑定规范 (Tags & Bindings)

为了支持“按需自适应绑定编译”并减小编译出的规则文件大小，项目根目录下的 `.pgrms.json` 扮演了关键的配置角色。

### 5.1 标签匹配关系表（Tags Mapping）
在执行智能自适应绑定时，系统内置了对以下标志性项目配置文件和依赖包的自动关联：
*   **前端与设计类 (design)**：
    *   匹配文件：`package.json`
    *   关联标签：`react` (含 `next`), `vue` (含 `nuxt`), `typescript`, `javascript`, `tailwind` (匹配 `tailwindcss`)
*   **软件工程与算法类 (engineering)**：
    *   匹配文件：`requirements.txt`, `Pipfile`, `pyproject.toml`
    *   关联标签：`python` (核心语言), `django`, `flask`, `fastapi`, `numpy`, `pandas`, `matplotlib`, `scipy`
    *   匹配文件：包含 `.m` 文件的文件夹
    *   关联标签：`matlab`
*   **通用与系统工具 (productivity / general)**：
    *   匹配文件：`.git`
    *   关联标签：`git`
    *   兜底匹配：若无任何上述特定配置文件，或含有大量 Markdown 文档，则自动附带 `general` 和 `productivity` 标签。

### 5.2 隐藏项目配置文件规范 (`.pgrms.json`)
由 `pgrms.py bind` 子命令自动生成并保存在被绑定的项目根目录下，其标准格式规范如下：
```json
{
  "bound_at": "2026-05-20 13:00:00",
  "project_path": "d:/AI_project/my_target_project",
  "tags": ["python", "matplotlib", "git"]
}
```
编译引擎在检测到目标项目包含该文件时，仅会将 `tags` 有交集的规则合并输出至该项目的 `.cursorrules` / `.clinerules` 等目标中。

