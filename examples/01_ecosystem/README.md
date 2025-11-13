<!-- Placeholder example README. -->

# examples/01_ecosystem

本目录包含书中引用的生态系统示例（轻量、可运行）。

目标

- 提供一个简短的架构概览（组件连线）和一个可运行的演示脚本，帮助读者快速看到数据流从生产到分析的过程。

包含文件（主要）

- `overview.md` - 架构/概览说明
- `demo.sh` - 可运行的演示脚本（打印 ASCII 拓扑并模拟简单的生产-消费输出）

快速运行

```bash
bash examples/01_ecosystem/demo.sh
```

注意

- 脚本是轻量示例，无外部依赖（内置 Python 可运行）。
- 用于 CI 的 smoke-test 会执行 `demo.sh` 并期望脚本以退出码 0 成功返回。
