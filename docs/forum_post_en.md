# Help wanted: revive the abandoned Netease Sing Cloud Speaker

Hi everyone,

I am trying to organize a collaborative rescue effort for an abandoned smart speaker: **Netease Sing Cloud Speaker** (`网易三音云音箱`).

## What happened

- The original onboarding / control entry appears to be gone from newer official app flows
- The speaker can no longer be easily reconnected to Wi‑Fi
- There is no 3.5mm input
- It does not behave like a normal Bluetooth audio speaker for me
- But the hardware itself still seems valuable and worth saving

## Why this device is interesting

Public teardown material suggests the device may contain:

- `Allwinner R16-J`
- `AP6236`
- `Broadcom BCM43436`
- `TI TPA3118`
- `ADAU1761`
- `STM32F105`

Also observed in teardown images:

- `Mini-USB` port
- reset button
- reserved `TF` card slot footprint

So this may be more recoverable than a fully closed microcontroller-only product.

## Goal

I am **not** asking casual users to build an app for me.
I want to build a clear public project so that people with the right skills can quickly jump in.

Areas where help is needed:

- BLE / Bluetooth analysis
- embedded Linux / Android investigation
- UART / debug interface identification
- firmware extraction guidance
- LAN protocol discovery
- repurposing as a local speaker / TTS / AI agent endpoint

## Project repository

- [https://github.com/zixiang2008/wangyiyun.git](https://github.com/zixiang2008/wangyiyun.git)

The repo contains:

- product dossier
- known hardware notes
- research checklist
- posting templates
- help channels list
- probe scripts for collecting evidence

## What I can provide next

- high-resolution bottom label photos
- teardown photos
- router DHCP / hostname / MAC info
- Bluetooth scan results
- power-on voice recordings
- more hands-on tests if guided

## Questions I would especially appreciate help with

1. For an `Allwinner R16-J + AP6236 + BCM43436` device, what would you probe first?
2. Does the `Mini-USB` port look more like a debug / factory / maintenance path?
3. If BLE is still advertising, is there a good chance that provisioning characteristics still exist?
4. If the cloud path is fully dead, is speaker repurposing the more practical route?

If you are interested, please reply on GitHub or open an issue with the specific evidence you want me to collect.
