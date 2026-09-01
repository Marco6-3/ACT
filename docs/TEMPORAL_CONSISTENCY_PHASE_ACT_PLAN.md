# 示教时序一致性与 Phase-ACT 实验计划

> 状态：2026-09-01 提案。该路线不替代已经冻结的 Mix-1-100@20k、Mix-1-300@60k、All-3@20k 三组多视角收尾实验；只有多视角没有形成可靠增益，或其失败机制仍与单视角一致时，才把本文件提升为主线。

## 1. 动机

当前最强诊断信号不是“看得不够多”，而是示教本身存在显著的时序多模态：

- 100 条成功示教中，左侧先闭合 57 条、右侧先闭合 43 条；
- 左右首次闭合间隔中位数为 2.80 s；
- 没有一条示教在 1 s 内完成双侧首次闭合；
- 第一侧抓住后，毛巾已经被约束/形变，第二侧动作实际是在一个不同的条件分布中执行；
- 部署时如果第一侧夹空，策略仍会继续进入第二阶段动作，而训练集中几乎没有“夹空后恢复/重抓”的状态。

因此需要区分两个不同问题：

1. **Temporal consistency：** 相似初态对应“左先/右先”两种长间隔动作顺序，是否让行为克隆产生动作多模态和折中轨迹？
2. **Phase representation：** 如果明确告诉模型“当前处于哪个动作阶段”，是否能在保留混合示教的情况下减少状态别名和错误阶段动作？

研究门控关系：

```text
Experiment A：Fixed-order vs Mixed-order
        ↓
若固定顺序明显更稳定
        ↓
说明时序多模态值得继续追查
        ↓
Experiment C：Phase-ACT
        ↓
检验显式 phase 是否能在混合顺序数据上恢复性能
```

如果 Experiment A 没有效应，不进入 Phase-ACT，优先回到空间精度、接触、反馈和数据覆盖问题。

---

## 2. Experiment A：示教时序一致性

### 2.1 核心问题

> 在数据量、训练预算、相机和部署参数相同的条件下，去掉“左先/右先”顺序多模态，是否能提高 ACT 的角点落点精度和稳定双抓成功率？

### 2.2 假设

**H-A：** Mixed-order 数据中，相似视觉状态对应两种不同的后续动作时序；确定性部署时 ACT 会在两种模式之间产生折中或错误相位切换。固定唯一先后顺序后，轨迹方差、闭合误差和双抓失败应下降。

反驳条件：Fixed-order 与 Mixed-order 的闭合误差、第一侧成功率、第二侧条件成功率和最终双抓成功率均无一致改善。

### 2.3 数据构造

先只使用当前表现最好的单顶部相机数据源，默认优先 Orbbec，对已有 100 条 source episode 自动标注 `first_close_side`：

- `L-first`：左夹爪首次进入 `<5 mm` 早于右夹爪；
- `R-first`：右夹爪首次进入 `<5 mm` 早于左夹爪；
- 同时闭合若未来出现，单独标为 `simultaneous`，本轮不混入三组。

首轮冻结三组，每组 **40 episodes**：

| 条件 | 组成 | episodes | steps | 目的 |
|---|---|---:|---:|---|
| A0 / Mixed-40 | 20 L-first + 20 R-first | 40 | 8k | 保留顺序多模态 |
| A1 / Left-first-40 | 40 L-first | 40 | 8k | 固定左先 |
| A2 / Right-first-40 | 40 R-first | 40 | 8k | 固定右先 |

8k steps 的原因：现有基线为 100 episodes@20k，即 200 optimizer updates / dataset episode；40@8k 保持相同口径。三组保持 batch size、seed、图像输入、动作标签、checkpoint 规则和数据增强完全一致。

为了降低“刚好抽到更容易 episode”的风险：

- 在建集前按布局/初始位置做分层抽样；
- A0 中 L/R 各 20 条；
- A1/A2 也尽量匹配 A0 的布局分布；
- 保存 source episode ID 清单和随机 seed；
- 首轮使用 seed 1000；若出现明确效应，再补 2 个训练 seed 复验，而不是直接扩大方法复杂度。

### 2.4 真机评估

冻结当前研究比较参数：

- 外部相机：Orbbec；
- `M=20`；
- 当前 no-hold 后台推理 runtime；
- 五布局 `L1–L5`；
- 灯光、窗帘、毛巾朝向和平整度固定；
- 所有失败和超时均保存。

首轮每个模型 **10 trials**，每个布局 2 次，只作为 gate；若 A1 或 A2 相对 A0 出现至少 3/10 的绝对成功数优势，或闭合误差出现清晰下降，再将相关条件扩展到至少 20 trials。

### 2.5 主要指标

最终成功率不是唯一指标。逐 trial 至少记录：

1. `stable_corner_grasp_success`；
2. 第一侧是否抓住指定角；
3. 第二侧是否抓住指定角；
4. `P(second_success | first_success)`；
5. `P(second_success | first_fail)`；
6. 左右首次闭合时间与间隔；
7. 闭合瞬间角点—TCP 误差（标定可用后）；
8. 失败类型：`miss_first / miss_second / wrong_corner / timeout / slip / other`。

特别关注：如果固定顺序主要提升 `P(second_success | first_success)`，说明第二阶段条件分布更稳定；如果第一侧本身也明显提升，则说明顺序多模态可能已经污染了更早的动作预测。

### 2.6 Go / No-Go

**进入 Experiment C 的最小证据：**

