# 下一步实验（2026-09-03）

当前状态：完整抓取到折叠已定性成功。明天不再探索新模型结构，先关闭定量证据缺口。

## Gate 0：数据与配置冻结（真机运动前）

- [ ] 从 HIL 的 101 个磁盘 episode 中确认哪 100 个是有效训练样本，输出固定 ID 清单；
- [ ] 为每条 HIL episode 补 `towel_id / color / layout_semantics / accepted`；
- [ ] 解释 101 条 `episode_health.result=WARN` 的具体 profile 原因；当前顶层 `errors/warnings` 均为空，但不能直接视为 PASS；
- [ ] 固定 `base20k / scratch10k / finetune10k` 三个 checkpoint；
- [ ] 记录实际 executed steps `M`、相机 topic、曝光/照明和安全限制；
- [ ] 贴好 C 与 H1–H4 桌面标记，记录毫米偏移和方向；
- [ ] 选定第三颜色的未见毛巾，并确认它未进入 HIL 数据。

通过证据：有效 episode 清单、三模型路径、布局照片/坐标和空白 trial 表全部保存。未通过时不开始正式计数。

## Gate 1：安全 smoke

按 `finetune10k → base20k → scratch10k` 各做 1 次中心布局低速 smoke，不计入正式成功率。确认三模型加载正确、初始动作方向正确、夹爪与工作空间安全、录制可用。

通过证据：三条 episode 均可唯一关联 checkpoint，无异常运动。任何模型加载或控制配置不同都先修复，不进入 Gate 2。

## Gate 2：36-trial 课程对照

执行 [`../results/curriculum_screening_2026-09-03.csv`](../results/curriculum_screening_2026-09-03.csv)。三模型、三毛巾、C/H1、两次重复；全自主，无人工补救。

判读：

- Fine-tune > Base：HIL 微调改善了完整任务；
- Fine-tune > Scratch10k：继承直接抓角预训练具有数据效率/性能价值；
- Fine-tune 只在红绿有效：只支持训练颜色内能力，不支持颜色泛化；
- Fine-tune 在未见毛巾也有效：支持初步跨颜色/实例泛化；
- 三者接近：不能归因于课程，检查天花板效应并增加更困难布局；
- 三者都差：先核对训练/测试配置漂移，不继续扩模型。

## Gate 3：45-trial 最终候选验收

只有 Gate 2 安全且 `finetune10k` 表现最好时执行：3 毛巾 × C/H1/H2/H3/H4 × 3 repeats。输出总体、颜色、布局、阶段成功率和 Wilson 95% CI。

## Gate 4：结论冻结

- [ ] 将逐 trial CSV、汇总表和失败视频索引写入 `results/`；
- [ ] 明确区分工程结论、探索性统计和因果结论；
- [ ] 若课程优势成立，将多视角和 Phase-ACT 标为 deferred；
- [ ] 若优势不成立，再根据第一失败 Gate 选择补数据、对齐训练预算或恢复旧研究路线。

完整判定规则见 [`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md)。
