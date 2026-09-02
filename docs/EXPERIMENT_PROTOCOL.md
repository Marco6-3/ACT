# 2026-09-03 课程式毛巾折叠定量协议

## 1. 目标和边界

明日只量化三件事：最终模型的完整任务成功率、困难偏位带来的性能变化、预训练加 HIL 微调相对 base 与 HIL 从零训练的收益。所有正式 trial 必须全自主；人工接管只用于安全终止，出现即记 `autonomous_success=0`，不能接管后继续并记成功。

## 2. 冻结模型

| model_id | checkpoint | 作用 |
|---|---|---|
| `base20k` | `/home/alpha/lerobot_train/outputs/pick_corner_orbbec_150/checkpoints/020000/pretrained_model` | 课程前能力基线 |
| `scratch10k` | `/home/alpha/lerobot_train/outputs/pick_corner_hil/checkpoints/010000/pretrained_model` | 相同 HIL 数据、相同 10k updates 的从零训练对照 |
| `finetune10k` | `/home/alpha/lerobot_train/outputs/pick_corner_finetune/checkpoints/010000/pretrained_model` | 最终课程式候选 |

三者固定同一 runtime、Orbbec + 双腕相机、`K=150`、相同 executed steps、30 Hz 控制、无 temporal ensemble。测试前把实际 `M` 写入台账，全天不得按模型单独调参。

## 3. 冻结毛巾与布局

- `T-red-seen`：训练出现过的红色毛巾；
- `T-green-seen`：训练出现过的绿色毛巾；
- `T-unseen`：训练完全未出现的第三颜色，最好同时是新实例；若没有新实例，必须注明只验证颜色而非实例泛化；
- `C`：中心标准布局；
- `H1`：从今天高频接管区域中选一个固定困难偏位，贴桌面标记并记录 `dx/dy/yaw`；
- 正式最终模型扩展使用 `H2/H3/H4`，分别覆盖其余三个偏移方向，偏移量在第一条 trial 前冻结。

毛巾朝向、展开程度、目标角身份、机器人起始关节、相机位置、曝光、顶灯/窗帘和超时统一冻结。每个 trial 结束后按标记复位，不能“凭感觉摆回去”。

## 4. Gate A：36-trial 配对筛查

三个模型 × 三种毛巾 × 两种布局 × 两次重复，共 36 次。使用 [`../results/curriculum_screening_2026-09-03.csv`](../results/curriculum_screening_2026-09-03.csv) 逐条记录，按表中顺序执行，以轮换模型减少升温、光照和操作员熟练度漂移。

通过标准：

- `finetune10k` 无安全异常；
- `finetune10k` 的完整任务成功数高于 `base20k`，且优势不只来自某一种颜色；
- 困难布局 H1 上失败类型相对 base 有明显减少；
- 与 `scratch10k` 比较，至少显示同等或更好的性能；样本少时只作为筛查信号，不报告显著性。

## 5. Gate B：最终候选泛化验收

Gate A 通过后，只测试 `finetune10k`：3 种毛巾 × 5 个布局（C、H1–H4）× 3 次重复，共 45 trials。采用分块随机化，每个 block 包含全部 15 个条件一次。

45 次属于定量探索验收，不足以证明普适性。若要形成论文主结果，每格至少扩到 5 次（75 trials），并加入第二个训练 seed。

## 6. 成功定义与分层指标

主要终点 `full_task_success=1` 同时要求：

1. 全程没有人工接管、安全停止或超时；
2. 左右夹爪抓住预定毛巾角；
3. 抬升过程无滑脱；
4. 完成预定折叠动作；
5. 机器人释放后毛巾保持目标折叠状态 3 s。

在第一条 trial 前，用 5 条人工合格样例冻结折叠质量阈值：从顶视图测量目标对应角的最大误差 `fold_corner_error_mm`，取“人工可接受”的最大值作为全天阈值，测试中不得修改。没有几何测量时，只能报告人工判定的 `fold_success`，并保留盲审视频。

每条必须同时记录：

- `correct_both_corner_grasp`；
- `lift_success`；
- `fold_success`；
- `full_task_success`；
- `fold_corner_error_mm`；
- `task_time_s`；
- `intervention_or_abort`；
- `failure_stage`：`approach / grasp / lift / fold / release / timeout / safety`；
- `failure_mode`：偏左、偏右、夹空、抓错角、单侧失败、滑脱、折叠未对齐等；
- 视频/episode 路径和人工复核者。

## 7. 数据有效性

- 成功、策略失败和超时都必须保存，不得只保存成功；
- 仅摆放错误、录制损坏或外部人员碰撞可标为 `invalid`，并写原因后原条件重测；
- 测试者在盲审时只看匿名 trial ID，不看模型名；
- 颜色与毛巾实例必须写入逐 trial 台账，不能继续只放在口头记录；
- 先冻结 HIL 有效 episode 清单。当前转换目录是 101 episodes，而口述有效数据为 100 条；未解决前所有训练集描述都要同时注明两个口径。

## 8. 统计输出

每个模型、颜色和布局分别报告 `n_success/n_total` 与 Wilson 95% 置信区间。另报告：

- 模型总体完整任务成功率；
- 中心 C 与困难 H1–H4 成功率；
- 已见颜色与未见毛巾成功率；
- 各阶段条件成功率，例如 `P(fold_success | lift_success)`；
- 任务时间和折叠误差的中位数、四分位数；
- base → fine-tune 的配对成功差；
- scratch10k → finetune10k 的差异，作为预训练价值证据。

只有逐 trial 数据完整后，才使用“成功率很好”“颜色泛化”等定量表述。
