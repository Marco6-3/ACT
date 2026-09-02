# ACT 毛巾折叠：课程式训练与人工接管微调

本仓库记录双臂机器人使用 ACT 完成“角点抓取 → 抬升 → 折叠毛巾”任务的实验事实、方法、结论边界和验证协议。运行代码与原始数据位于 `/home/alpha/physical_ai_runtime` 和 `/home/alpha/lerobot_train`；本仓库只保存可审计的研究记录。

## 当前结论（2026-09-02）

工程目标已经定性达成：以 2026-09-01 训练的直接抓角策略为初始能力，在抓取失败或夹爪偏位时人工接管，采集覆盖困难状态的完整任务轨迹，再从原策略继续微调。现场测试表明，微调模型可以较稳定地完成从抓起到折好的全过程，并在红、绿毛巾上均表现良好。

这可以称为一次成功的**课程式训练 / corrective HIL fine-tuning**：先学习较简单且可复用的抓角能力，再把数据预算集中到原策略易失败的状态，并学习完整任务与纠偏动作。

但当前只能下工程结论，不能下严格的因果结论。尚未完成逐 trial 成功率、未见颜色/实例测试、base 与 scratch 对照及置信区间。因此更准确的表述是：

> 分阶段训练方案已经在当前硬件、相机和毛巾任务上实现了定性闭环；“优于从零训练”“提高了多少”“颜色泛化到什么范围”由 2026-09-03 的冻结实验确认。

## 已完成的课程阶段

| 阶段 | 内容 | 已有证据 | 状态 |
|---|---|---|---|
| C0 管线与失败诊断 | 验证多相机同步、ACT 推理、夹爪闭合、动作执行和失败分类 | 2026-08-26 至 08-29 的诊断、数据验收和真机筛查 | 完成 |
| C1 直接抓角 | 100 条 Orbbec + 双腕相机示教，训练 `chunk_size=150` ACT 20k steps | `pick_corner_orbbec_150/checkpoints/020000` | 完成 |
| C2 困难状态采样 | C1 策略先运行，偏位/夹取风险出现时人工接管，完成抓取至折叠；重点覆盖偏位，含红、绿毛巾 | 原始目录 101 episodes；每条恰有一次 teleop interval | 完成，待冻结 100 条有效清单 |
| C3 继承微调 | 从 C1 checkpoint 初始化，在 HIL 数据上训练 10k steps | `pick_corner_finetune/checkpoints/010000` | 完成 |
| C4 定性整任务测试 | 无人工帮助完成抓取至折叠，多颜色表现良好 | 操作员现场观察，尚无逐 trial 台账 | 定性通过 |
| C5 定量验收 | base / scratch / fine-tune 配对比较；已见与未见颜色、中心与偏位布局 | [`docs/NEXT_EXPERIMENTS.md`](./docs/NEXT_EXPERIMENTS.md) | 2026-09-03 执行 |

## 关键资产

- C1 数据：`/home/alpha/lerobot_train/pick_corner_orbbec`，100 episodes、35,474 frames；
- C1 模型：`/home/alpha/lerobot_train/outputs/pick_corner_orbbec_150/checkpoints/020000/pretrained_model`；
- HIL 原始数据：`/home/alpha/physical_ai_runtime/data/episodes/pick_corner_hil`；
- HIL 转换数据：`/home/alpha/lerobot_train/pick_corner_hil`，当前目录为 101 episodes、54,791 frames；
- 最终微调候选：`/home/alpha/lerobot_train/outputs/pick_corner_finetune/checkpoints/010000/pretrained_model`；
- HIL 从零训练对照：`/home/alpha/lerobot_train/outputs/pick_corner_hil/checkpoints/010000/pretrained_model`。

## 过去几天最重要的学习

1. 单纯“到达毛巾附近”不等于稳定抓角，角点落点、闭合时机和双臂协调必须分层记录。
2. 更短的 executed steps 并不自动提高闭环能力；同步推理会降低动作推进吞吐。后台推理且等待期不重复发送 hold 后，执行语义才稳定。
3. 单视角原生模型明显好于把同一模型直接换到未训练相机；视角分布需要匹配。
4. 原始成功示教在左右闭合顺序上有较大时序差异，说明数据一致性重要；但在新的 HIL 路线已达到任务目标后，不再优先开发 Phase-ACT。
5. 最有效的新策略不是继续堆叠相机，而是主动收集策略最薄弱区域的数据：偏位、将要夹空和需要纠偏的状态。
6. 人工接管数据同时承担两项作用：把 rollout 拉回成功轨迹，以及把任务从“抓角”扩展到“完整折叠”。因此明天必须用对照实验区分预训练贡献、HIL 数据贡献和继承微调贡献。

## 文档导航

- [`results/curriculum_hil_finetune_2026-09-02.md`](./results/curriculum_hil_finetune_2026-09-02.md)：本轮完整事实记录与结论；
- [`docs/RESEARCH_QUESTION.md`](./docs/RESEARCH_QUESTION.md)：当前研究问题、假设与可声称边界；
- [`docs/EXPERIMENT_PROTOCOL.md`](./docs/EXPERIMENT_PROTOCOL.md)：明日定量协议和判定规则；
- [`docs/NEXT_EXPERIMENTS.md`](./docs/NEXT_EXPERIMENTS.md)：按 Gate 排序的执行清单；
- [`TODO.md`](./TODO.md)：最短操作清单；
- [`results/result_schema.csv`](./results/result_schema.csv)：完整逐 trial 字段；
- [`results/curriculum_screening_2026-09-03.csv`](./results/curriculum_screening_2026-09-03.csv)：明日 36-trial 筛查表。

多视角、旧 M 消融和 Phase-ACT 文档仍保留，用作历史证据与备选路线，不代表当前优先级。
