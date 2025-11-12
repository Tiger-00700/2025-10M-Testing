# Placeholder example file.

    # 1. 初始化主节点
    kubeadm init --pod-network-cidr=192.168.0.0/16
    # 2. 配置kubectl
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    # 3. 安装网络插件
    kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
    # 4. 加入工作节点
    kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
