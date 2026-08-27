# Corner-Approach Baseline：test1 / 020000

记录日期：2026-08-26（Asia/Shanghai）

## 定位

该模型只执行双臂接近毛巾目标角的动作，不闭合夹爪、不折叠。它对应
`TODO.md` 中“固定场景过拟合 Sanity Check”的候选模型；训练完成不等于该
sanity check 已通过。

## 已冻结的训练配置

- 数据集：`/home/alpha/lerobot_train/test1`
- 数据集规模：40 episodes、7495 frames、30 Hz、1 task（任务文本为 `test1`）
- checkpoint：`/home/alpha/lerobot_train/outputs/test1/checkpoints/020000/pretrained_model`
- checkpoint 选择规则：本次训练的最终且唯一保存步（20,000 steps）
- LeRobot：0.6.1
- policy：ACT，ResNet-18，51,613,582 parameters
- 随机种子：1000
- batch size：4
- 相机输入：`top`、`left_wrist`、`right_wrist`
- 数据和模型声明分辨率：三路均为 480 × 640 RGB
- 图像增强：关闭
- state/action：14 维，顺序均为左臂 6 关节、左夹爪、右臂 6 关节、右夹爪
- prediction horizon `K`：100
- checkpoint 默认连续执行步数 `M`：100
- 当前真机候选：保持 `K=100`，运行时覆盖为 `M=30`（无需重新训练）
- Policy 发布频率：30 Hz（`piper_bimanual.yaml` 和 `act_piper.py` 默认值）
- 名义 policy query frequency：约 0.3 Hz，即每约 3.33 s query 一次，另加推理阻塞时间
- 部署端现支持 `--action-steps M`（`1 <= M <= K`）；无需重新训练
- temporal ensemble：关闭（`temporal_ensemble_coeff=null`）
- normalization：图像、state、action 均为 mean/std

`M=100` 已由当前部署源码确认。0.3 Hz 是根据 `30 Hz / 100 steps` 得到的名义值，
真实 query 间隔还包含同步推理阻塞时间；robot controller frequency 和图像采集到
动作执行的端到端延迟仍需从运行日志测量。

M=30 无运动验证命令：

```bash
cd /home/alpha/physical_ai_runtime
pixi run -e lerobot act-piper -- \
  --checkpoint /home/alpha/lerobot_train/outputs/test1/checkpoints/020000/pretrained_model \
  --action-steps 30 \
  --hold-grippers-open \
  --dry-run
```

已验证日志包含 `chunk=100, execute=30` 和 `action shape=(30, 14)`。人工随后完成
了定性真机测试，报告机械臂可以接近/跟随角点；因为该次没有配套录包和量化结果，
不计入 20 次验收，也不能据此估计 `G`。

## 文件指纹

| 文件 | SHA-256 |
|---|---|
| `model.safetensors` | `cc2c92723754f4f7412a3e4e6600295f3319f4cb9e91654f7cf1b3bb232b66ba` |
| `config.json` | `632143f761d2b1070007dcc3eaf0c8e598ea756f75be5f6c3460527980e776d5` |
| `train_config.json` | `27fdf76eb36bbd5c907f88e203c4caced4d3238545a8d96ed6d73a61296a6830` |
| dataset `meta/info.json` | `35a6f4f13a1748260510665fb293a0b149ce26bbd8b1f1bc363fb9a28b54c258` |
| dataset `meta/stats.json` | `61d61dee9fb4eae31baea76a67315ad8f492b8df48b8341b03fe811133e29da4` |
| dataset `meta/tasks.parquet` | `b9e06292088ff59074256a14b0187712174131273a4455b89dc0b3837a4ab5e4` |

## 已通过的离线门

