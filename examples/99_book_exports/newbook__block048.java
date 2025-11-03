// 数据脱敏效果测试
public class DataMaskingTest {
    private static final String[] SENSITIVE_PATTERNS = {
        // 身份证号码模式
        "\\d{17}[\\d|x|X]",
        // 手机号码模式
        "1[3-9]\\d{9}",
        // 银行卡号模式
        "[0-9]{16,19}",
        // 邮箱地址模式
        "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
    };

    public static boolean testMaskingEffectiveness(String originalData, String maskedData) {
        // 验证脱敏后数据中没有敏感信息模式
        for (String pattern : SENSITIVE_PATTERNS) {
            Pattern regex = Pattern.compile(pattern);
            Matcher originalMatcher = regex.matcher(originalData);
            Matcher maskedMatcher = regex.matcher(maskedData);

            // 检查原始数据中的敏感信息是否在脱敏后数据中被移除
            while (originalMatcher.find()) {
                String sensitivePart = originalMatcher.group();
                if (maskedData.contains(sensitivePart)) {
                    System.out.println("脱敏失败: " + sensitivePart + " 仍然可见");
                    return false;
                }
            }

            // 检查脱敏后数据是否仍包含敏感模式
            if (maskedMatcher.find()) {
                System.out.println("脱敏不彻底: 仍检测到敏感信息模式");
                return false;
            }
        }

        // 验证脱敏数据的业务可用性（保留格式和部分特征）
        if (maskedData.length() < originalData.length() * 0.7) {
            System.out.println("脱敏过度: 数据格式变化太大");
            return false;
        }

        System.out.println("数据脱敏测试通过");
        return true;
    }

    public static boolean testConsistentMasking(String data1, String data2, String masked1, String masked2) {
        // 验证相同输入得到相同的脱敏结果
        if (data1.equals(data2) && !masked1.equals(masked2)) {
            System.out.println("脱敏不一致: 相同输入得到不同输出");
            return false;
        }

        System.out.println("脱敏一致性测试通过");
        return true;
    }

> 【小结】

- 用 3~5 条项目化要点复盘本章内容
- 指出易错点/反模式与纠正建议
- 给出可延伸阅读或下一步实践方向

}