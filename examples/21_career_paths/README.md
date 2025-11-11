# examples/21_career_paths

职业路径示例目录。提供一个小脚本用于以友好的文本方式展示能力/角色映射。

主要文件：

- `career_map.md` - 简短的能力/角色映射说明。
- `show_career_map.sh` - 打印职业路径示例的脚本，用作 smoke-test。

快速运行：

```bash
bash examples/21_career_paths/show_career_map.sh
```

CI: `examples/21_career_paths/smoke.sh` 将调用 `show_career_map.sh` 并以退出码 0 返回。