- [x] checkpoint 文件完整且训练步为 20,000
- [x] 使用 LeRobot 0.6.1 在 CUDA 上加载为 `ACTPolicy`
- [x] checkpoint 的三路 camera key、分辨率和 14 维 state/action 与数据集元信息一致
- [x] 加载后参数量为 51,613,582，policy 处于 eval mode
- [x] 使用同一 dataloader 和 checkpoint preprocessor 导出 20 组、共 60 张训练输入图像
- [x] 使用正式 `act-piper` 入口完成无 ROS、无运动 dry-run；输出 shape 为 `(100, 14)` 且全部有限
- [x] `M=30` dry-run；输出 shape 为 `(30, 14)` 且全部有限
- [x] 只接近任务的双夹爪硬保护：`--hold-grippers-open` 将两路夹爪命令保持为 0.020 m
- [x] MCAP 自动测量工具通过真实旧录包冒烟，并与在线 TF 交叉验证 FK（两臂误差 0.0 mm）

导出命令：

```bash
cd /home/alpha/lerobot_train
pixi run python /home/alpha/ACT/scripts/export_network_inputs.py \
  /home/alpha/lerobot_train/outputs/test1/checkpoints/020000/pretrained_model \
  /home/alpha/ACT/results/artifacts/test1_020000_network_inputs \
  --count 20
```

证据：`results/artifacts/test1_020000_network_inputs/contact_sheet.jpg`、
`manifest.csv` 和 60 张独立 JPEG。该 artifacts 目录已被 Git 忽略，避免将批量图像
提交到研究记录仓库。

人工检查结论：

- 蓝毛巾和红标签的颜色自然，未发现明显 RGB/BGR 颠倒；
- top、left_wrist、right_wrist 的内容符合各自安装视角，未发现 camera key 串位；
- top 相机稳定覆盖全局工作区，wrist 相机提供局部视角；
- 若干 episode 的早期 wrist 帧只看到房间背景，说明角点并非在 wrist 输入中始终可见；
- 训练配置无 crop、翻转或图像增强；checkpoint preprocessor 只执行 key rename、
  batch/device 转换和 mean/std normalization。

## 当前验收门：只接近角点，不闭合

范围：真实相机和机器人状态；只允许接近动作，禁用夹爪闭合和后续折叠。

安全边界：部署入口已有 `--hold-grippers-open` 硬限制，但 `--real` 仍只是显式确认，
不会替用户切换外部 RT launch 的 fake/real hardware。真机录制会在每条 episode 前
自动归位，必须由位于急停/接管位置的人启动并监督；Codex 不自动启动该步骤。

- [ ] 固定毛巾、双臂初始位置和相机，并给布局编号
- [x] 在部署入口加入并验证夹爪保持张开的硬保护
- [ ] 定义并验证 corner-approach 自动结束条件
- [ ] 核对真实推理的 camera key、RGB/BGR、分辨率、state/action 关节顺序
- [x] 导出至少 20 张 dataloader 实际网络输入图像
- [x] 实现接近阶段 query 状态、预测动作块、发布动作和时间戳记录（真实证据待下一批录制）
- [ ] 明确并记录实际 query Hz、controller Hz 和端到端延迟（`M=100` 已确认）
- [ ] 在至少 20 次执行中记录左右臂最近接误差和是否进入实测捕获区域
- [ ] 全程确认没有夹爪闭合命令

通过标准：至少 20 次执行均有完整证据，且根据实测捕获区域阈值报告左右臂及
双臂进入捕获区域的比例。模型到达“大致角点附近”不视为通过。

## 当前人工真机门

已完成能在无人干预下安全完成的代码、单测、dry-run 和旧 MCAP 离线验证。下一步
必须由人监督真机：用 `M=30`、夹爪强制张开，按 `C,L,R,F,B,CCW,CW` 顺序录制
7 条初筛 episode。完整命令见
`/home/alpha/physical_ai_runtime/apps/README.md` 的“M=30 角点跟随录制与自动测量”。

录制结束后运行：

```bash
cd /home/alpha/physical_ai_runtime
pixi run analyze-corner-following -- \
  --episodes-root data/episodes/corner_follow_m30 \
  --output-dir /home/alpha/ACT/results/artifacts/corner_follow_m30
```

固定 D435i 尚未标定到 `world`：TCP 轨迹是毫米，毛巾角点是像素。二者的探索性
回归只用于检查“是否随布局同向变化”和左右不对称，不能命名为真实 `G`；正式
`G_x/G_y/G_yaw` 必须等桌面 homography 或相机外参完成。
