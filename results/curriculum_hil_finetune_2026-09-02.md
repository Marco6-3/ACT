# 2026-09-02 课程式 HIL 微调总结

> 收尾更新（2026-09-03）：本文件记录定量评估前的训练与定性观察。后续 150 次对照已完成，`finetune10k` 为 35/50、`base20k` 为 13/50、`scratch20k` 为 10/50；以 [final_curriculum_evaluation_2026-09-03.md](./final_curriculum_evaluation_2026-09-03.md) 为最终结论。

## 一句话结果

直接抓角预训练策略作为第一阶段能力，在其易偏位/易夹空的困难状态由人工接管并完成整套折叠，所得纠偏式完整任务数据用于继承微调后，现场测试已定性完成“抓起到折好”，且红、绿毛巾均表现良好。

## 过去几天的工作链

### 1. 管线建立与失败诊断（08-26 至 08-29）

- 建立同步外部相机与双腕相机数据、ACT 训练/推理和真机录制链路；
- 验收 100 个同步 source episodes，并生成 Orbbec、D435i1、D435i2 三个单外部视角数据集；
- 比较 E1/E2/E3 和不同 executed steps。原生模型在 `M=20` 的初筛分别为 3/10、6/10、8/10；E3 checkpoint 直接换两个未训练 D435i 视角均为 0/5；
- 发现同步推理会阻塞控制循环，短 M 会降低动作推进吞吐；改为后台推理、等待期间不重复发 hold 后，执行语义稳定；
- 离线与真机共同表明原策略已经能粗定位和闭合，但角点精度、双臂协同和示教时序仍是主要薄弱处。

### 2. 直接抓角基础能力（09-01）

- 数据：`pick_corner_orbbec`，100 episodes、35,474 frames；
- 输入：Orbbec 顶视图 + 左右腕部 RGB + 14 维机器人状态；
- 输出：14 维双臂与夹爪动作；
- ACT：ResNet-18，`K=150`，20k steps，seed 1000，batch size 4，无图像增强、无验证 split；
- checkpoint：`/home/alpha/lerobot_train/outputs/pick_corner_orbbec_150/checkpoints/020000/pretrained_model`。

### 3. 困难状态 HIL 数据采集（09-02）

- 部署上述 base20k，`K=150 / M=50 / 30 Hz`；
- 策略先自主运行，在毛巾即将夹取失败或夹爪位置偏移时由人工接管；
- 接管后完成从抓取、抬升到最终折叠的完整任务；
- 使用红、绿两种毛巾，并有意识把数据集中在夹爪偏位区域；
- 操作员口述有效采集 100 条。

磁盘核查结果：

- 原始目录为 `episode_000000..episode_000100`，共 101 条；
- 每条都有 1 个 teleop interval，证明数据确为 policy prefix + human correction；
- episode 时长 19.0–34.2 s，中位数 24.0 s；
- 人工接管开始时间中位数 4.78 s，接管持续时间中位数 12.84 s；
- 101 条顶层 `errors=[]`、`warnings=[]`，但 health 总结果均为 `WARN`，需进一步确认 profile 警告原因；
- 转换数据为 101 episodes、54,791 frames，30 fps，三个 RGB 视角、14 维 state/action；
- 颜色和布局语义没有写入 episode 元数据，当前只能依据操作员记录，不能按颜色自动统计。

因此正式数据版本尚需冻结：确认 101 条中的哪一条是试录/额外样本，或把有效数据口径正式改为 101。

### 4. 继承微调（09-02）

- 初始化：base20k；
- 数据：`/home/alpha/lerobot_train/pick_corner_hil`；
- 训练：10k steps、batch size 4、seed 1000、学习率 `1e-5`；
- checkpoint：`/home/alpha/lerobot_train/outputs/pick_corner_finetune/checkpoints/010000/pretrained_model`；
- 最终训练 loss 0.1669，L1 loss 0.1531，KLD loss 0.00138；
- 无 validation split，所以训练 loss 不能代替真机成功率。

同一 HIL 数据还保存了从零训练的 ACT checkpoint，随后用于 2026-09-03 的严格对照。

### 5. 定性真机结果

操作员测试观察：微调模型完成率很好，可以自主完成从夹起到折好；红、绿毛巾均能工作，并在多种颜色上表现出初步泛化。当前没有逐 trial 测试次数、成功数、布局和 checkpoint 对应表，故只记录为**定性通过**。

## 方法上的结论

本轮流程符合课程式学习的工程定义：

1. 先获得可复用的先修技能——直接抓角；
2. 用基础策略访问真实部署分布，而不是重新均匀遥操作；
3. 在基础策略最容易失败的偏位状态接管；
4. 接管不仅纠偏，还展示任务后半段折叠；
5. 从原权重继续学习，而非丢弃已有技能。

它也可称为 intervention-based imitation learning、DAgger 风格的数据聚合或 corrective demonstration fine-tuning。由于没有多轮反复聚合且没有严格 on-policy label 全覆盖，不应直接声称实现了标准 DAgger 算法。

## 当前能说与不能说

可以说：

- 课程式 HIL 微调在当前系统上已经实现完整任务的定性成功；
- 定向采集困难状态是比继续均匀增加成功示教更有效的工程方向；
- 红、绿毛巾的结果支持初步颜色鲁棒性观察。

暂时不能说：

- 课程学习在统计上显著优于从零训练；
- 成功率达到某个百分比；
- 已对未见颜色、材质、尺寸和褶皱实现普遍泛化；
- 提升来自预训练、困难状态采样还是更多完整任务标签中的某一项单独因素。

## 后续验证更新

原计划后实际执行为随机摆放毛巾的 3 模型 × 5 毛巾 × 10 次（150 trial）对照。汇总结果显示 `finetune10k` 35/50（70%）高于 `base20k` 13/50（26%）和 `scratch20k` 10/50（20%），从而完成本阶段的工程验证；位置未逐条记录，故不能量化位置鲁棒性或位置难度平衡。

本仓库随后收到的是每个条件的 10 位成功/失败编码，而非带视频和阶段标签的逐 trial 台账。因此最终报告给出 Wilson 区间与严格的结论边界，但不将定性观察升级为失败机制的因果解释。详见 [final_curriculum_evaluation_2026-09-03.md](./final_curriculum_evaluation_2026-09-03.md)。
