# 千脑智能 · Thousand Brains

Jeff Hawkins《千脑智能》（*A Thousand Brains*）读书会档案。

A bilingual reading archive for Jeff Hawkins’ *A Thousand Brains*.

## 关于这个仓库

本仓库保存《千脑智能》的逐页阅读与讨论笔记。每场讨论从书页和手写批注出发，围绕参考系、皮质柱、位姿、知识组织与智能机制展开，保留问题提出、概念校准和结论形成的完整线索。

笔记以中文为主；README 提供中英双语说明与会话索引，方便检索和后续回顾。

## About This Repository

This repository contains page-by-page reading notes and discussions of *A Thousand Brains*. Each session starts from photographed pages and handwritten annotations, then develops questions about reference frames, cortical columns, pose, knowledge organization, and the mechanisms of intelligence.

The session notes are primarily written in Chinese. This README provides bilingual documentation and a bilingual session index for retrieval and review.

## 阅读与整理原则

1. **批注驱动**：优先回应书页上的手写问题，保留原始问题意识与关键表述。
2. **机制优先**：不停留在概念定义，继续拆解状态、输入、更新规则、预测与反馈。
3. **证据分层**：区分神经科学实验事实、作者提出的理论假说，以及讨论中的类比和推演。
4. **不剧透**：只讨论已经拍摄和阅读的页面，不提前展开后续章节的结论。
5. **动态事实注明日期**：涉及实时研究与技术事件时，写明证据状态和截止日期。

## Reading and Editorial Principles

1. **Annotation-driven**: Begin with the handwritten questions on each page and preserve the original phrasing and line of inquiry.
2. **Mechanism-first**: Move beyond definitions to states, inputs, update rules, predictions, and feedback.
3. **Evidence-aware**: Distinguish experimental findings in neuroscience, the author’s theoretical hypotheses, and analogies developed during discussion.
4. **No spoilers**: Discuss only pages already photographed and read; do not preview conclusions from later chapters.
5. **Date-sensitive claims are dated**: For ongoing research and technical events, record the evidence status and its as-of date.

## 会话索引 · Session Index

| Session | 中文笔记 | English Title |
|---|---|---|
| 01 | [闭环之内皆可压缩，裁判必须在环外](sessions/01-闭环之内皆可压缩，裁判必须在环外.md) | Everything Inside a Closed Loop Can Be Compressed; the Judge Must Stand Outside It |
| 02 | [最贵的不是计算，是遗忘和重写都得便宜](sessions/02-最贵的不是计算，是遗忘和重写都得便宜.md) | The Real Cost Is Not Computation, but Making Forgetting and Rewriting Cheap |
| 03 | [思考是受约束的关系转移](sessions/03-思考是受约束的关系转移.md) | Thinking Is Constrained Movement Through Relations |

## 笔记结构 · Note Structure

每场讨论保存为 `sessions/NN-中文标题.md`。笔记通常包括：

- 原始批注与核心问题；
- 机制拆解、公式与对照表；
- 对直觉和类比的校准；
- 实验事实、理论假说与讨论推演的边界；
- 最终保留的结论与关键表述。

Each session is stored as `sessions/NN-中文标题.md`. A note typically includes:

- The original annotations and guiding questions;
- Mechanistic explanations, equations, and comparison tables;
- Calibration of intuitions and analogies;
- The boundary between empirical findings, theoretical hypotheses, and discussion-based extrapolation;
- The final conclusions and key formulations retained from the discussion.

## 模型友好约定 · Model-Friendly Conventions

为了让大语言模型（LLM）与程序稳定地解析、检索和引用笔记，新增内容遵循以下约定。

To help large language models (LLMs) and software parse, retrieve, and reuse the notes reliably, new content follows these conventions.

