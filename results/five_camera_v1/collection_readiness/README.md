# Collection readiness — 2026-08-27

> 作用范围：本页记录的是正式采集前用 `bimanual_pickup` 短 episode 完成的链路冒烟，只证明当时五相机录制和 `paired3` 转换路径可运行。它不是 2026-08-28 `pick_corner` 100 条正式数据的完整性验收，也不能替代三份最终数据集的逐 episode 配对检查。

自动预检已经确认：

- 五路 canonical RGB topic 全部在线，实测约 29.97–30.02 Hz；
- `external_1` 为 1280×720，其余四路为 640×480，均符合冻结配置；
- NUC chrony 跟随本地主机，检查时 offset 在 0–10 µs，判定 `GOOD`；
- 五路首帧已保存为 `first_frames.jpg`，未发现空帧或解码错误。
- 人工已确认 `external_1=top`、`external_2=side_oblique`、`external_3=front`。

真机门禁已经通过：

1. 本地 `can1/can0` 均为 `UP/ERROR-ACTIVE`，RX 持续增长且无 bus error；
2. 人员在真机旁并确认急停可用后完成 5 秒成功示范 `episode_000001`；
3. `mcap_smoke.json` 证明五路 RGB 各收到并写入 150 帧、零 recorder drop；
4. `paired3_smoke_validation.json` 证明三个独立输出各有 149 帧，三个 camera feature
   均为 640×480@30 Hz，且 state/action/timestamp 完全一致。

旧的 `episode_000000` checksum 不匹配，保留原状用于排查；批量转换会明确隔离它，
不会把它写入训练集。

主机稳定性备注：本次启动以来三个无关进程均在逻辑 CPU 8 上发生非法跳转。
五相机 workstation 与 record 入口暂时将其进程树限制到 `0-7,10-31`，排除同一
P-core 的 CPU 8/9；正式长时间采集前仍应检查 BIOS 超频/XMP、CPU 和内存稳定性。

`live_preflight.json`、`mcap_smoke.json` 和 `paired3_smoke_validation.json` 均为历史准备证据。正式采集状态及转换验收门槛见 [`../../data_collection_2026-08-28.md`](../../data_collection_2026-08-28.md)。
