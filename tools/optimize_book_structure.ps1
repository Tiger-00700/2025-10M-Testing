# 书籍结构优化自动化脚本
# 执行顺序: 篇章重构 -> 内容扩充 -> 章节标准化 -> 验证

Write-Host "=== 书籍结构优化开始 ===" -ForegroundColor Green

# 任务1: 第2篇拆分重构
Write-Host "`n🔧 任务1: 第2篇拆分重构" -ForegroundColor Yellow

# 步骤1.1: 修改第2篇标题
Write-Host "   步骤1.1: 修改第2篇标题" -ForegroundColor Cyan
$part2File = "framework/第2篇-进阶篇-大数据测试方法与技术.md"
if (Test-Path $part2File) {
    $content = Get-Content $part2File -Raw -Encoding UTF8
    $content = $content -replace "## 第2篇 进阶篇-大数据测试方法与技术", "## 第2篇 数据处理测试（进阶）"
    Set-Content $part2File $content -Encoding UTF8
    Write-Host "      ✓ 第2篇标题已修改" -ForegroundColor Green
} else {
    Write-Host "      ✗ 文件不存在: $part2File" -ForegroundColor Red
}

# 步骤1.2: 创建第8篇框架文件
Write-Host "   步骤1.3: 创建第8篇框架文件" -ForegroundColor Cyan
$newPart8File = "framework/第8篇-数据质量安全（进阶）.md"
$newPart8Content = @"
## 第8篇 数据质量安全（进阶）

### 第9章 数据质量管理与测试【质量保障篇】

#### 9.1 数据质量维度与评估标准
#### 9.2 数据质量监控与告警机制
#### 9.3 数据质量问题诊断与修复
#### 9.4 数据质量自动化测试实践
#### 9.5 数据质量治理框架

### 第10章 大数据安全与合规测试【安全与合规篇】

#### 10.1 大数据安全威胁模型
#### 10.2 数据加密与访问控制测试
#### 10.3 隐私保护与合规性测试
#### 10.4 安全漏洞扫描与渗透测试
#### 10.5 安全监控与事件响应
"@
Set-Content $newPart8File $newPart8Content -Encoding UTF8
Write-Host "      ✓ 第8篇框架文件已创建" -ForegroundColor Green

# 任务2: 第3篇内容扩充
Write-Host "`n🔧 任务2: 第3篇内容扩充" -ForegroundColor Yellow

# 步骤2.1: 在第3篇框架文件末尾添加新章节
Write-Host "   步骤2.1: 添加新章节到第3篇" -ForegroundColor Cyan
$part3File = "framework/第3篇-进阶篇-环境与数据治理.md"
if (Test-Path $part3File) {
    $newChapters = @"

### 第14章 测试环境监控与告警体系

#### 14.1 测试环境资源监控
#### 14.2 性能指标收集与分析
#### 14.3 告警规则配置与管理
#### 14.4 监控仪表板设计
#### 14.5 自动化扩缩容策略

### 第15章 数据血缘治理与元数据管理

#### 15.1 数据血缘追踪技术
#### 15.2 元数据采集与存储
#### 15.3 数据目录构建
#### 15.4 血缘分析与影响评估
#### 15.5 元数据质量管理

### 第16章 多云环境测试策略

#### 16.1 多云架构测试挑战
#### 16.2 云服务兼容性测试
#### 16.3 数据迁移测试策略
#### 16.4 混合云网络测试
#### 16.5 成本优化与性能平衡
"@
    Add-Content $part3File $newChapters -Encoding UTF8
    Write-Host "      ✓ 新章节已添加到第3篇" -ForegroundColor Green
} else {
    Write-Host "      ✗ 文件不存在: $part3File" -ForegroundColor Red
}

# 任务3: 章节标准化 - 扩充过浅章节
Write-Host "`n🔧 任务3: 章节标准化" -ForegroundColor Yellow

# 步骤3.1: 扩充第22章
Write-Host "   步骤3.1: 扩充第22章" -ForegroundColor Cyan
$chapter22File = "chapter/第6篇-第22章-流批一体链路端到端案例.md"
if (Test-Path $chapter22File) {
    $expansionContent = @"

#### 22.2 案例背景与需求分析
#### 22.3 系统架构设计
#### 22.4 实施步骤与关键技术
#### 22.5 测试策略与验证方法
#### 22.6 性能优化与效果评估
"@
    Add-Content $chapter22File $expansionContent -Encoding UTF8
    Write-Host "      ✓ 第22章已扩充" -ForegroundColor Green
} else {
    Write-Host "      ✗ 文件不存在: $chapter22File" -ForegroundColor Red
}

# 任务4: 验证与发布
Write-Host "`n🔧 任务4: 验证与发布" -ForegroundColor Yellow

# 步骤4.1: 重新生成书籍
Write-Host "   步骤4.1: 重新生成书籍" -ForegroundColor Cyan
Write-Host "      运行构建脚本..." -ForegroundColor Cyan
& python build_book.py

# 步骤4.2: 结构验证
Write-Host "   步骤4.2: 结构验证" -ForegroundColor Cyan
Write-Host "      运行资产清单检查..." -ForegroundColor Cyan
& python tools/inventory_referenced_assets.py

Write-Host "      运行归档状态检查..." -ForegroundColor Cyan
& python tools/inventory_archive_status.py

Write-Host "`n=== 书籍结构优化完成 ===" -ForegroundColor Green
Write-Host "请检查生成的新书籍文件和验证报告" -ForegroundColor Cyan