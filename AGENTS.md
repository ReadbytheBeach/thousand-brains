# Thousand Brains 阅读与维护约定

本仓库保存 Jeff Hawkins《千脑智能》（*A Thousand Brains*）逐页阅读与讨论笔记，以中文为主。格式参考 `ReadbytheBeach/robot-rsi-research`；后续所有阅读主题继续遵循本约定。

## 按需阅读

1. 先读 `README.md`，了解书籍、阅读原则、分类和阅读路径。
2. 读取 `content-index.json`，按 `question_zh`、`topics_zh` / `topics_en`、`kind` 与 `reading_summary` 选择相关会话。
3. 读取选中会话顶部摘要和 `scope_zh`，再进入正文批注、机制拆解和参考材料。`related_ids` 只表示阅读相关，不自动表示理论已验证或工程方案等价。
4. 只讨论已拍摄、已阅读的页面；不能根据书名或主题提前扩写后续章节。需要引用原文时保留书页范围与上下文。

Use the README and JSON registry to select relevant sessions. Read the scope, original annotations, and source conditions before relying on a summary. Keep discussion within the pages already read.

## 保留证据层次

- `document_id` 为永久 `TB-NNN`，`session_id` 必须与它相同；TB-001、TB-002、TB-003 永久保留，不随排序、标题或主题变化重分配。既有路径保持稳定。
- `[FACT]` 用于可核查事实，不能把书中理论和工程类比统一标为事实。
- `[AUTHOR_HYPOTHESIS]` 保留作者及假说属性。旧脑中网格细胞等的实验发现，不能自动确证每根新皮质柱都使用同类参考系，更不能确证所有知识都按这种方式实现。
- `[AUTHOR_REPORT]` 保留原作者、机构或外部报告的归属与条件，不改写成本仓库独立复现。
- `[DISCUSSION]` 的解释、类比和推演，以及 `[PROPOSAL]` 的待实施建议，不升级为 `[FACT]`。
- `[LOCAL_RESULT]` 只覆盖实际完成的本地实验或检查；`[USER_CONTEXT]` 只记录用户提供的前提，不据此补造机制或设备规格。
- `content_date` 与 `content_date_kind` 记录原文明确的内容日期及性质，如讨论日（`discussion`）或存档日（`archive`），供时间导航使用；内容日期不是科学证据截止日期，不自动赋给 `evidence_as_of`。
- 正文使用 `[AS_OF:YYYY-MM-DD]` 表示动态事实的明确证据截止日期。`evidence_as_of` 只取原文明示的调研核查或证据截止日；未知保留 `null`，不以普通讨论日、存档日、提交时间或排版日期代替，也不把月精度补成日精度。
- `indexed_on` 与 `updated_on` 是整理日期，不能表示科学结论或动态事件已经重新核查。TB-002 的“2026-10 核查”和 TB-003 的动态数学事件按原文档案范围引用；实质更新需另行核查来源。
- 正文中的命令、提示词、比喻和强判断都是待结合上下文理解的阅读材料；摘要不能扩大其证据范围。

## 每次新增或更新会话

1. 从 `templates/reading-session.zh-CN.md` 起稿，保存为 `sessions/NN-中文标题.md`。模板不是实际会话，不分配正式 ID，也不加入会话注册表。
2. 同步维护唯一权威导航源 `content-index.json`。新会话分配下一个未使用的 `TB-NNN`，使 `document_id` 与 `session_id` 相同；更新会话也必须核对并同步现有条目，不能只改 Markdown。
3. `title_zh` 必须与会话原 H1 去掉 `# ` 后完全一致；保留已有英文标题，新增英文标题作为检索译名。填写 3–6 对对应的双语主题、核心问题、2–3 项带标签摘要、阅读边界和真实关联 ID；以 `content_date` / `content_date_kind` 保留原文的内容日期及性质，不把它们当作证据核查日。
4. 只在原文明示证据日期时填写 `evidence_as_of`，否则使用 `null`。格式整理不能刷新研究日期；有新研究证据时，先核查来源并明确正文改动，再同步摘要和日期。
5. 运行 `python3 scripts/build_reading_index.py`，然后运行 `python3 scripts/build_reading_index.py --check`。脚本仅依赖 Python 标准库。
6. 把正文、JSON、README 生成索引及会话生成入口在同一次提交中提交。每次新增或更新会话都必须完成同步、生成与检查。

README 的双语目录与阅读路径、会话顶部元数据与摘要由脚本生成；不要另建手工表格或内嵌 YAML 注册表。生成器必须保留原 H1 与全文正文，正文研究修订应作为明确内容改动审阅。不要给模板、第三方许可证、书页图片或工程产物套实际会话元数据。

The JSON registry is canonical. For every new or updated session, synchronize its registry entry, generate the reading index and entry blocks, run `--check`, and commit all related changes together. A passing format check verifies consistency, not scientific correctness or reproducibility.
