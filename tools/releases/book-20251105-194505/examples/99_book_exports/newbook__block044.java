// 欺诈检测系统压力测试示例
public class FraudDetectionStressTest {
    private static final int CONCURRENT_USERS = 1000;
    private static final int TRANSACTIONS_PER_USER = 10;

    public static void main(String[] args) throws InterruptedException {
        // 创建线程池
        ExecutorService executor = Executors.newFixedThreadPool(CONCURRENT_USERS);
        CountDownLatch latch = new CountDownLatch(CONCURRENT_USERS * TRANSACTIONS_PER_USER);

        // 开始时间
        long startTime = System.currentTimeMillis();

        // 提交并发请求
        for (int i = 0; i < CONCURRENT_USERS; i++) {
            final int userId = i;
            for (int j = 0; j < TRANSACTIONS_PER_USER; j++) {
                executor.submit(() -> {
                    try {
                        // 生成测试交易
                        Transaction transaction = generateTransaction(userId, j);

                        // 调用欺诈检测API
                        FraudResult result = fraudDetectionService.detectFraud(transaction);

                        // 验证响应时间
                        long responseTime = System.currentTimeMillis() - startTime;
                        Assert.assertTrue("响应时间超过阈值", responseTime < 100); // 100ms阈值

                        // 验证结果格式
                        Assert.assertNotNull("结果为空", result);
                        Assert.assertNotNull("风险分数为空", result.getRiskScore());
                    } finally {
                        latch.countDown();
                    }
                });
            }
        }

        // 等待所有请求完成
        latch.await();
        long endTime = System.currentTimeMillis();

        System.out.println("总交易数: " + (CONCURRENT_USERS * TRANSACTIONS_PER_USER));
        System.out.println("总耗时: " + (endTime - startTime) + "ms");
        System.out.println("TPS: " + (CONCURRENT_USERS * TRANSACTIONS_PER_USER * 1000.0 / (endTime - startTime)));

        executor.shutdown();
    }

    private static Transaction generateTransaction(int userId, int txId) {
        // 生成测试交易数据
        Transaction tx = new Transaction();
        tx.setUserId(userId);
        tx.setTxId("TX" + userId + "_" + txId);
        tx.setAmount(new Random().nextDouble() * 10000);
        tx.setTimestamp(System.currentTimeMillis());
        tx.setLocation("LOCATION_" + (userId % 10));
        // 注入一些已知的欺诈模式
        if (txId % 20 == 0) {
            tx.setAmount(9999.99); // 接近阈值的大额交易
        }
        return tx;
    }
}

> 【小结】

- 用 3~5 条项目化要点复盘本章内容
- 指出易错点/反模式与纠正建议
- 给出可延伸阅读或下一步实践方向
