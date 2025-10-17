# 添加域名

## Request

### 请求示例

```http
POST /api/domain HTTP/1.1
Authorization: Basic {token}
Content-Type: application/json; charset=utf-8

{
    "groupId": "",
    "domain": "test.com"
}
```

### 请求参数

| 参数    | 名称         | 类型   | 必选 |
|---------|--------------|--------|------|
| domain  | 域名         | string | YES  |
| groupId | 分组id,空为未分组 | string | NO   |

## Response

### 响应示例

```json
{
    "code":200,
    "msg":"",
    "data":{
        "id":"85369994254488576"
    }
}
```