# K-12 Teaching Harness

本项目旨在基于 **LangChain** 与 **LangGraph**，为 Anthropic 开源的 [k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) 提供一套灵活、可复用、可评测的 Agent Harness（执行与编排测试架构）。

---

## 🎯 背景与目标

Anthropic 在 `k12-teacher-skills` 中定义并开源了用于 K-12 教师的核心 Agent Skills：
- **`k12-lesson-plan-creation`**：构建符合课程标准的高质量教学方案。
- **`k12-lesson-differentiation`**：针对不同学情（基础 / 达标 / 拓展）的分层教学设计。
- **`k12-lesson-prep`**：备课助教伙伴，推演教学核心任务并生成备课便签。
- **`k12-check-for-understanding`**：形成性评价与学生理解度检测（包含基于真实学生误区的干扰项设计与后续引导路线）。

**本仓库（k12-teaching-harness）的核心目标：**
1. **LangGraph 流程编排**：将原始 Prompt / Skill 规范抽象为基于 LangGraph 的有向图状态机（StateGraph），提供清晰的状态转移、人机协同（Human-in-the-loop）和分支控制。
2. **模型与工具解耦**：通过 LangChain 统一接口，支持多模型调用（Claude、OpenAI、开源模型等）与外部工具（标准知识图谱、检索器、评估套件）的即插即用。
3. **评测与基准测试（Evaluation Harness）**：对接 `k12-teacher-skills/evals` 评测框架，支持针对教学技能产出质量的自动化评估。

---

## 📂 项目结构

```text
k12-teaching-harness/
├── k12-teacher-skills/    # [Submodule] Anthropic 官方 k12-teacher-skills 仓库
├── src/                   # 基于 LangChain / LangGraph 的 Harness 核心实现 (待构建)
├── evals/                 # 评测与自动化测试脚本
├── .gitmodules            # Git 子模块配置
└── README.md              # 项目说明文档
```

---

## 🚀 快速开始

### 1. 克隆代码库（包含子模块）

```bash
git clone --recursive git@github.com:morebests/k12-teaching-harness.git
# 或者先 clone 后初始化子模块：
# git submodule update --init --recursive
```

### 2. 更新子模块

若需要拉取上游技能库的最新变更：

```bash
git submodule update --remote --merge
```

---

## 🔗 相关链接

- 上游技能库：[anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills)
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 官方文档](https://python.langchain.com/)
