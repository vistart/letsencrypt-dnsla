#!/bin/bash

###############################################
# Let's Encrypt DNS.LA 证书管理工具安装脚本
###############################################

set -e

echo "=========================================="
echo "Let's Encrypt DNS.LA 证书管理工具"
echo "安装脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "检查Python版本..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3${NC}"
    echo "请先安装Python 3.7或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓${NC} Python版本: $PYTHON_VERSION"

# 检查pip
echo ""
echo "检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误: 未找到pip3${NC}"
    echo "请先安装pip3"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip已安装"

# 创建虚拟环境（可选）
echo ""
echo "是否创建Python虚拟环境？(推荐)"
echo "  1) 是（推荐）"
echo "  2) 否（直接安装到系统Python）"
read -p "请选择 [1/2]: " choice

case $choice in
    1)
        echo ""
        echo "创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}✓${NC} 虚拟环境已创建并激活"
        ;;
    2)
        echo ""
        echo "将安装到系统Python环境"
        ;;
    *)
        echo -e "${RED}无效选择${NC}"
        exit 1
        ;;
esac

# 安装依赖
echo ""
echo "安装Python依赖..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 依赖安装成功"
else
    echo -e "${RED}✗${NC} 依赖安装失败"
    exit 1
fi

# 创建必要的目录
echo ""
echo "创建必要的目录..."
mkdir -p certs accounts
echo -e "${GREEN}✓${NC} 目录创建成功"

# 配置文件
echo ""
if [ -f "config.yaml" ]; then
    echo -e "${YELLOW}⚠${NC} config.yaml已存在，跳过配置"
else
    echo "配置config.yaml..."
    echo ""
    
    read -p "请输入您的邮箱地址: " email
    read -p "请输入DNS.LA API ID: " api_id
    read -p "请输入DNS.LA API Secret: " api_secret
    read -p "请输入域名（如rho.im）: " domain
    read -p "请输入域名ID: " domain_id
    
    echo ""
    echo "使用测试环境还是生产环境？"
    echo "  1) 测试环境（推荐首次使用）"
    echo "  2) 生产环境"
    read -p "请选择 [1/2]: " env_choice
    
    if [ "$env_choice" = "1" ]; then
        staging="true"
    else
        staging="false"
    fi
    
    # 创建配置文件
    cat > config.yaml << EOF
# Let's Encrypt 配置
letsencrypt:
  # 测试环境（建议首次使用时设为true）
  staging: $staging
  # 联系邮箱
  email: "$email"
  # 证书存储目录
  cert_dir: "./certs"
  # 账户密钥存储目录
  account_dir: "./accounts"

# DNS.LA API 配置
dnsla:
  # API基础URL
  base_url: "https://api.dns.la"
  # API ID（用户名）
  api_id: "$api_id"
  # API Secret（密码）
  api_secret: "$api_secret"
  # DNS记录生效等待时间（秒）
  propagation_seconds: 120

# 域名配置
domains:
  - domain: "$domain"
    domain_id: "$domain_id"
    # 要申请的子域名/通配符
    subdomains:
      - "@"  # 根域名
      # - "www"
      # - "*"  # 通配符域名

# 证书配置
certificate:
  # RSA密钥大小（2048, 3072, 4096）
  key_size: 2048
  # 证书续期提前天数
  renew_days: 30
EOF
    
    echo -e "${GREEN}✓${NC} 配置文件已创建"
fi

# 设置脚本权限
echo ""
echo "设置脚本权限..."
chmod +x main.py
echo -e "${GREEN}✓${NC} 权限设置成功"

# 测试安装
echo ""
echo "测试DNS API连接..."
python3 main.py test-dns

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ 安装完成！${NC}"
    echo "=========================================="
    echo ""
    echo "快速开始:"
    echo ""
    
    if [ "$choice" = "1" ]; then
        echo "  1. 激活虚拟环境:"
        echo "     source venv/bin/activate"
        echo ""
    fi
    
    echo "  2. 颁发证书:"
    echo "     python main.py issue"
    echo ""
    echo "  3. 查看证书:"
    echo "     python main.py info"
    echo ""
    echo "  4. 查看帮助:"
    echo "     python main.py --help"
    echo ""
    echo "详细文档请查看 README.md"
    echo ""
else
    echo ""
    echo -e "${RED}✗ DNS API测试失败${NC}"
    echo "请检查配置文件中的API凭证"
fi
