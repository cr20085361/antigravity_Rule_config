---
description: 自动部署全局技能和配置文件
---

# 部署全局配置和技能

当需要在新电脑或者新环境上部署规则和技能时运行此工作流：

// turbo-all

1. 检查并创建技能目录：
   `New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agent\skills"`

2. 复制所有的 skills 至全局目录：
   `Copy-Item -Path "$PWD\skills\*" -Destination "$env:USERPROFILE\.agent\skills" -Recurse -Force`

3. 复制 gitignore 配置到主目录：
   `Copy-Item -Path "$PWD\.gitignore_global" -Destination "$env:USERPROFILE\.gitignore_global" -Force`

4. 生效 git 的全局忽略规则：
   `git config --global core.excludesfile "$env:USERPROFILE\.gitignore_global"`

5. 检查并创建全局规则目录：
   `New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.gemini"`

6. 复制全局规则配置 (GEMINI.md)：
   `Copy-Item -Path "$PWD\GEMINI.md" -Destination "$env:USERPROFILE\.gemini\GEMINI.md" -Force`
