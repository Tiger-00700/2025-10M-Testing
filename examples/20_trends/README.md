# examples/20_trends

趋势与技术方向示例目录。此处提供一个非常小的演示脚本，用来展示如何用脚本生成并简单分析时间序列趋势。

主要文件：

- `trend_demo.py` - 生成小样本并计算简单斜率估计，适合 CI smoke-tests。
- `trend_note.md` - 短说明/笔记。

快速运行：

```bash
python examples/20_trends/trend_demo.py
```

CI: `examples/20_trends/smoke.sh` 将调用 `trend_demo.py` 并以退出码 0 返回。
