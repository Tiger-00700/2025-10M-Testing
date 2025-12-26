# 环境管理与基础设施即代码

## 概述

环境管理是CI/CD流水线成功的关键因素。本文档详细介绍大数据测试环境的管理策略、基础设施即代码(IaC)实践，以及自动化部署方案。

## 环境管理策略

### 环境分类体系

#### 1. 开发环境 (Development Environment)
```yaml
development_environment:
  purpose: "开发者日常开发和调试"
  lifecycle: "按需创建，长期运行"
  access_control: "开发者个人权限"
  data_strategy: "模拟数据和测试数据"
  backup_policy: "可选备份"
  cost_optimization: "按需付费实例"
```

#### 2. 持续集成环境 (CI Environment)
```yaml
ci_environment:
  purpose: "自动化构建和基础测试"
  lifecycle: "流水线触发，按需创建"
  access_control: "自动化工具权限"
  data_strategy: "自动化生成测试数据"
  backup_policy: "无备份需求"
  cost_optimization: "竞价实例，快速启动"
```

#### 3. 测试环境 (Testing Environment)
```yaml
testing_environment:
  purpose: "集成测试和系统测试"
  lifecycle: "按分支/版本创建"
  access_control: "测试团队权限"
  data_strategy: "生产数据脱敏副本"
  backup_policy: "定期备份"
  cost_optimization: "预留实例，稳定运行"
```

#### 4. 预发布环境 (Staging Environment)
```yaml
staging_environment:
  purpose: "验收测试和最终验证"
  lifecycle: "发布前创建，验证后销毁"
  access_control: "业务团队和运维权限"
  data_strategy: "生产数据实时同步"
  backup_policy: "完整备份"
  cost_optimization: "按需扩展，成本控制"
```

#### 5. 生产环境 (Production Environment)
```yaml
production_environment:
  purpose: "最终用户服务"
  lifecycle: "7x24小时运行"
  access_control: "最小权限原则"
  data_strategy: "生产数据"
  backup_policy: "多重备份策略"
  cost_optimization: "高可用架构，成本效益平衡"
```

### 环境隔离策略

#### 网络隔离
```yaml
network_isolation:
  vpc_design:
    - "每个环境独立VPC"
    - "VPC间通过VPC对等连接或Transit Gateway通信"
    - "安全组和网络ACL精细控制"
  dns_strategy:
    - "环境级域名后缀区分"
    - "内部DNS服务隔离"
    - "跨环境服务发现机制"
```

#### 数据隔离
```yaml
data_isolation:
  database_strategy:
    - "环境级独立数据库实例"
    - "数据脱敏和匿名化处理"
    - "跨环境数据同步机制"
  storage_strategy:
    - "环境级独立存储桶"
    - "对象版本控制和生命周期管理"
    - "跨环境数据复制"
```

#### 权限隔离
```yaml
permission_isolation:
  iam_strategy:
    - "环境级IAM角色分离"
    - "最小权限原则"
    - "临时权限和会话管理"
  access_control:
    - "多因素认证"
    - "访问日志审计"
    - "异常行为检测"
```

## 基础设施即代码实践

### Terraform基础架构

#### 目录结构
```
infrastructure/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── monitoring/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── global/
└── terraform.tfvars
```

