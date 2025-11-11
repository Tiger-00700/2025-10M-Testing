````markdown

# examples/07_batch

批处理（batch）示例目录。

本目录包含一个非常轻量的批处理示例，演示如何从 CSV 读取、简单转换并写出结果文件。该示例无外部依赖。

快速运行（Unix）:

```bash
bash examples/07_batch/batch_demo.sh
```

Windows（PowerShell）:

```powershell
powershell -File examples/07_batch/batch_demo.ps1
```

CI smoke-test: `examples/07_batch/smoke.sh` / `smoke.ps1` 会运行 demo 并期待退出码 0。

````

# examples/07_batch

Batch-processing examples for the book. Include at least one sample that demonstrates a batch ingest and simple transformation.

Suggested files

- `batch_ingest.py` - small Python batch example
- `README.md` - this file

Quick run

```bash
python examples/07_batch/batch_ingest.py
```
