# Skills 使用指南

**版本**：v1.0  
**日期**：2026/01/29  
**适用平台**：Kimi CC、Claude Code、支持 Skills 的智能体平台

---

## 目录

1. [什么是 Skills](#什么是-skills)
2. [查看已安装的 Skills](#查看已安装的-skills)
3. [在 Kimi CC 中使用 Skills](#在-kimi-cc-中使用-skills)
4. [创建自定义 Skill（Deep Research 示例）](#创建自定义-skilldeep-research-示例)
5. [常见问题](#常见问题)

---

## 什么是 Skills

**Skills** 是封装了完整工作流程的**可复用能力单元**，它包含：
- **输入参数定义**（Schema）
- **内部执行逻辑**（SOP / 流程）
- **输出格式规范**

与普通工具（Tool）的区别：
- **Tool**：只提供单个动作（如"搜索一下"）
- **Skill**：封装完整流程（如"深度调研 → 多源检索 → 证据分级 → 生成报告"）

---

## 查看已安装的 Skills

### 方法 1：使用 find-skills 命令

如果你已经安装了 `find-skills`（通过 `npx skills add`），可以使用：

```bash
# 查找所有可用的 skills
npx skills find

# 搜索与特定关键词相关的 skills（如 deep research）
npx skills find deep research

# 查看某个 skill 的详细信息
npx skills info <skill-name>
```

### 方法 2：在 Kimi CC 中查看

在 `kimi cc` 终端中，可以：

```bash
# 进入 kimi cc 交互模式
kimi cc

# 在对话中询问
> 列出所有可用的 skills
> 有哪些与深度研究相关的 skills？
```

### 方法 3：查看本地 Skills 目录

Skills 通常安装在以下位置：

- **Windows**：`%USERPROFILE%\.skills\` 或 `C:\Users\<用户名>\.skills\`
- **macOS/Linux**：`~/.skills/`

你可以直接查看这些目录：

```bash
# Windows PowerShell
ls $env:USERPROFILE\.skills

# 或
dir C:\Users\<你的用户名>\.skills
```

---

## 在 Kimi CC 中使用 Skills

### 方式 1：自然语言触发（推荐）

在 `kimi cc` 对话中，直接用自然语言描述需求，模型会自动识别并调用对应的 Skill：

```bash
# 启动 kimi cc
kimi cc

# 在对话中输入
> 帮我深度研究一下"乳腺结节随访最新指南"
> 使用 deep_research skill，对"甲状腺结节管理方案"做一次全面调研
> 生成关于"肺结节筛查标准"的行业分析报告
```

**优点**：无需记忆命令，适合业务人员使用。

### 方式 2：命令行参数调用

如果 Skill 支持命令行模式，可以：

```bash
# 示例（具体命令取决于你的 kimi cc 版本）
kimi cc --skill deep_research --topic "乳腺结节随访" --depth deep --audience professional

# 或使用 JSON 参数
kimi cc --skill deep_research --params '{"topic": "乳腺结节随访", "depth": "deep"}'
```

**优点**：适合自动化脚本、批量处理。

### 方式 3：在代码/脚本中调用

如果 Skill 提供了 API 接口，可以在 Python/Node.js 等脚本中调用：

```python
# 示例（伪代码，具体取决于实现）
from kimi_skills import invoke_skill

result = invoke_skill(
    skill_name="deep_research",
    params={
        "topic": "乳腺结节随访最新指南",
        "depth": "deep",
        "audience": "professional"
    }
)

print(result["summary"])
print(result["key_findings"])
```

---

## 创建自定义 Skill（Deep Research 示例）

### 步骤 1：创建 Skill 目录结构

按照标准结构创建你的 Skill：

```bash
# 创建目录
mkdir deep-research-skill
cd deep-research-skill

# 创建标准文件结构
mkdir scripts references assets
touch SKILL.md
```

**目录结构**：
```
deep-research-skill/
├── SKILL.md          # Skill 定义文件（核心）
├── scripts/          # 执行逻辑
│   └── research.py   # 主程序
├── references/       # 知识库/模板
└── assets/           # 静态资源（Schema 等）
```

### 步骤 2：编写 SKILL.md（核心定义文件）

`SKILL.md` 是 Skill 的"说明书"，定义名称、触发方式、输入输出等：

```markdown
# Deep Research Skill

## 基本信息
- **名称**：deep_research
- **版本**：1.0.0
- **描述**：对指定主题进行深度调研，整合多源信息，生成结构化研究报告

## 触发方式
- **自然语言触发词**：
  - "对 [主题] 进行深度研究"
  - "生成 [主题] 的行业分析报告"
  - "帮我调研一下 [主题]"

## 输入参数（Input Schema）

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| topic | string | 是 | 调研主题 | "乳腺结节随访最新指南" |
| depth | enum | 否 | 调研深度 | "quick" / "deep"（默认：deep） |
| audience | enum | 否 | 目标受众 | "professional" / "general"（默认：professional） |
| output_format | enum | 否 | 输出格式 | "report" / "brief"（默认：report） |

## 输出结构（Output Schema）

```json
{
  "summary": "整体综述（300-500字）",
  "key_findings": [
    {
      "statement": "核心结论",
      "confidence": "高/中/低",
      "evidence_ids": [1, 2, 3]
    }
  ],
  "references": [
    {
      "id": 1,
      "title": "文献/指南标题",
      "source": "来源",
      "year": 2024,
      "url": "链接"
    }
  ],
  "limitations": "当前证据的局限性说明"
}
```

## 执行流程（SOP）

1. **Planner（策划）**：解析 topic，拆解为子问题
2. **Executor（执行）**：并行调用多个检索源（Google Scholar、行业数据库、官网）
3. **Reviewer（审核）**：去重、证据分级、逻辑校验
4. **Synthesizer（合成）**：生成结构化报告

## 错误处理（Fail-safe）

- 如果主要检索源失败，自动切换到备用源
- 如果检索结果不足，给出明确提示而非直接报错
- 高敏感话题自动触发人工确认流程
```

### 步骤 3：实现执行逻辑（scripts/research.py）

编写实际的执行代码（示例框架）：

```python
# scripts/research.py
"""
Deep Research Skill 的执行逻辑
"""

def run_deep_research(topic: str, depth: str = "deep", audience: str = "professional"):
    """
    执行深度调研
    
    Args:
        topic: 调研主题
        depth: 调研深度（quick/deep）
        audience: 目标受众（professional/general）
    
    Returns:
        dict: 结构化调研结果
    """
    # 1. Planner：拆解问题
    sub_questions = _plan_research(topic, depth)
    
    # 2. Executor：并行检索
    raw_data = _execute_search(sub_questions)
    
    # 3. Reviewer：清洗与验证
    validated_data = _review_and_validate(raw_data)
    
    # 4. Synthesizer：生成报告
    result = _synthesize_report(validated_data, audience)
    
    return result

def _plan_research(topic: str, depth: str) -> list:
    """拆解研究主题为子问题"""
    # 实现逻辑...
    pass

def _execute_search(questions: list) -> dict:
    """执行多源检索"""
    # 实现逻辑（调用 Tavily、Google Scholar 等）...
    pass

def _review_and_validate(data: dict) -> dict:
    """审核与验证"""
    # 实现逻辑（去重、打分、幻觉检测）...
    pass

def _synthesize_report(data: dict, audience: str) -> dict:
    """生成结构化报告"""
    # 实现逻辑...
    pass
```

### 步骤 4：注册 Skill 到 Kimi CC

将 Skill 安装到 Kimi CC 的 Skills 目录：

```bash
# 方式 1：使用 npx skills（如果支持）
npx skills add ./deep-research-skill --skill deep_research

# 方式 2：手动复制到 Skills 目录
# Windows
xcopy /E /I deep-research-skill %USERPROFILE%\.skills\deep-research-skill

# macOS/Linux
cp -r deep-research-skill ~/.skills/
```

### 步骤 5：测试 Skill

在 `kimi cc` 中测试：

```bash
kimi cc

# 测试自然语言触发
> 对"乳腺结节随访最新指南"进行深度研究

# 或使用命令行参数（如果支持）
kimi cc --skill deep_research --topic "乳腺结节随访" --depth deep
```

---

## 常见问题

### Q1：如何知道某个 Skill 是否已安装？

```bash
# 方法 1：查看目录
ls ~/.skills/  # macOS/Linux
dir %USERPROFILE%\.skills  # Windows

# 方法 2：使用 find-skills
npx skills find <skill-name>

# 方法 3：在 kimi cc 中询问
> 列出所有可用的 skills
```

### Q2：Skill 调用失败怎么办？

1. **检查 Skill 是否已正确安装**
   - 确认目录结构完整
   - 确认 `SKILL.md` 格式正确

2. **检查输入参数**
   - 确认必填参数都已提供
   - 确认参数类型符合 Schema 定义

3. **查看错误日志**
   - 在 `kimi cc` 中查看详细错误信息
   - 检查 Skill 的 `scripts/` 目录下的日志文件

### Q3：如何更新已安装的 Skill？

```bash
# 方式 1：使用 npx skills（如果支持更新命令）
npx skills update deep_research

# 方式 2：手动替换
# 先备份旧版本，然后复制新版本到 Skills 目录
```

### Q4：可以在多个平台使用同一个 Skill 吗？

**可以**，前提是：
- Skill 基于标准协议（如 MCP）封装
- 目标平台支持相同的协议
- Skill 的依赖工具（如搜索 API）在各平台都可用

### Q5：如何分享 Skill 给团队成员？

1. **方式 1：Git 仓库**
   - 将 Skill 目录推送到 Git 仓库
   - 团队成员 `git clone` 后安装到本地

2. **方式 2：打包分发**
   - 将 Skill 目录打包成 `.zip` 或 `.tar.gz`
   - 团队成员解压后安装

3. **方式 3：内部 Skill 市场**（如果有）
   - 上传到公司内部的 Skill 仓库
   - 团队成员通过统一命令安装

---

## 下一步行动

1. **熟悉现有 Skills**
   - 使用 `npx skills find` 或 `kimi cc` 查看已安装的 Skills
   - 尝试调用几个示例 Skill，熟悉使用方式

2. **开始创建 Deep Research Skill**
   - 按照上述步骤创建 `deep-research-skill` 目录结构
   - 先写 `SKILL.md` 定义文件
   - 逐步实现 `scripts/research.py` 的执行逻辑

3. **与团队对齐**
   - 确认团队统一的 Skill 规范（目录结构、命名规则等）
   - 确认在 `kimi cc` 中的标准调用方式
   - 确定 Skill 的版本管理与分发流程

---

**参考资源**：
- [Skills 官方文档](https://github.com/vercel-labs/skills)（如果适用）
- [MCP 协议文档](https://modelcontextprotocol.io/)
- 团队内部的 Skill 开发规范（如有）