#### VPC模块设计
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name        = "${var.environment}-private-${count.index + 1}"
    Environment = var.environment
    Type        = "private"
  }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name        = "${var.environment}-public-${count.index + 1}"
    Environment = var.environment
    Type        = "public"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "main" {
  count         = length(var.public_subnets)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name        = "${var.environment}-nat-${count.index + 1}"
    Environment = var.environment
  }
}
```

#### EKS集群配置
```hcl
# modules/eks/main.tf
resource "aws_eks_cluster" "main" {
  name     = "${var.environment}-cluster"
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.allowed_cidrs
  }

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]

  tags = {
    Name        = "${var.environment}-eks-cluster"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.environment}-node-group"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = var.desired_capacity
    max_size     = var.max_capacity
    min_size     = var.min_capacity
  }

  instance_types = var.instance_types
  capacity_type  = var.capacity_type

  update_config {
    max_unavailable = 1
  }

  tags = {
    Name        = "${var.environment}-node-group"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

#### 环境变量配置
```hcl
# environments/dev/terraform.tfvars
environment = "dev"

vpc_config = {
  cidr_block = "10.0.0.0/16"
  private_subnets = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]
  public_subnets = [
    "10.0.101.0/24",
    "10.0.102.0/24",
    "10.0.103.0/24"
  ]
  availability_zones = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c"
  ]
}

eks_config = {
  kubernetes_version = "1.27"
  desired_capacity   = 2
  min_capacity      = 1
  max_capacity      = 10
  instance_types    = ["t3.medium"]
  capacity_type     = "ON_DEMAND"
}
```

### Ansible配置管理

#### 目录结构
```
ansible/
├── inventories/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── playbooks/
│   ├── deploy.yml
│   ├── configure.yml
│   └── rollback.yml
├── roles/
│   ├── common/
│   ├── application/
│   ├── database/
│   └── monitoring/
├── group_vars/
├── host_vars/
└── ansible.cfg
```

#### 应用部署Playbook
```yaml
# playbooks/deploy.yml
---
- name: Deploy Big Data Testing Application
  hosts: application_servers
  become: yes
  vars_files:
    - "../group_vars/{{ environment }}.yml"
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

    - name: Install required packages
      package:
        name: "{{ item }}"
        state: present
      loop: "{{ required_packages }}"

  roles:
    - common
    - application
    - monitoring

  post_tasks:
    - name: Wait for application to be ready
      uri:
        url: "http://localhost:{{ application_port }}/health"
        status_code: 200
      register: health_check
      until: health_check.status == 200
      retries: 30
      delay: 10

    - name: Notify deployment completion
      slack:
        token: "{{ slack_token }}"
        msg: "Application deployed successfully to {{ environment }}"
        channel: "#deployments"
      when: slack_notification | default(false)
```

#### 通用角色定义
```yaml
# roles/common/tasks/main.yml
---
- name: Set timezone
  timezone:
    name: "{{ timezone | default('UTC') }}"

- name: Configure NTP
  package:
    name: ntp
    state: present
  when: configure_ntp | default(true)

- name: Configure firewall
  ufw:
    state: enabled
    policy: deny
  when: configure_firewall | default(true)

- name: Create application user
  user:
    name: "{{ application_user }}"
    system: yes
    shell: /bin/bash
    home: "{{ application_home }}"

- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ application_user }}"
    group: "{{ application_user }}"
    mode: '0755'
  loop:
    - "{{ application_home }}"
    - "{{ application_log_dir }}"
    - "{{ application_config_dir }}"
```

### Helm Chart设计

#### Chart结构
```
helm/
├── bigdata-testing/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml
│   │   └── _helpers.tpl
│   └── charts/
└── requirements.yaml
```

#### 部署模板
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "bigdata-testing.fullname" . }}
  labels:
    {{- include "bigdata-testing.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "bigdata-testing.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "bigdata-testing.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "bigdata-testing.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: {{ .Values.healthCheck.path }}
              port: http
            initialDelaySeconds: {{ .Values.healthCheck.initialDelaySeconds }}
            periodSeconds: {{ .Values.healthCheck.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.healthCheck.path }}
              port: http
            initialDelaySeconds: {{ .Values.healthCheck.initialDelaySeconds }}
            periodSeconds: {{ .Values.healthCheck.periodSeconds }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          env:
            {{- range .Values.env }}
            - name: {{ .name }}
              value: {{ .value | quote }}
            {{- end }}
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: logs
              mountPath: /app/logs
      volumes:
        - name: config
          configMap:
            name: {{ include "bigdata-testing.fullname" . }}
        - name: logs
          emptyDir: {}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

#### 环境特定配置
```yaml
# values-dev.yaml
replicaCount: 1

image:
  repository: registry.company.com/bigdata-testing
  tag: "latest"
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8080

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 100m
    memory: 256Mi

env:
  - name: SPRING_PROFILES_ACTIVE
    value: "dev"
  - name: DATABASE_URL
    value: "jdbc:postgresql://dev-db:5432/testdb"

healthCheck:
  path: "/actuator/health"
  initialDelaySeconds: 30
  periodSeconds: 10

ingress:
  enabled: false
```

## 环境自动化管理

### 环境创建流程

#### 1. 基础设施准备
```bash
#!/bin/bash
# create_environment.sh

ENVIRONMENT=$1

# 验证参数
if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment>"
    exit 1
fi

# 初始化Terraform
cd infrastructure/environments/$ENVIRONMENT
terraform init

# 计划部署
terraform plan -out=tfplan

# 应用配置
terraform apply tfplan

# 验证部署
terraform output > environment_outputs.json
```

#### 2. 应用部署
```bash
#!/bin/bash
# deploy_application.sh

ENVIRONMENT=$1
VERSION=$2

# 验证参数
if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <environment> <version>"
    exit 1
fi

# 切换到对应环境
cd ansible/environments/$ENVIRONMENT

# 部署应用
ansible-playbook -i inventories/$ENVIRONMENT \
                 --extra-vars "version=$VERSION" \
                 playbooks/deploy.yml

# 验证部署
ansible-playbook -i inventories/$ENVIRONMENT \
                 playbooks/verify.yml
```

#### 3. 数据准备
```bash
#!/bin/bash
# prepare_data.sh

ENVIRONMENT=$1

# 创建数据库
ansible-playbook -i inventories/$ENVIRONMENT \
                 --tags database \
                 playbooks/configure.yml

# 初始化数据
ansible-playbook -i inventories/$ENVIRONMENT \
                 --tags data \
                 --extra-vars "data_source=production" \
                 playbooks/configure.yml

# 验证数据
ansible-playbook -i inventories/$ENVIRONMENT \
                 playbooks/verify_data.yml
```

### 环境清理流程

#### 1. 安全清理
```bash
#!/bin/bash
# cleanup_environment.sh

ENVIRONMENT=$1

# 验证环境状态
ansible-playbook -i inventories/$ENVIRONMENT \
                 playbooks/check_environment.yml

# 备份重要数据
ansible-playbook -i inventories/$ENVIRONMENT \
                 --tags backup \
                 playbooks/maintenance.yml

# 停止服务
ansible-playbook -i inventories/$ENVIRONMENT \
                 --tags stop \
                 playbooks/deploy.yml

# 清理资源
cd infrastructure/environments/$ENVIRONMENT
terraform destroy -auto-approve

# 验证清理
ansible-playbook -i inventories/$ENVIRONMENT \
                 playbooks/verify_cleanup.yml
```

## 监控和告警

### 基础设施监控

#### CloudWatch告警配置
```yaml
cloudwatch_alarms:
  - alarm_name: "HighCPUUtilization"
    comparison_operator: "GreaterThanThreshold"
    evaluation_periods: 2
    metric_name: "CPUUtilization"
    namespace: "AWS/EC2"
    period: 300
    statistic: "Average"
    threshold: 80.0
    alarm_actions:
      - "arn:aws:sns:region:account:alarm-topic"

  - alarm_name: "LowStorageSpace"
    comparison_operator: "LessThanThreshold"
    evaluation_periods: 1
    metric_name: "FreeStorageSpace"
    namespace: "AWS/RDS"
    period: 300
    statistic: "Average"
    threshold: 20.0
    unit: "Percent"
```

#### Prometheus监控配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  - job_name: 'kubernetes-nodes'
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics

  - job_name: 'bigdata-testing'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: replace
        target_label: app
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_container_port_number]
        action: replace
        target_label: port
```

### 告警规则配置
```yaml
# alert_rules.yml
groups:
  - name: bigdata-testing
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High request latency (instance {{ $labels.instance }})"
          description: "Request latency is {{ $value }}s for the last 10 minutes."

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate (instance {{ $labels.instance }})"
          description: "Error rate is {{ $value }} for the last 5 minutes."

      - alert: LowDiskSpace
        expr: (disk_free_bytes / disk_total_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space (instance {{ $labels.instance }})"
          description: "Disk space is below 10%."

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[5m]) > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Pod crash looping (pod {{ $labels.pod }})"
          description: "Pod {{ $labels.pod }} is crash looping."
```

通过系统化的环境管理和基础设施即代码实践，大数据测试团队能够实现高效、可靠、可扩展的环境管理，为CI/CD流水线的成功运行提供坚实的基础保障。