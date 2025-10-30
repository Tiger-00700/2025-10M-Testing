import com.klarna.hiverunner.HiveShell;
import com.klarna.hiverunner.StandaloneHiveRunner;
import com.klarna.hiverunner.annotations.HiveSQL;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.List;

import static org.junit.Assert.assertEquals;

@RunWith(StandaloneHiveRunner.class)
public class HiveQueryTest {

    @HiveSQL(files = {})  // 可以加载HQL脚本文件
    private HiveShell hiveShell;

    @Test
    public void testSimpleQuery() {
        // 创建测试表
        hiveShell.execute("CREATE TABLE test_table (id INT, name STRING, value DOUBLE)");
        
        // 插入测试数据
        hiveShell.execute("INSERT INTO test_table VALUES (1, 'A', 10.5), (2, 'B', 20.5), (3, 'C', 30.5)");
        
        // 执行查询
        List<Object[]> result = hiveShell.executeQuery("SELECT * FROM test_table WHERE id > 1");
        
        // 验证结果
        assertEquals(2, result.size());
        assertEquals(2, result.get(0)[0]);
        assertEquals("B", result.get(0)[1]);
        assertEquals(20.5, result.get(0)[2]);
    }

    @Test
    public void testAggregationQuery() {
        // 创建测试表
        hiveShell.execute("CREATE TABLE sales (region STRING, amount INT)");
        
        // 插入测试数据
        hiveShell.execute("INSERT INTO sales VALUES ('North', 100), ('South', 200), ('North', 300)");
        
        // 执行聚合查询
        List<Object[]> result = hiveShell.executeQuery(
            "SELECT region, SUM(amount) as total FROM sales GROUP BY region ORDER BY total DESC"
        );
        
        // 验证结果
        assertEquals(2, result.size());
        assertEquals("North", result.get(0)[0]);
        assertEquals(400, result.get(0)[1]);
    }
}
