<!-- Placeholder example README. -->
# examples/10_tdms

示例目录用于展示时序数据（Time Domain Measurement/TDMS）的读取与预览。仓库中使用 CSV 作为轻量替代示例，说明如何读取时间序列并打印摘要。

主要文件：

- `read_tdms.py` - 演示如何读取示例时序 CSV（替代真实 TDMS 库），并打印点数与首个点。
- `sample_time_series.csv` - 小型示例数据。
- `preview_tdms.sh` / `preview_tdms.ps1` - 运行预览的脚本。

快速运行：

```bash
python examples/10_tdms/read_tdms.py
```

CI: `examples/10_tdms/smoke.sh` 会调用 `read_tdms.py` 并返回退出码 0。
