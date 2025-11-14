// 测试用例组织与管理示例
public class TestSuiteManager {
    private Map<String, TestSuite> testSuites = new HashMap<>();
    private TestRegistry registry = new TestRegistry();

    // 注册测试套件
    public void registerTestSuite(TestSuite suite) {
        testSuites.put(suite.getId(), suite);
        // 注册测试用例到全局注册表
        for (TestCase testCase : suite.getTestCases()) {
            registry.registerTestCase(testCase);
        }
    }

    // 按标签筛选测试用例
    public List<TestCase> getTestsByTags(String... tags) {
        Set<String> tagSet = new HashSet<>(Arrays.asList(tags));
        return registry.getTestCases().stream()
                .filter(test -> {
                    Set<String> testTags = new HashSet<>(test.getTags());
                    return !Collections.disjoint(testTags, tagSet);
                })
                .collect(Collectors.toList());
    }

    // 按优先级获取测试用例
    public List<TestCase> getTestsByPriority(Priority priority) {
        return registry.getTestCases().stream()
                .filter(test -> test.getPriority() == priority)
                .collect(Collectors.toList());
    }

    // 执行测试套件
    public TestResult executeTestSuite(String suiteId, TestContext context) {
        TestSuite suite = testSuites.get(suiteId);
        if (suite == null) {
            throw new IllegalArgumentException("Test suite not found: " + suiteId);
        }

        TestResult result = new TestResult();
        result.setSuiteId(suiteId);
        result.setStartTime(System.currentTimeMillis());

        // 执行前置条件
        try {
            suite.getBeforeSuite().execute(context);
        } catch (Exception e) {
            result.setStatus(TestStatus.FAILED);
            result.setErrorMessage("Before suite failed: " + e.getMessage());
            result.setEndTime(System.currentTimeMillis());
            return result;
        }

        // 执行测试用例
        for (TestCase testCase : suite.getTestCases()) {
            if (context.shouldSkip(testCase.getId())) {
                result.addSkippedTest(testCase.getId());
                continue;
            }

            try {
                // 执行测试前置方法
                testCase.getBeforeTest().execute(context);

                // 执行测试
                TestStatus status = testCase.execute(context);

                // 记录结果
                if (status == TestStatus.PASSED) {
                    result.addPassedTest(testCase.getId());
                } else {
                    result.addFailedTest(testCase.getId(), testCase.getErrorMessage());
                }
            } catch (Exception e) {
                result.addFailedTest(testCase.getId(), e.getMessage());
            } finally {
                // 执行测试后置方法
                try {
                    testCase.getAfterTest().execute(context);
                } catch (Exception e) {
                    // 记录清理错误但不影响测试结果
                    result.addCleanupError(testCase.getId(), e.getMessage());
                }
            }
        }

        // 执行后置条件
        try {
            suite.getAfterSuite().execute(context);
        } catch (Exception e) {
            // 记录清理错误但不影响整体结果
            result.addCleanupError("suite", e.getMessage());
        }

        result.setEndTime(System.currentTimeMillis());

        // 计算整体状态
        if (result.getFailedTests().isEmpty() && result.getSkippedTests().isEmpty()) {
            result.setStatus(TestStatus.PASSED);
        } else if (result.getFailedTests().isEmpty()) {
            result.setStatus(TestStatus.SKIPPED);
        } else {
            result.setStatus(TestStatus.FAILED);
        }

        return result;
    }
}
