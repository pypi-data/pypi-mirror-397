# agent-skill

## 概述

agent-skill 是一个用于定义和管理智能体【技能】的框架。它允许开发者创建、注册和调用各种技能，以增强智能代理的功能和适应性。

`一个技能（skill） = 特定领域的专业知识（prompt） + 一组可执行的操作（tools）`

一个 md 文件即可描述一个技能：

```markdown
---
name: skill_name
description: A brief description of the skill.
allowed_tools: ["tool_1", "tool_2"]
---
当情况 X 发生时，使用 tool_1 来执行操作 A。
当情况 Y 发生时，使用 tool_2 来执行操作 B。
当情况 Z 发生时，先使用 tool_1 获得结果 A'，再根据情况使用 tool_2 来执行操作 C。
```