1. **稳定标识 · Stable identifiers**：每场会话使用 `TB-NNN` 作为永久 `session_id`；文件路径一经归档不再随意改变。Each session receives a permanent `session_id` in the form `TB-NNN`; archived paths should remain stable.
2. **双语术语 · Bilingual terminology**：关键概念首次出现时写成“中文（English）”，后文保持同一译名。Write key concepts as “中文（English）” on first use and keep the terminology consistent.
3. **原子命题 · Atomic claims**：一个句子尽量只表达一个可核查判断，明确主语、关系与对象，减少缺少指代的“它”“这个”。Keep one checkable claim per sentence where possible, with explicit subjects, relations, and objects.
4. **显式关系 · Explicit relations**：优先使用“导致、更新、绑定、预测、约束、等同于、不同于”等关系词，不把隐含推理全部留给读者。Prefer explicit relations such as causes, updates, binds, predicts, constrains, equals, and differs from.
5. **统一摘要 · Consistent summaries**：每场笔记末尾保留“主线/关键结论”，作为模型检索时的短上下文入口。End each session with a concise summary that can serve as a retrieval entry point.

### 证据标签 · Evidence Tags

- `[FACT]`：可核查的实验结果或公开事实；a verifiable experimental result or public fact.
- `[AUTHOR_HYPOTHESIS]`：作者提出但尚未得到同等程度验证的假说；a hypothesis attributed to the author.
- `[DISCUSSION]`：本次讨论形成的解释、类比或推演；an interpretation, analogy, or extrapolation developed in discussion.
- `[AS_OF:YYYY-MM-DD]`：动态事实的证据截止日期；the as-of date for a time-sensitive claim.

模型引用或总结笔记时，应保留 `session_id`、证据标签和动态事实日期；不得把 `[AUTHOR_HYPOTHESIS]` 或 `[DISCUSSION]` 改写成 `[FACT]`。

When citing or summarizing a note, a model should preserve its `session_id`, evidence tags, and as-of dates. It must not promote `[AUTHOR_HYPOTHESIS]` or `[DISCUSSION]` to `[FACT]`.

## 机器可读会话注册表 · Machine-Readable Session Registry

上方表格面向人类阅读；以下 YAML 使用相同的路径、编号和标题，供模型与程序直接解析。新增会话时，两处索引应同步更新。

The table above is optimized for human reading. The YAML below exposes the same identifiers, paths, and titles for direct machine parsing. Update both indexes when adding a session.

```yaml
schema_version: 1
book:
  title_zh: "千脑智能"
  title_en: "A Thousand Brains"
  author: "Jeff Hawkins"
  primary_language: "zh"
sessions:
  - session_id: "TB-001"
    number: 1
    status: "archived"
    language: "zh"
    path: "sessions/01-闭环之内皆可压缩，裁判必须在环外.md"
    title_zh: "闭环之内皆可压缩，裁判必须在环外"
    title_en: "Everything Inside a Closed Loop Can Be Compressed; the Judge Must Stand Outside It"
    concepts_zh: ["闭环", "压缩", "外部裁判"]
    concepts_en: ["closed loop", "compression", "external judge"]
  - session_id: "TB-002"
    number: 2
    status: "archived"
    language: "zh"
    path: "sessions/02-最贵的不是计算，是遗忘和重写都得便宜.md"
    title_zh: "最贵的不是计算，是遗忘和重写都得便宜"
    title_en: "The Real Cost Is Not Computation, but Making Forgetting and Rewriting Cheap"
    concepts_zh: ["计算", "遗忘", "重写", "状态更新"]
    concepts_en: ["computation", "forgetting", "rewriting", "state updating"]
  - session_id: "TB-003"
    number: 3
    status: "archived"
    language: "zh"
    path: "sessions/03-思考是受约束的关系转移.md"
    title_zh: "思考是受约束的关系转移"
    title_en: "Thinking Is Constrained Movement Through Relations"
    concepts_zh: ["网格细胞", "皮质柱", "位姿", "参考系", "知识组织", "大模型推理"]
    concepts_en: ["grid cells", "cortical columns", "pose", "reference frames", "knowledge organization", "LLM reasoning"]
```
