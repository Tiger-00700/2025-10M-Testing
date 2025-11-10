
# GitHub Actions 环境变量配置示例

将以下内容添加到你的 `.github/workflows/xxx.yml` 的 `env:` 区块，实现质量门控：

```yaml
env:
  QUALITY_MAX_BROKEN_INTERNAL_LINKS: '0'           # 内部链接断链为0即失败
  QUALITY_FAIL_ON_BROKEN_EXAMPLE_LINKS: '1'        # 示例链接断链即失败
  # 可选：其它门控变量
  # BOOK_CI_FAIL_ON_CYCLES: '1'
  # BOOK_CI_FAIL_ON_UNREFERENCED: '1'
  # LEARNING_BLOCK_STYLE: balanced
  # LEARNING_BLOCK_REWRITE: '1'
```

> 说明：

> - 这些变量会被 `tools/aggregate_quality_dashboard.py` 读取并强制执行。
> - 断链/示例链接等指标超标时，CI 会直接 fail。
> - 其它变量可参考 `.github/ci-env-vars.md`。
