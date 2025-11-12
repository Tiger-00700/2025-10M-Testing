# examples/07_batch

批处理示例目录。该目录包含一个非常小的示例，用于展示如何以批处理方式读取 CSV 并进行简单处理。

主要文件：

- `batch_ingest.py` - 使用标准库读取 `sample_data.csv` 并打印行计数。
- `batch_demo.sh` / `batch_demo.ps1` - 简短的 shell/PowerShell 演示，可在 CI 中作为 smoke 测试调用。
- `sample_data.csv` - 示例数据（小文件）。

快速运行（bash）:

```bash
bash examples/07_batch/batch_demo.sh
```

CI 要求：`examples/07_batch/smoke.sh` 应能在 Linux runner 上返回退出码 0。

<!-- Placeholder example README. -->