- A1 或 A2 相对 A0 在相同评估协议下有稳定方向的提升；并且
- 改善不仅来自某一个布局；并且
- 至少一个机制指标（闭合误差、第一/第二侧条件成功率、动作时序方差）与最终成功率同方向改善。

以下情况停止“时序多模态”主线：

- Fixed-order 与 Mixed-order 基本一致；
- 提升只来自单个布局或明显的数据难度差异；
- 固定顺序后仍主要在第一侧接近阶段出现厘米级落点误差；
- 真实捕获区域测量表明当前误差远大于夹爪容差，此时优先解决空间精度。

---

## 3. Experiment C：Phase-ACT

### 3.1 启动条件

只有 Experiment A 支持“时序一致性影响性能”时才实现 Phase-ACT。目标不是单纯增加参数，而是回答：

> 显式动作阶段表征，能否让 ACT 在继续使用 mixed-order demonstrations 时区分视觉相似但动作语义不同的状态？

### 3.2 第一版 phase 定义

先不引入触觉和复杂恢复控制，使用可以从现有示教自动派生的阶段标签：

| phase | 含义 |
|---|---|
| P0 | 双臂 approach，均未进入抓取事件 |
| P1-L | 左侧作为 first-grasp 的接近/闭合阶段 |
| P1-R | 右侧作为 first-grasp 的接近/闭合阶段 |
| P2 | 第一侧已经闭合，第二侧继续对齐/接近 |
| P3 | 第二侧闭合，双侧抓取确认窗口 |
| P4 | lift / hold |

`P1-L` 与 `P1-R` 必须分开，否则 phase 本身无法消除左先/右先的动作冲突。

未来只有在补充 corrective demonstrations 后，才增加 `P5-recovery`，避免在没有恢复数据时人为定义一个模型从未见过的阶段。

### 3.3 模型对照

在同一 mixed-order 数据上至少比较：

| 条件 | 输入/监督 | 目的 |
|---|---|---|
| C0 Raw-ACT | 原始 RGB + state | 基线 |
| C1 Oracle-Phase ACT | 额外输入真实 phase token | 诊断 phase 信息的性能上限 |
| C2 Predicted-Phase ACT | phase classifier 预测 phase，再条件化 ACT | 可部署方案 |

建议实现：

```text
images + robot state
        ↓
shared visual/state encoder
        ├── phase head → p(z_t)
        ↓
phase embedding z_t
        ↓
ACT transformer / action chunk decoder
```

训练损失：

```text
L = L_ACT + lambda_phase * L_phase
```

首轮不要同时修改 backbone、chunk size、temporal ensemble 或相机数量，避免无法归因。

### 3.4 phase 标签生成

优先使用动作和夹爪状态自动生成：

- 首次 `<5 mm` 闭合作为 first-grasp 事件；
- 第二侧首次 `<5 mm` 作为 second-grasp 事件；
- 闭合事件前设置有限 pre-grasp 窗口；
- 双侧闭合后的微抬/保持归入 P4；
- 对边界帧允许设置小范围 ignore window，避免 1–2 帧抖动造成标签噪声。

必须把 phase 标签生成脚本、阈值和边界规则固定在 runtime 仓库中，并在 ACT 仓库保存版本和数据快照。

### 3.5 关键判定

Phase-ACT 只有在以下证据同时出现时才值得继续：

1. C1 Oracle-Phase 明显优于 C0，说明 phase 信息本身有价值；
2. C2 的 phase 分类准确率和真机行为足以接近 C1，而不是只在离线分类上高分；
3. C2 改善 Mixed-order 数据上的闭合误差/双抓成功，而不是依赖固定顺序；
4. phase token 的收益在至少多个布局成立。

如果 C1 都不优于 C0，则停止 Phase-ACT：问题不太可能主要来自“缺少动作阶段变量”。

如果 C1 有明显收益而 C2 没有，研究问题转为“如何从视觉与机器人状态可靠估计接触阶段”，而不是继续扩大 ACT。

---

## 4. 与多视角路线的关系

多视角和时序一致性回答的是两个不同问题：

- 多视角：**同一动作意图下，增加视觉信息是否改善空间表征？**
- Experiment A/C：**相似视觉状态下，动作标签自身存在多个时序模式时，如何避免行为克隆发生状态别名？**

因此，即使 All-3 最终略有提升，只要失败仍集中在“第一侧失败后第二侧继续执行错误阶段”或 mixed-order 的高方差轨迹，Experiment A 仍有独立研究价值。

但如果 All-3 已把主要失败消除到接触/滑脱阶段，就不应同时启动 Phase-ACT，应优先解释多视角的真实增益来源。

## 5. 当前推荐执行顺序

```text
完成多视角三组收尾 gate
        ↓
若无可靠增益 / 失败机制不变
        ↓
自动标注现有 100 条示教的 first_close_side
        ↓
A0 Mixed-40 / A1 Left-first-40 / A2 Right-first-40
        ↓
8k steps，同训练预算，10-trial gate
        ↓
有明确 temporal-consistency 效应？
   ├── 否：停止 Phase-ACT，转空间精度/接触/反馈
   └── 是：扩展到 20 trials + 多 seed
                    ↓
              C0/C1/C2 Phase-ACT
```

这条路线的首要目标不是立刻提高成功率，而是形成一个可以被证伪的机制结论：**对于接触精度敏感的双臂柔性操作，示教动作的时序一致性是否比额外视觉观测更关键，以及显式 phase 是否能恢复 mixed-order demonstrations 的可学习性。**
