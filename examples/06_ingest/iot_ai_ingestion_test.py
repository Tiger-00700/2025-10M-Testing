# iot_ai_ingestion_test.py
# 物联网AI采集测试案例

import json
import time
import numpy as np
from ai_anomaly_deployment import AIAnomalyDetector
from kafka import KafkaProducer, KafkaConsumer

class IoTAIIngestionTest:
    def __init__(self):
        self.anomaly_detector = AIAnomalyDetector('iot_anomaly_model.pkl')
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def simulate_sensor_data(self):
        """模拟物联网传感器数据"""
        sensors = ['temperature', 'humidity', 'motion', 'power']
        data = {}

        for sensor in sensors:
            if sensor == 'temperature':
                # 正常范围20-30°C，偶尔异常
                base_temp = 25 + np.random.normal(0, 2)
                if np.random.random() < 0.05:  # 5%异常概率
                    base_temp += np.random.normal(0, 10)
                data[sensor] = round(base_temp, 1)
            elif sensor == 'humidity':
                data[sensor] = round(60 + np.random.normal(0, 5), 1)
            elif sensor == 'motion':
                data[sensor] = np.random.choice([0, 1], p=[0.7, 0.3])
            elif sensor == 'power':
                data[sensor] = round(12 + np.random.normal(0, 1), 2)

        data['timestamp'] = time.time()
        data['device_id'] = f"device_{np.random.randint(1, 100)}"
        return data

    def ai_powered_monitoring(self, num_iterations=100):
        """AI驱动的物联网监控"""
        print("启动物联网AI监控...")

        anomalies_detected = 0
        total_processed = 0

        for i in range(num_iterations):
            sensor_data = self.simulate_sensor_data()
            total_processed += 1

            # 提取关键指标用于异常检测
            metrics = [
                sensor_data['temperature'],
                sensor_data['humidity'],
                sensor_data['power']
            ]

            # AI异常检测
            prediction, score = self.anomaly_detector.predict_anomaly(metrics)

            # 发送到Kafka用于进一步处理
            message = {
                'sensor_data': sensor_data,
                'ai_analysis': {
                    'is_anomaly': prediction == -1,
                    'anomaly_score': score,
                    'timestamp': time.time()
                }
            }

            self.producer.send('iot_sensor_analysis', message)

            if prediction == -1:
                anomalies_detected += 1
                print(f"[{i+1}] 检测到异常设备 {sensor_data['device_id']}: 温度{sensor_data['temperature']}°C, 异常分数{score:.3f}")
                # 触发告警或维护流程

            if (i + 1) % 20 == 0:
                print(f"已处理 {i+1}/{num_iterations} 个传感器数据，检测到 {anomalies_detected} 个异常")

            time.sleep(0.1)  # 模拟数据采集间隔

        self.producer.close()

        print(f"物联网AI监控完成")
        print(f"总处理数据点: {total_processed}")
        print(f"检测到异常: {anomalies_detected}")
        print(f"异常检测率: {anomalies_detected/total_processed*100:.1f}%")

        return {
            'total_processed': total_processed,
            'anomalies_detected': anomalies_detected,
            'detection_rate': anomalies_detected / total_processed
        }

    def predictive_maintenance_simulation(self):
        """预测性维护模拟"""
        print("启动预测性维护模拟...")

        # 模拟设备健康度下降
        device_health = 1.0  # 1.0 = 健康, 0.0 = 故障
        maintenance_alerts = []

        for day in range(30):  # 30天模拟
            # 设备健康度逐渐下降
            device_health -= np.random.uniform(0.01, 0.05)
            device_health = max(0, device_health)

            # 基于健康度生成传感器数据
            sensor_data = self.simulate_sensor_data()
            sensor_data['device_health'] = device_health
            sensor_data['day'] = day

            # AI预测维护需求
            risk_score = 1 - device_health + np.random.normal(0, 0.1)
            risk_score = min(1, max(0, risk_score))

            if risk_score > 0.7:
                alert = {
                    'day': day,
                    'device_id': sensor_data['device_id'],
                    'risk_score': risk_score,
                    'recommended_action': 'schedule_maintenance'
                }
                maintenance_alerts.append(alert)
                print(f"Day {day}: 设备 {sensor_data['device_id']} 维护风险高 (分数: {risk_score:.2f})")

        print(f"预测性维护模拟完成，共生成 {len(maintenance_alerts)} 个维护告警")
        return maintenance_alerts

# 使用示例
if __name__ == "__main__":
    iot_test = IoTAIIngestionTest()

    # AI监控测试
    monitoring_results = iot_test.ai_powered_monitoring(50)
    print("监控结果:", monitoring_results)

    # 预测性维护测试
    maintenance_alerts = iot_test.predictive_maintenance_simulation()
    print(f"维护告警示例: {maintenance_alerts[:3] if maintenance_alerts else '无告警'}")