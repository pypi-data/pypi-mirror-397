
import os
from xmov_oss.core import XmovOSSBucket
from xmov_oss.schema import OSSConfigWithSecret
from xmov_oss.args import parse_args
from xmov_oss.utils import download
import urllib.parse
from pprint import pprint


def main():
    args = parse_args()
    config = OSSConfigWithSecret(secret=args.secret)
    bucket = XmovOSSBucket(config)
    remote_file_path = args.remote_file_path

    if args.action == "upload":
        file_info = bucket.upload(args.local_file_path, args.remote_file_path, args.overwrite)
        pprint(file_info)
    elif args.action == "download":
        if remote_file_path.startswith("https://"):
            parse_result = urllib.parse.urlparse(args.remote_file_path)
            if parse_result.netloc != config.OSS_BASE_URL:
                # 使用原始地址
                download(args.remote_file_path)
            else:
                remote_path = parse_result.path
                bucket.download(remote_path)
        elif remote_file_path.startswith("oss://"):
            parse_result = urllib.parse.urlparse(args.remote_file_path)
            if parse_result.netloc != config.OSS_BUCKET_NAME:
                raise ValueError(f"无效的地址: {args.remote_file_path}, 当前仅支持 {config.OSS_BUCKET_NAME} 桶")
            remote_path = parse_result.path
            bucket.download(remote_path)
        else:
            remote_path = args.remote_file_path
            bucket.download(remote_path)

    elif args.action == "ls":
        data = bucket.ls(args.remote_file_path)
        pprint(data)
    
    elif args.action == "doc":
        docs = """
# 设置密码, 如果不使用export, 需要在命令行使用 -p ***指定
export XMOV_OSS_SECRET=***

# 显示列表
xmov_oss ls tmp/xmov_oss

# 上传文件
xmov_oss upload README.md 

# 下载oss
xmov_oss download -r tmp/xmov_oss/README.md

# 下载任意文件，可以不是oss链接
xmov_oss download https://public-xmov.oss-cn-hangzhou.aliyuncs.com/tmp/xmov_oss/README.md
        """
        print(docs)


if __name__ == "__main__":
    main()