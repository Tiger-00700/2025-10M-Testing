#!/usr/bin/env bash
# Jenkins install script (extracted from book). Run on Debian/Ubuntu systems.

echo "开始安装Jenkins..."

set -euo pipefail

echo "更新系统"
apt-get update

echo "安装 Java"
apt-get install -y openjdk-17-jdk

echo "添加 Jenkins 源"
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | apt-key add -
echo "deb https://pkg.jenkins.io/debian-stable binary/" > /etc/apt/sources.list.d/jenkins.list

apt-get update
apt-get install -y jenkins

systemctl start jenkins
systemctl enable jenkins

echo "Jenkins 已启动"
echo "初始管理员密码:"
cat /var/lib/jenkins/secrets/initialAdminPassword || true
