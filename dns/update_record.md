# 修改解析记录

## Request

### 请求示例

```http
PUT /api/record HTTP/1.1
Authorization: Basic {token}
Content-Type: application/json; charset=utf-8

{
    "id": "85369994254488576",
    "type": 1,
    "host": "www",
    "data": "1.1.1.1",
    "ttl": 600,
    "groupId": "",
    "lineId": "",
    "preference": 10,
    "weight": 1,
    "dominant": false
}
```

### 请求参数

| 参数       | 名称                                    | 类型   | 必选         |
|------------|-----------------------------------------|--------|--------------|
| id         | 记录id                                  | string | YES          |
| type       | 记录类型                                | int    | NO           |
| host       | 主机头                                  | string | 有type必选此项 |
| data       | 记录值                                  | string | 有type必选此项 |
| ttl        | TTL， 1~4294967295                      | int    | NO           |
| groupId    | 分组id,默认分组为空字符串               | string | NO           |
| lineId     | 线路id,参考线路文档                     | string | NO           |
| preference | 优先级 MX 记录有效， 1~55               | int    | NO           |
| weight     | 权重 A CNAME AAAA URL转发 记录有效,1~10 | int    | NO           |
| dominant   | 是否显性URL转发，URL转发记录有效        | bool   | NO           |

### 记录类型

| 记录类型 | 值   |
|----------|------|
| A        | 1    |
| NS       | 2    |
| CNAME    | 5    |
| MX       | 15   |
| TXT      | 16   |
| AAAA     | 28   |
| SRV      | 33   |
| CAA      | 257  |
| URL转发  | 256  |

## Response

### 响应示例

```json
{
    "code":200,
    "msg":"",
    "data":null
}
```