import os
import sys
from fastapi import APIRouter
from datetime import timedelta
import alibabacloud_oss_v2 as oss   # 注意：原图中写为 'os'，但实际应为 'oss2'，这里修正

router = APIRouter()

# 从环境变量中加载凭证信息
credentials_provider = oss.EnvironmentVariableCredentialsProvider()

# 加载 SDK 默认配置并设置凭证提供者
cfg = oss.config.load_default()
cfg.credentials_provider = credentials_provider

# 指定 Region（例如 cn-beijing）
cfg.region = 'cn-beijing'

# 创建 OSS 客户端
client = oss.Client(cfg)

# OSS 域名和存储桶名称（从环境变量读取，提供默认值）
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.getenv("OSS_BUCKET")

@router.get("/oss/presign")
def chat_endpoint(filename: str):
    # 根据文件扩展名判断 Content-Type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    content_type = content_type_map.get(ext, "application/octet-stream")

    pre_result = client.presign(
        oss.PutObjectRequest(
            bucket=OSS_BUCKET,
            key=filename,
            content_type=content_type,
        ),
        expires=timedelta(seconds=3600)
    )

    # 返回上传 URL 和可访问的图片路径
    return {
        "uploadUrl": pre_result.url.strip(),
        "contentType": content_type,
        "accessUrl": f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{filename}"
    }