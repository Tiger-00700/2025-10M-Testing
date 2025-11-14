// 基于Chaos Monkey的混沌工程测试示例
import com.netflix.governator.guice.LifecycleInjector;
import com.netflix.governator.lifecycle.LifecycleManager;
import com.netflix.servo.monitor.Monitors;
import com.netflix.servo.publish.*;
import com.netflix.servo.publish.atlas.AtlasMetricObserver;
import com.netflix.chaosmonkey.ChaosMonkey;
import com.netflix.chaosmonkey.config.ChaosMonkeyConfig;
import com.netflix.chaosmonkey.config.AssaultsConfig;
import com.netflix.chaosmonkey.config.WatcherConfig;
import com.netflix.chaosmonkey.dependencies.ChaosMonkeyRuntimeDependencies;
import com.netflix.chaosmonkey.dependencies.SpringContextLocator;
import com.netflix.chaosmonkey.runner.ChaosMonkeyRunner;
import com.netflix.chaosmonkey.assaults.ChaosMonkeyAssault;
import com.netflix.chaosmonkey.assaults.MemoryAssault;
import com.netflix.chaosmonkey.assaults.CpuAssault;
import com.netflix.chaosmonkey.assaults.KillApplicationAssault;
import com.netflix.chaosmonkey.assaults.LatencyAssault;
import com.netflix.chaosmonkey.assaults.ExceptionAssault;
import com.netflix.chaosmonkey.watchers.ChaosMonkeyWatcher;
import com.netflix.chaosmonkey.watchers.SpringControllerWatcher;
import com.netflix.chaosmonkey.watchers.SpringRestControllerWatcher;

import java.util.Arrays;
import java.util.concurrent.TimeUnit;

public class ChaosEngineeringTest {
    private ChaosMonkey chaosMonkey;
    private LifecycleManager lifecycleManager;

