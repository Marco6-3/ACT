# 实验结果目录

当前主结果是 [final_curriculum_evaluation_2026-09-03.md](./final_curriculum_evaluation_2026-09-03.md)：它冻结本阶段的 150 次条件化评估结论，并给出原始 0/1 汇总编码、Wilson 95% CI、可支持的结论和限制。

[curriculum_final_evaluation_2026-09-03.csv](./curriculum_final_evaluation_2026-09-03.csv) 是与报告对应的机器可读条件汇总：3 个模型 × 5 条毛巾，每个条件 10 次。`success_code` 中的每一位对应一次成功（1）或失败（0）。它保留了操作者提交的条件级编码，但没有可靠的 trial ID、阶段标签、视频路径或运行时元数据映射；因此不能把它误作完整逐 trial 原始台账，也不能从中反推失败阶段、任务时间或折叠误差。

[curriculum_screening_2026-09-03.csv](./curriculum_screening_2026-09-03.csv) 保留为评估前生成的 150 行 run sheet。它记录随机化测试顺序和条件定义，其中的中心布局 C 是原计划字段；实际测试改为随机摆放、且未保存位置元数据。该表没有用本次汇总编码回填，避免在缺少“编码位置 ↔ TS 编号”对应关系时虚构逐条实验记录。

与阶段收尾相关的记录：

- [curriculum_hil_finetune_2026-09-02.md](./curriculum_hil_finetune_2026-09-02.md)：HIL 数据采集、微调与定性结果；
- [../docs/EXPERIMENT_PROTOCOL.md](../docs/EXPERIMENT_PROTOCOL.md)：最终评估的预定义成功标准和结论边界；
- [../docs/NEXT_EXPERIMENTS.md](../docs/NEXT_EXPERIMENTS.md)：已完成测试矩阵的归档说明。

历史证据仍可用于回顾问题定位：

- [data_acceptance_2026-08-29.md](./data_acceptance_2026-08-29.md)：训练数据验收；
- [e1_e3_grasp_failure_diagnosis_2026-08-29.md](./e1_e3_grasp_failure_diagnosis_2026-08-29.md)：E1–E3 训练与真机失败诊断；
- [e3_m30_screening_2026-08-29.md](./e3_m30_screening_2026-08-29.md)：E3-Orbbec 的 M=30 五布局筛查；
- [e3_m10_m5_screening_2026-08-29.md](./e3_m10_m5_screening_2026-08-29.md)：M=10/M=5 与控制执行语义诊断。

原始视频、机器人日志和包含个人信息或体积较大的数据不应直接提交到公开仓库，除非已经完成脱敏、许可和存储方案确认。
