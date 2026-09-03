# 2026-09-03 五种毛巾 × 三种模型正式协议

> 状态：已执行并归档。本文件保留评估前冻结的成功定义、条件和记录规范；最终结果见 [../results/final_curriculum_evaluation_2026-09-03.md](../results/final_curriculum_evaluation_2026-09-03.md)。公开记录目前只有每个条件的 10 位成功/失败汇总编码，不能据此伪造逐 trial 元数据。

## 1. 目标与样本量

本协议在评估前的目标是：在同一固定标准布局下比较预训练模型、HIL 从头训练模型和 HIL 微调模型，观察它们对不同训练暴露与形状条件的完整毛巾折叠表现。实际测试改为随机摆放；该执行差异及其结论限制记录在第 7 节。

正式设计为 3 个模型 × 5 条毛巾 × 10 次独立重复 = 150 个正式 trial。没有策略运动冒烟测试；TS001 是当天第一条策略动作，也是第一条正式记录。

## 2. 冻结模型

| model_id | checkpoint | 训练定义 |
|---|---|---|
| base20k | /home/alpha/lerobot_train/outputs/pick_corner_orbbec_150/checkpoints/020000/pretrained_model | 蓝色正方形毛巾直接抓角预训练，20k updates；未做 HIL 微调 |
| scratch20k | /home/alpha/lerobot_train/outputs/pick_corner_hil/checkpoints/020000/pretrained_model | 随机初始化，在 HIL 的 101 条数据上训练 20k updates |
| finetune10k | /home/alpha/lerobot_train/outputs/pick_corner_finetune/checkpoints/010000/pretrained_model | 从 base20k 初始化，在同一 101 条 HIL 数据上微调 10k updates |

三者必须使用同一 runtime、相机、控制频率、prediction horizon K、executed steps M、无 temporal ensemble 设置和安全边界。开始前记录实际 M 与 runtime_config_id，全天不得按模型单独调参。

## 3. 冻结毛巾条件

| towel_id | 颜色 | 形状 | 预训练暴露 | HIL 暴露 | 解释 |
|---|---|---|---|---|---|
| T-blue-pretrain-square | 蓝 | 正方形 | 是 | 否 | 预训练内分布 |
| T-red-hil-square | 红 | 正方形 | 否 | 是 | HIL 内分布 |
| T-green-hil-square | 绿 | 正方形 | 否 | 是 | HIL 内分布 |
| T-yellow-unseen-square | 黄 | 正方形 | 否 | 否 | 未见颜色/实例，形状保持正方形 |
| T-white-unseen-rectangle | 白 | 长方形 | 否 | 否 | 未见颜色/实例，且形状变化 |

颜色、形状和具体毛巾实例均写入逐 trial 表。不要把“红/绿 HIL 暴露”误标为 base20k 已见，也不要把蓝色误标为 scratch20k 已见；表中的 pretrain_exposure 与 hil_exposure 描述的是数据来源，模型已见性需结合 model_id 判读。

## 4. 原计划的固定摆放与执行顺序

评估前的原计划是：所有 150 条都使用中心标准布局 C，不测 H1–H4 或其他偏位。第一条正式 trial 前冻结：

- 毛巾朝向、展开程度、预定目标角身份和桌面标记；
- 机器人起始关节、相机位置/标定、曝光、顶灯与窗帘状态；
- 运行配置 ID、实际 M、视频/episode 命名规则；
- 101 条 HIL 训练 episode 的固定 manifest。

执行 [../results/curriculum_screening_2026-09-03.csv](../results/curriculum_screening_2026-09-03.csv)。该表分为 10 个 block；每个 block 含全部 15 个模型 × 毛巾条件各一次。按表中顺序执行，不根据即时结果改序。每个模型在一个 block 内连续完成 5 条毛巾，随后轮换模型和毛巾顺序，以减小时间漂移及重载开销。

启动前只能核对静态配置和安全边界，不运行任何额外策略动作；不设置、不隐藏也不扣除冒烟 trial。

## 5. 成功定义与记录

full_task_success=1 必须同时满足：

1. 全程无人工接管、安全停止或超时；
2. 左右夹爪正确抓住预定毛巾角；
3. 抬升过程无滑脱；
4. 完成预定折叠动作；
5. 释放后毛巾保持目标折叠状态至少 3 s。

每条同时记录 autonomous_success、correct_both_corner_grasp、lift_success、fold_success、full_task_success、fold_corner_error_mm（可测时）、task_time_s、intervention_or_abort、failure_stage、failure_mode、视频/episode 路径与 human_verified。

失败阶段使用 approach / grasp / lift / fold / release / timeout / safety；更细的主失败代码可按 [FAILURE_TAXONOMY.md](./FAILURE_TAXONOMY.md) 填写。人工接管后的完成不改变该条失败判定。

仅在机器人动作前已经确认的摆放错误、录制损坏或外部碰撞时标为 trial_valid=0。保留原始记录、写明 invalid_reason，并追加带 rerun_of 的新行重测；统计仅使用每个计划条件的 10 条 valid 试验，绝不静默删除失败。

## 6. 报告

至少输出：

- 每个模型 × 毛巾条件的 n_success/10、成功率与 Wilson 95% CI；
- 每个模型总计 n_success/50、成功率与 Wilson 95% CI；
- 蓝色预训练内分布、红绿 HIL 内分布、黄色未见方巾、白色未见长方巾的分组汇总；
- 各阶段条件成功率、任务时间、折叠误差与失败模式；
- finetune10k − base20k、finetune10k − scratch20k 的描述性差异。

n=10/格适合给出探索性条件对比，不足以把很小的成功率差异写成确定的统计结论。黄色可支持未见方巾泛化；白色同时改变颜色、实例和形状，只能支持综合色/形状分布外泛化。

## 7. 执行结果与记录完整性

本轮按 3 × 5 × 10 矩阵得到 150 个条件化结果：`base20k` 13/50（26.0%）、`scratch20k` 10/50（20.0%）、`finetune10k` 35/50（70.0%）。`finetune10k` 在五个毛巾条件中均有更高成功数；详细的条件表、Wilson 95% CI 和结论边界见 [../results/final_curriculum_evaluation_2026-09-03.md](../results/final_curriculum_evaluation_2026-09-03.md)。

与原计划的关键差异是：实际测试时毛巾随机摆放，而不是固定在中心布局 C；未保存每次的 `dx/dy/yaw`、毛巾朝向，也没有编码位与 trial ID 的映射。因此本结果可报告为随机摆放下的总体条件成功率，但不能验证模型间位置难度是否平衡，也不能估计成功率随位置变化的关系。

协议原本要求填写逐 trial 的阶段成功、时间、折叠误差、失败模式、视频路径和人工复核。本次提交仅包含按条件聚合的 0/1 成功编码，故以下证据仍不可用：

- 每个编码位与 `TS001`–`TS150` 的对应关系；
- 抓取、抬升、折叠等阶段的具体失败归因；
- task time、fold corner error、runtime_config_id、视频和 invalid/rerun 信息。

[../results/curriculum_screening_2026-09-03.csv](../results/curriculum_screening_2026-09-03.csv) 因此保留为预生成的 run sheet，而不是被推断填充的原始结果表。条件级结果另存为 [../results/curriculum_final_evaluation_2026-09-03.csv](../results/curriculum_final_evaluation_2026-09-03.csv)。
