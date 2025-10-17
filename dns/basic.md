## 开发必读

### 基础域名
```
https://api.dns.la
```

### Basic 认证

我的账户 -> API 密钥 中获取 `APIID` 和 `APISecret`

```
APIID=myApiId
APISecret=mySecret
```

生成 Basic 令牌

```
# 用冒号连接 APIID APISecret
str = "myApiId:mySecret"
token = base64Encode(str)
```

在请求头中添加 Basic 认证令牌
```
Authorization: Basic {token}
```
响应示例
相应格式 application/json
```json
{
	"code":200,
	"msg":"",
	"data":{}
}
```

HTTP 状态码

|状态码|	说明|
|----|----|
|200|	请求正常|
|401|	认证失败|

业务 Code 码

|Code| 	说明     |
|----|---------|
|200| 	成功     |
|400| 	请求错误   |
|500| 	内部错误   |
|6xx| 	参见 msg |