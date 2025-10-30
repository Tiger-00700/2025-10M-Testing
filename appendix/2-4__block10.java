import java.io.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.Date;

public class PostgreSQLRestoreTest {
    
    private static final String LOG_FILE = "/logs/postgresql_restore_test.log";
    private static final String DB_HOST = "localhost";
    private static final String DB_PORT = "5432";
    private static final String DB_NAME = "test_database";
    private static final String DB_USER = "postgres";
    private static final String DB_PASSWORD = "secure_password";
    private static final String BACKUP_DIR = "/backup/postgresql";
    
    public static void main(String[] args) {
        try {
            log("开始PostgreSQL恢复测试");
            
            // 记录开始时间
            long startTime = System.currentTimeMillis();
            
            // 1. 准备测试数据
            log("准备测试数据...");
            prepareTestData();
            
            // 2. 创建备份
            log("创建备份...");
            String backupFilePath = createBackup();
            
            // 3. 损坏数据
            log("损坏测试数据...");
            corruptData();
            
            // 4. 执行恢复
            log("执行数据恢复...");
            boolean restoreSuccess = restoreData(backupFilePath);
            
            // 5. 验证恢复结果
            log("验证恢复结果...");
            boolean verificationSuccess = verifyRestore();
            
            // 6. 计算执行时间
            long endTime = System.currentTimeMillis();
            long duration = (endTime - startTime) / 1000;
            
            if (restoreSuccess && verificationSuccess) {
                log("PostgreSQL恢复测试成功，耗时: " + duration + " 秒");
                System.out.println("测试成功");
            } else {
                log("PostgreSQL恢复测试失败");
                System.out.println("测试失败");
            }
            
        } catch (Exception e) {
            log("测试过程中发生错误: " + e.getMessage());
            e.printStackTrace();
            System.out.println("测试失败");
        }
    }
    
    private static void prepareTestData() throws IOException, InterruptedException {
        // 创建测试表并插入数据
        String sqlCommand = "psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -c ";
        
        // 创建测试表
        String createTable = "CREATE TABLE IF NOT EXISTS test_users (id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(100));";
        executeCommand(sqlCommand + "\"" + createTable + "\"");
        
        // 插入测试数据
        String insertData = "INSERT INTO test_users (name, email) VALUES ('测试用户1', 'test1@example.com'), ('测试用户2', 'test2@example.com');";
        executeCommand(sqlCommand + "\"" + insertData + "\"");
        
        log("测试数据准备完成");
    }
    
    private static String createBackup() throws IOException, InterruptedException {
        String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String backupFile = BACKUP_DIR + File.separator + "backup_" + timestamp + ".sql";
        
        // 创建备份目录（如果不存在）
        Files.createDirectories(Paths.get(BACKUP_DIR));
        
        // 使用pg_dump创建备份
        String backupCommand = "PGPASSWORD=" + DB_PASSWORD + " pg_dump -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -f " + backupFile;
        executeCommand(backupCommand);
        
        log("备份创建完成: " + backupFile);
        return backupFile;
    }
    
    private static void corruptData() throws IOException, InterruptedException {
        // 删除部分数据并修改剩余数据
        String sqlCommand = "psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -c ";
        
        // 删除一条记录
        executeCommand(sqlCommand + "\"DELETE FROM test_users WHERE id = 1;\"");
        
        // 修改剩余记录
        executeCommand(sqlCommand + "\"UPDATE test_users SET name = '损坏数据', email = 'corrupted@example.com';\"");
        
        log("数据已损坏");
    }
    
    private static boolean restoreData(String backupFilePath) throws IOException, InterruptedException {
        // 停止数据库服务（可选，取决于测试场景）
        // executeCommand("systemctl stop postgresql");
        
        // 删除并重新创建数据库
        String dropDbCommand = "PGPASSWORD=" + DB_PASSWORD + " psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -c \"DROP DATABASE IF EXISTS " + DB_NAME + ";\"";
        executeCommand(dropDbCommand);
        
        String createDbCommand = "PGPASSWORD=" + DB_PASSWORD + " psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -c \"CREATE DATABASE " + DB_NAME + ";\"";
        executeCommand(createDbCommand);
        
        // 从备份恢复
        String restoreCommand = "PGPASSWORD=" + DB_PASSWORD + " psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -f " + backupFilePath;
        int exitCode = executeCommand(restoreCommand);
        
        // 启动数据库服务（如果之前停止了）
        // executeCommand("systemctl start postgresql");
        
        boolean success = (exitCode == 0);
        log("数据恢复" + (success ? "成功" : "失败"));
        return success;
    }
    
    private static boolean verifyRestore() throws IOException, InterruptedException {
        // 查询恢复后的数据
        String sqlCommand = "psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -t -c \"SELECT COUNT(*) FROM test_users;\"";
        String countResult = executeCommandWithOutput(sqlCommand).trim();
        
        log("恢复后的数据记录数: " + countResult);
        
        // 验证记录数是否正确
        boolean countCorrect = "2".equals(countResult);
        
        // 验证数据内容
        sqlCommand = "psql -h " + DB_HOST + " -p " + DB_PORT + " -U " + DB_USER + " -d " + DB_NAME + " -t -c \"SELECT email FROM test_users WHERE name = '测试用户1';\"";
        String emailResult = executeCommandWithOutput(sqlCommand).trim();
        
        log("恢复后的邮箱地址: " + emailResult);
        
        boolean dataCorrect = "test1@example.com".equals(emailResult);
        
        boolean verificationSuccess = countCorrect && dataCorrect;
        log("数据验证" + (verificationSuccess ? "通过" : "失败"));
        
        return verificationSuccess;
    }
    
    private static int executeCommand(String command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("bash", "-c", command);
        pb.environment().put("PGPASSWORD", DB_PASSWORD);
        Process process = pb.start();
        
        // 读取错误输出
        String errorOutput = new String(process.getErrorStream().readAllBytes());
        if (!errorOutput.isEmpty()) {
            log("命令执行错误: " + errorOutput);
        }
        
        return process.waitFor();
    }
    
    private static String executeCommandWithOutput(String command) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("bash", "-c", command);
        pb.environment().put("PGPASSWORD", DB_PASSWORD);
        Process process = pb.start();
        
        // 读取输出
        String output = new String(process.getInputStream().readAllBytes());
        
        // 读取错误输出
        String errorOutput = new String(process.getErrorStream().readAllBytes());
        if (!errorOutput.isEmpty()) {
            log("命令执行错误: " + errorOutput);
        }
        
        process.waitFor();
        return output;
    }
    
    private static void log(String message) {
        try {
            String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
            String logEntry = timestamp + " - " + message;
            
            // 写入日志文件
            Files.write(Paths.get(LOG_FILE), (logEntry + System.lineSeparator()).getBytes(), 
                        StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            
            // 同时输出到控制台
            System.out.println(logEntry);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
