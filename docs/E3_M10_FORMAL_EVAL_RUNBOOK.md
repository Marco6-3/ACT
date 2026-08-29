# E3-Orbbec M=10 正式 20 次评估执行清单

## 目标与冻结配置

本轮只建立 E3-Orbbec 的正式基线，不同时比较模型或继续调参。主要终点是左右夹爪均抓住指定材料角，抬升 10 cm 并保持 3 s。

| 项目 | 冻结值 |
|---|---|
| 模型 | E3-Orbbec |
| checkpoint | `pick_corner3/020000` |
| 数据集 | `pick_corner_orbbec` |
| 外部相机 | Orbbec；必须使用训练时对应的 top topic |
| 腕部相机 | 左右腕部相机均启用，映射不变 |
| prediction horizon | `K=100` |
| executed steps/query | `M=10` |
| 控制频率 | 30 Hz |
| 推理模式 | 后台推理；等待期间不重复发送 hold reference |
| 布局 | L1–L5，每个布局 4 次 |
| 随机种子 | `20260829` |
| 超时 | 60 s；超时按失败记录，不因“尚未闭合”而排除 |

逐 trial 顺序与登记字段已经冻结在 [`results/five_camera_v1/e3_m10_formal_20_plan.csv`](../results/five_camera_v1/e3_m10_formal_20_plan.csv)。不得根据上一条成败调整后续布局。

## 人工门禁：未完成不得开始正式 20 次

- [ ] 在安全静止状态下，分别给左、右夹爪发送可识别但不接触毛巾的开合动作，确认物理左/右臂与 `/execution/left_*`、`/execution/right_*` topic、action index 完全一致；将证据目录或截图路径写入 CSV 的 `operator_notes`。
- [ ] 逐视频核对历史 M=10 的 L1/L2：是否抓的是指定双角、是否实际抬升约 10 cm、是否保持至少 3 s。该核对只修正历史筛查记录，不并入正式 20 次。
- [ ] 将实际绝对 checkpoint 路径、Orbbec top topic、运行代码 commit SHA 写入 20 行 CSV；三项不得留空或只写简称。
- [ ] 固定机器人、夹爪、相机安装、桌面标记和毛巾实例；保存一张开跑前全景图。
- [ ] 固定顶灯和窗帘状态，不在 trial 中途调光；关闭会随 trial 改变的自动曝光设置，或明确记录其仍为启用状态。
- [ ] 完成一次不计入 20 次的无运动/低风险 preflight，确认三路图像、joint state、action、policy trace、recorder health 都能保存。

## 每条 trial 的操作

1. 按 CSV 当前行的 `layout_id` 放置毛巾，只做指定 ±30 mm 平移；保持朝向、平整度和目标角一致。
2. 将机器人恢复到同一初始状态，确认没有人工接管残留，启动本条唯一 `trial_id` 的录制。
3. 运行 E3-Orbbec、M=10；不在中途扶正毛巾、调灯、修改 timeout 或接管机械臂。
4. 到稳定保持、不可恢复失败、60 s 超时或安全停止时结束。
5. 立即填写左右有效接触、左右抓角、10 cm 抬升、3 s 保持、最终成功、失败类型和光照备注；不得只凭“看起来抓住了”填写成功。
6. 检查 recorder health。系统/相机故障标为 `invalid_system` 并另行补跑同一布局；策略超时仍是有效失败，不能补跑替换。

## 统一判定

- `stable_corner_grasp_success=1`：左右均为指定材料角，抬升 10 cm，保持 3 s，期间没有滑脱或明显夹入内侧布料。
- 双侧抓到布但偏离指定角：`wrong_corner`，主要终点记 0。
- 只有单侧夹住：`single_side_left` 或 `single_side_right`，主要终点记 0。
- 60 s 内没有完成：`timeout`，主要终点记 0；备注是否从未发出闭合指令。
- 人工急停、相机掉线、记录损坏等非策略故障：`invalid_system`，不进入分母，但必须保留原 trial 并追加补跑行，不能覆盖。

## 完成 20 次后的 Gate

先人工复核全部视频和标签，再计算总体及分布局成功率、95% Wilson 区间、左右/双侧夹持率、抬升保持率和失败类型。只有 E3 正式基线完成后，才用完全相同协议运行 E1-D435i1 和 E2-D435i2；模型 checkpoint 与 top topic 必须成对更换。

当前需要人类介入的最早节点就是上面的两项人工门禁与真机执行。其余统计和报告可在 CSV 回填后自动继续。
