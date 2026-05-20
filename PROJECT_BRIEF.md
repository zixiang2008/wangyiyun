# 网易三音云音箱求助协作项目

## 项目定位

这个项目的目标不是让普通用户自己写完适配程序，而是把：

- 产品公开资料
- 已知硬件信息
- 可行逆向方向
- 求助渠道
- 发帖模板
- 待补证据清单

整理成一个**方便高手接手**的协作包。

## 你当前最需要的结果

1. 让更多懂下面方向的人看到：
   - 蓝牙/BLE
   - 嵌入式 Linux / Android
   - 智能音箱协议
   - 拆机/UART/固件提取
   - Home Assistant / 本地智能体接入
2. 让他们快速理解：
   - 这不是“没电不会用”
   - 而是“厂商停服/入口消失，设备被半废弃”
3. 让高手判断哪条路线最值得做：
   - 恢复原功能
   - 本地化控制
   - 改造成 AI 语音终端
   - 直接硬改保留音腔与功放

## 项目建议标题

- `help-revive-netease-sing-cloud-speaker`
- `netease-sanyin-speaker-rescue`
- `网易三音云音箱-求助逆向与复活计划`

## 建议仓库简介

> 厂商入口下线后的网易三音云音箱资料汇总、逆向求助、硬件信息整理与协作入口。

## 推荐仓库栏目

- `README.md`：对外首页
- `docs/product_dossier.md`：产品资料档案
- `docs/help_channels.md`：求助渠道清单
- `docs/forum_post_zh.md`：中文发帖模板
- `docs/forum_post_en.md`：英文发帖模板
- `docs/research_checklist.md`：排查清单
- `docs/posting_plan.md`：发帖顺序与执行建议
- `artifacts/`：后续放扫描结果、拆机照片、抓包记录

## 高手最关心的几个问题

- 具体型号和底部铭牌是什么
- 主控、Wi‑Fi/BT 模组是什么
- 是否有调试口 / Mini-USB / UART
- 蓝牙到底是 BLE 配网，还是支持经典蓝牙音频
- 设备能否在路由器里拿到 IP
- App 是否还有旧版可用
- 有没有抓到任何局域网接口

## 你后续补充资料时的命名建议

- `artifacts/photos/bottom-label.jpg`
- `artifacts/photos/mainboard-front.jpg`
- `artifacts/photos/mainboard-back.jpg`
- `artifacts/network/probe_result.json`
- `artifacts/network/router-device-info.txt`
- `artifacts/audio/boot-voice.m4a`
- `artifacts/notes/timeline.md`