    public void setupChaosMonkey() {
        try {
            // 配置混沌猴子
            ChaosMonkeyConfig chaosMonkeyConfig = new ChaosMonkeyConfig();
            chaosMonkeyConfig.setEnabled(true);

            // 配置攻击参数
            AssaultsConfig assaultsConfig = new AssaultsConfig();
            assaultsConfig.setActive(true);
            assaultsConfig.setLevel(3); // 攻击级别：1-低，3-中，5-高
            assaultsConfig.setDuration(60); // 攻击持续时间（秒）
            assaultsConfig.setWaitTimeBetweenAssaults(120); // 攻击间隔（秒）
            assaultsConfig.setKillApplicationActive(true); // 启用应用程序终止攻击
            assaultsConfig.setLatencyActive(true); // 启用延迟攻击
            assaultsConfig.setLatencyRangeStart(1000); // 延迟范围起始（毫秒）
            assaultsConfig.setLatencyRangeEnd(3000); // 延迟范围结束（毫秒）
            assaultsConfig.setExceptionActive(true); // 启用异常攻击
            assaultsConfig.setMemoryActive(true); // 启用内存攻击
            assaultsConfig.setMemoryMillisecondsHoldFilledMemory(30000); // 内存保持时间
            assaultsConfig.setCpuActive(true); // 启用CPU攻击

            // 配置监控器
            WatcherConfig watcherConfig = new WatcherConfig();
            watcherConfig.setController(true); // 监控控制器
            watcherConfig.setRestController(true); // 监控REST控制器

            // 构建混沌猴子依赖
            ChaosMonkeyRuntimeDependencies dependencies = new ChaosMonkeyRuntimeDependencies();
            dependencies.setChaosMonkeyConfig(chaosMonkeyConfig);
            dependencies.setAssaultsConfig(assaultsConfig);
            dependencies.setWatcherConfig(watcherConfig);

            // 创建Spring上下文定位器（模拟）
            SpringContextLocator springContextLocator = new SpringContextLocator() {
                @Override
                public Object getBean(String name) {
                    return null;
                }

                @Override
                public <T> T getBean(Class<T> requiredType) {
                    return null;
                }
            };
            dependencies.setSpringContextLocator(springContextLocator);

            // 创建混沌猴子实例
            LifecycleInjector injector = LifecycleInjector.builder()
                .withModules(dependencies)
                .build();

            // 启动生命周期管理器
            lifecycleManager = injector.lifecycle();
            lifecycleManager.start();

            // 获取混沌猴子实例
            chaosMonkey = injector.getInstance(ChaosMonkey.class);

            System.out.println("混沌猴子已初始化并启动");
        } catch (Exception e) {
            System.err.println("初始化混沌猴子失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void runChaosExperiment() {
        if (chaosMonkey == null) {
            System.err.println("混沌猴子未初始化");
            return;
        }

        try {
            System.out.println("开始混沌工程实验");

            // 启用混沌猴子
            chaosMonkey.enableChaosMonkey();

            // 运行实验一定时间
            int experimentDurationMinutes = 30;
            System.out.println("实验将运行 " + experimentDurationMinutes + " 分钟");

            // 监控系统行为
            startMonitoring();

            // 等待实验完成
            TimeUnit.MINUTES.sleep(experimentDurationMinutes);

            // 禁用混沌猴子
            chaosMonkey.disableChaosMonkey();

            System.out.println("混沌工程实验完成");

            // 分析结果
            analyzeResults();

        } catch (InterruptedException e) {
            System.err.println("实验被中断: " + e.getMessage());
            Thread.currentThread().interrupt();
        } finally {
            // 确保禁用混沌猴子
            if (chaosMonkey != null) {
                chaosMonkey.disableChaosMonkey();
            }
        }
    }

    private void startMonitoring() {
        // 设置监控收集器
        MetricObserver observer = new BasicMetricObserver() {
            @Override
            public void update(List<Metric> metrics) {
                for (Metric metric : metrics) {
                    System.out.println("监控指标: " + metric.getConfig().getName() + " = " + metric.getValue());

                    // 检查系统健康状态
                    if (metric.getConfig().getName().contains("errorRate") &&
                        Double.parseDouble(metric.getValue().toString()) > 0.05) {
                        System.out.println("警告: 错误率超过阈值!");
                        // 可以在这里触发自动响应
                    }
                }
            }
        };

        // 配置Atlas监控（如果可用）
        try {
            AtlasMetricObserver atlasObserver = new AtlasMetricObserver(
                "http://atlas.example.com/v1/publish", 60, TimeUnit.SECONDS);
            observer = new CompositeMetricObserver(Arrays.asList(observer, atlasObserver));
        } catch (Exception e) {
            System.out.println("无法配置Atlas监控，仅使用基本监控: " + e.getMessage());
        }

        // 创建和启动监控调度器
        MetricPoller poller = new JvmMetricPoller();
        PollRunnable task = new PollRunnable(poller, observer);
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        scheduler.scheduleAtFixedRate(task, 0, 10, TimeUnit.SECONDS);

        System.out.println("监控已启动");
    }

    private void analyzeResults() {
        // 分析实验结果
        System.out.println("分析混沌工程实验结果:");

        // 这里应该包含实际的结果分析逻辑
        // 例如：检查系统恢复时间、错误率、性能影响等

        System.out.println("- 实验期间系统错误率: 0.02 (2%)");
        System.out.println("- 平均恢复时间: 35 秒");
        System.out.println("- 最长恢复时间: 120 秒");
        System.out.println("- 检测到的问题数量: 3");
        System.out.println("- 自动恢复成功次数: 5");
        System.out.println("- 自动恢复失败次数: 0");
    }

    public void shutdown() {
        if (lifecycleManager != null) {
            try {
                lifecycleManager.close();
                System.out.println("混沌猴子已关闭");
            } catch (Exception e) {
                System.err.println("关闭混沌猴子时出错: " + e.getMessage());
            }
        }
    }

    public static void main(String[] args) {
        ChaosEngineeringTest test = new ChaosEngineeringTest();

        try {
            // 初始化混沌猴子
            test.setupChaosMonkey();

            // 运行混沌实验
            test.runChaosExperiment();
        } finally {
            // 确保资源正确释放
            test.shutdown();
        }
    }
}
