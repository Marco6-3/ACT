# 实验结果目录

当前主结果是 [`curriculum_hil_finetune_2026-09-02.md`](./curriculum_hil_finetune_2026-09-02.md)，记录“直接抓角预训练 → 困难状态人工接管 → 完整任务微调 → 定性成功”的课程式训练链。明日配对筛查使用 [`curriculum_screening_2026-09-03.csv`](./curriculum_screening_2026-09-03.csv)。下列多视角与抓角记录保留为历史诊断，不再是当前主线。

`result_schema.csv` 是逐次试验的最小字段模板。正式结果应一行对应一次 trial，不要只保存汇总成功率。

最终数据验收见 [`data_acceptance_2026-08-29.md`](./data_acceptance_2026-08-29.md)；E1–E3 训练与真机失败诊断见
[`e1_e3_grasp_failure_diagnosis_2026-08-29.md`](./e1_e3_grasp_failure_diagnosis_2026-08-29.md)。
E3-Orbbec 的 M=30 五布局真机结果见
[`e3_m30_screening_2026-08-29.md`](./e3_m30_screening_2026-08-29.md)。
相同布局的 M=10/M=5 配对结果与闭合 trace 诊断见
[`e3_m10_m5_screening_2026-08-29.md`](./e3_m10_m5_screening_2026-08-29.md)。
该记录也包含后台推理/重复 hold 的真机反证、无 hold 收尾 smoke、L2 光照敏感性假设，以及下一阶段
E3 正式 20 次和 E1/E2 相机对比计划。
[`data_collection_2026-08-28.md`](./data_collection_2026-08-28.md) 只保留转换过程中的历史快照，不再代表当前状态。

多视角实验应特别注意：

- `external_camera_count` 只统计外部观察相机，腕部相机单独记录；
- `source_episode_id` 保留同步视角共同来源，避免把同一示教重复计数；
- `*_visibility` 使用 `visible / partial / occluded / unknown`；
- `camera_intervention` 记录 mask、错帧替换或局部遮挡；
- `correspondence_*` 字段只有在运行对应评估时填写，否则留空；
- 自动标签必须保留 `label_source` 和人工复核状态。
- `stable_corner_grasp_success` 是当前主要任务标签：抓对双侧指定材料角，抬升 10 cm 并保持 3 s，无滑脱且未明显夹入内侧布料；
- `fold_success` 和 `full_task_success` 仅用于未来或附加实验，不能替代当前稳定抓角主要终点。

`baseline_corner_approach_test1_020000.md` 冻结了 2026-08-26 训练的只接近
角点模型。它是已归档的历史 pipeline 诊断，不是实机成功结果，也不再是当前实验门槛。

`artifacts/corner_following_analyzer_smoke` 是自动测量工具在既有遥操作 episode 上的
离线链路验证，不是 `M=30` policy 结果。`artifacts/` 已被 Git 忽略；正式摘要应在
人工真机录制完成、核对叠图后另行整理进本目录。

原始视频、机器人日志和包含个人信息或体积较大的数据不应直接提交到公开仓库，除非已经完成脱敏、许可和存储方案确认。
