#!/bin/bash

###########################################
# Let's Encrypt 证书申请和管理脚本
# 支持: macOS, Linux
# 用途: Web HTTPS + 数据库 SSL/TLS
###########################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_BASE_DIR="${CERT_BASE_DIR:-/etc/letsencrypt}"
LOG_FILE="${SCRIPT_DIR}/letsencrypt.log"

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_info "以root用户运行"
        return 0
    else
        print_warn "非root用户运行，某些操作可能需要sudo权限"
        return 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "检测到操作系统: macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "检测到操作系统: Linux"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 安装certbot
install_certbot() {
    print_info "检查certbot安装状态..."
    
    if command -v certbot &> /dev/null; then
        print_info "certbot已安装: $(certbot --version)"
        return 0
    fi
    
    print_warn "certbot未安装，开始安装..."
    
    if [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            print_error "需要安装Homebrew: https://brew.sh"
            exit 1
        fi
        brew install certbot
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y certbot
        else
            print_error "不支持的包管理器，请手动安装certbot"
            exit 1
        fi
    fi
    
    print_info "certbot安装完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
Let's Encrypt 证书申请和管理脚本

用法:
    $0 [选项]

选项:
    -d, --domain DOMAIN          域名 (必需，可多次使用)
    -w, --wildcard              申请通配符证书 (*.domain.com)
    -m, --email EMAIL           联系邮箱 (必需)
    -p, --webroot PATH          Webroot路径 (HTTP-01验证)
    --standalone                使用standalone模式 (HTTP-01验证)
    --dns-plugin PLUGIN         DNS插件名称 (DNS-01验证，通配符必需)
    --export-db                 导出数据库兼容格式证书
    --cert-name NAME            证书名称 (默认使用主域名)
    --staging                   使用Let's Encrypt测试服务器
    -h, --help                  显示此帮助信息

验证方式:
    1. HTTP-01 (webroot): 适用于普通域名，需要可访问的web目录
       示例: $0 -d example.com -d www.example.com -m admin@example.com -p /var/www/html
    
    2. HTTP-01 (standalone): 适用于临时停止web服务器
       示例: $0 -d example.com -m admin@example.com --standalone
    
    3. DNS-01: 适用于通配符域名，需要DNS插件
       示例: $0 -d example.com -w -m admin@example.com --dns-plugin cloudflare

常用DNS插件:
    - cloudflare: certbot-dns-cloudflare
    - route53: certbot-dns-route53
    - cloudns: certbot-dns-cloudns
    - dnspod: certbot-dns-dnspod

数据库使用:
    使用 --export-db 选项会额外生成数据库兼容的证书文件:
    - server-cert.pem (服务器证书)
    - server-key.pem (私钥)
    - ca-bundle.pem (CA证书链)

示例:
    # 申请单个域名证书 (webroot)
    $0 -d example.com -m admin@example.com -p /var/www/html
    
    # 申请多个域名证书
    $0 -d example.com -d www.example.com -d api.example.com -m admin@example.com -p /var/www/html
    
    # 申请通配符证书 (需要DNS插件)
    $0 -d example.com -w -m admin@example.com --dns-plugin cloudflare
    
    # 申请证书并导出数据库格式
    $0 -d example.com -m admin@example.com -p /var/www/html --export-db

EOF
}

# 参数解析
parse_args() {
    DOMAINS=()
    WILDCARD=false
    EMAIL=""
    WEBROOT=""
    STANDALONE=false
    DNS_PLUGIN=""
    EXPORT_DB=false
    CERT_NAME=""
    STAGING=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAINS+=("$2")
                shift 2
                ;;
            -w|--wildcard)
                WILDCARD=true
                shift
                ;;
            -m|--email)
                EMAIL="$2"
                shift 2
                ;;
            -p|--webroot)
                WEBROOT="$2"
                shift 2
                ;;
            --standalone)
                STANDALONE=true
                shift
                ;;
            --dns-plugin)
                DNS_PLUGIN="$2"
                shift 2
                ;;
            --export-db)
                EXPORT_DB=true
                shift
                ;;
            --cert-name)
                CERT_NAME="$2"
                shift 2
                ;;
            --staging)
                STAGING=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证必需参数
    if [[ ${#DOMAINS[@]} -eq 0 ]]; then
        print_error "必须指定至少一个域名 (-d)"
        show_help
        exit 1
    fi
    
    if [[ -z "$EMAIL" ]]; then
        print_error "必须指定邮箱地址 (-m)"
        show_help
        exit 1
    fi
    
    # 验证验证方式
    if [[ "$WILDCARD" == true ]] && [[ -z "$DNS_PLUGIN" ]]; then
        print_error "通配符证书必须使用DNS验证方式 (--dns-plugin)"
        exit 1
    fi
    
    if [[ -n "$WEBROOT" ]] && [[ "$STANDALONE" == true ]]; then
        print_error "不能同时使用webroot和standalone模式"
        exit 1
    fi
    
    if [[ -z "$DNS_PLUGIN" ]] && [[ -z "$WEBROOT" ]] && [[ "$STANDALONE" == false ]]; then
        print_error "必须指定验证方式: --webroot, --standalone, 或 --dns-plugin"
        exit 1
    fi
}

# 构建certbot命令
build_certbot_command() {
    local cmd="certbot certonly"
    
    # 非交互模式
    cmd="$cmd --non-interactive --agree-tos"
    
    # 邮箱
    cmd="$cmd --email $EMAIL"
    
    # 证书名称
    if [[ -n "$CERT_NAME" ]]; then
        cmd="$cmd --cert-name $CERT_NAME"
    fi
    
    # 域名
    for domain in "${DOMAINS[@]}"; do
        if [[ "$WILDCARD" == true ]]; then
            cmd="$cmd -d $domain -d *.$domain"
        else
            cmd="$cmd -d $domain"
        fi
    done
    
    # 验证方式
    if [[ -n "$DNS_PLUGIN" ]]; then
        cmd="$cmd --dns-$DNS_PLUGIN"
    elif [[ -n "$WEBROOT" ]]; then
        cmd="$cmd --webroot -w $WEBROOT"
    elif [[ "$STANDALONE" == true ]]; then
        cmd="$cmd --standalone"
    fi
    
    # 测试模式
    if [[ "$STAGING" == true ]]; then
        cmd="$cmd --staging"
        print_warn "使用测试服务器模式"
    fi
    
    echo "$cmd"
}

# 申请证书
request_certificate() {
    print_info "开始申请证书..."
    
    local cmd=$(build_certbot_command)
    print_info "执行命令: $cmd"
    
    if eval "$cmd"; then
        print_info "证书申请成功！"
        return 0
    else
        print_error "证书申请失败"
        return 1
    fi
}

# 获取证书路径
get_cert_path() {
    local domain="${DOMAINS[0]}"
    if [[ -n "$CERT_NAME" ]]; then
        domain="$CERT_NAME"
    fi
    
    echo "$CERT_BASE_DIR/live/$domain"
}

# 导出数据库兼容格式
export_db_certs() {
    local cert_path=$(get_cert_path)
    
    if [[ ! -d "$cert_path" ]]; then
        print_error "证书目录不存在: $cert_path"
        return 1
    fi
    
    print_info "导出数据库兼容格式证书..."
    
    local export_dir="$SCRIPT_DIR/db-certs"
    mkdir -p "$export_dir"
    
    # 复制证书文件
    cp "$cert_path/fullchain.pem" "$export_dir/server-cert.pem"
    cp "$cert_path/privkey.pem" "$export_dir/server-key.pem"
    cp "$cert_path/chain.pem" "$export_dir/ca-bundle.pem"
    
    # 设置权限
    chmod 644 "$export_dir/server-cert.pem"
    chmod 600 "$export_dir/server-key.pem"
    chmod 644 "$export_dir/ca-bundle.pem"
    
    print_info "数据库证书已导出到: $export_dir"
    echo ""
    print_info "数据库配置示例:"
    echo ""
    echo "MySQL/MariaDB:"
    echo "  ssl-ca=$export_dir/ca-bundle.pem"
    echo "  ssl-cert=$export_dir/server-cert.pem"
    echo "  ssl-key=$export_dir/server-key.pem"
    echo ""
    echo "PostgreSQL:"
    echo "  ssl_ca_file = '$export_dir/ca-bundle.pem'"
    echo "  ssl_cert_file = '$export_dir/server-cert.pem'"
    echo "  ssl_key_file = '$export_dir/server-key.pem'"
    echo ""
    echo "MongoDB:"
    echo "  net:"
    echo "    tls:"
    echo "      mode: requireTLS"
    echo "      certificateKeyFile: $export_dir/server-combined.pem"
    echo "      CAFile: $export_dir/ca-bundle.pem"
    echo ""
    
    # MongoDB需要合并证书和私钥
    cat "$export_dir/server-cert.pem" "$export_dir/server-key.pem" > "$export_dir/server-combined.pem"
    chmod 600 "$export_dir/server-combined.pem"
    print_info "MongoDB合并证书已生成: $export_dir/server-combined.pem"
    
    echo ""
    echo "Redis:"
    echo "  tls-cert-file $export_dir/server-cert.pem"
    echo "  tls-key-file $export_dir/server-key.pem"
    echo "  tls-ca-cert-file $export_dir/ca-bundle.pem"
}

# 显示证书信息
show_cert_info() {
    local cert_path=$(get_cert_path)
    
    if [[ ! -d "$cert_path" ]]; then
        print_error "证书目录不存在: $cert_path"
        return 1
    fi
    
    print_info "证书信息:"
    echo ""
    echo "证书路径: $cert_path"
    echo ""
    echo "证书文件:"
    echo "  - fullchain.pem (完整证书链，用于Web服务器)"
    echo "  - cert.pem (服务器证书)"
    echo "  - chain.pem (中间证书)"
    echo "  - privkey.pem (私钥)"
    echo ""
    
    # 显示证书详细信息
    print_info "证书详细信息:"
    openssl x509 -in "$cert_path/cert.pem" -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:" || true
    
    echo ""
    print_info "Web服务器配置示例:"
    echo ""
    echo "Nginx:"
    echo "  ssl_certificate $cert_path/fullchain.pem;"
    echo "  ssl_certificate_key $cert_path/privkey.pem;"
    echo ""
    echo "Apache:"
    echo "  SSLCertificateFile $cert_path/cert.pem"
    echo "  SSLCertificateKeyFile $cert_path/privkey.pem"
    echo "  SSLCertificateChainFile $cert_path/chain.pem"
}

# 设置自动续期
setup_auto_renewal() {
    print_info "设置自动续期..."
    
    # certbot会自动设置定时任务
    if certbot renew --dry-run; then
        print_info "自动续期测试成功"
        echo ""
        print_info "Let's Encrypt证书有效期为90天"
        print_info "certbot已自动配置续期任务，会在证书到期前30天自动续期"
        echo ""
        
        if [[ "$OS" == "linux" ]]; then
            print_info "查看续期定时任务:"
            echo "  systemctl list-timers | grep certbot"
            echo "  或: crontab -l | grep certbot"
        elif [[ "$OS" == "macos" ]]; then
            print_info "在macOS上，建议手动添加定时任务:"
            echo "  crontab -e"
            echo "  添加: 0 0,12 * * * certbot renew --quiet"
        fi
        
        if [[ "$EXPORT_DB" == true ]]; then
            echo ""
            print_warn "注意: 续期后需要重新导出数据库证书"
            print_info "建议创建续期钩子脚本"
        fi
    else
        print_error "自动续期测试失败"
        return 1
    fi
}

# 主函数
main() {
    print_info "Let's Encrypt 证书申请脚本启动"
    echo ""
    
    # 检测环境
    detect_os
    check_root
    
    # 解析参数
    parse_args "$@"
    
    # 安装certbot
    install_certbot
    
    echo ""
    print_info "配置信息:"
    echo "  域名: ${DOMAINS[*]}"
    echo "  通配符: $WILDCARD"
    echo "  邮箱: $EMAIL"
    [[ -n "$WEBROOT" ]] && echo "  Webroot: $WEBROOT"
    [[ "$STANDALONE" == true ]] && echo "  模式: Standalone"
    [[ -n "$DNS_PLUGIN" ]] && echo "  DNS插件: $DNS_PLUGIN"
    echo "  导出数据库格式: $EXPORT_DB"
    echo ""
    
    # 申请证书
    if ! request_certificate; then
        exit 1
    fi
    
    echo ""
    
    # 显示证书信息
    show_cert_info
    
    # 导出数据库证书
    if [[ "$EXPORT_DB" == true ]]; then
        echo ""
        export_db_certs
    fi
    
    echo ""
    
    # 设置自动续期
    setup_auto_renewal
    
    echo ""
    print_info "完成！证书已成功申请"
}

# 运行主函数
main "$@"
