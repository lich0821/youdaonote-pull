#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
from pathlib import Path

import frontmatter
import yaml

logging.basicConfig(level="ERROR", format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
LOG = logging.getLogger("OB")


def fix_time_with_front_matter(tg_file):
    local_file_path = str(tg_file)
    if local_file_path.endswith(".md.md"):
        os.rename(local_file_path, local_file_path[:-3])
        local_file_path = local_file_path[:-3]

    with open(local_file_path, "r") as f:
        try:
            fm = frontmatter.load(f)
        except yaml.scanner.ScannerError as ex:
            LOG.error(f"识别 markdown frontmatter错误, 忽略. file {f} except: {ex}")
            return

        ctime = fm.metadata.get("created", None)
        mtime = fm.metadata.pop("updated", None)
        if ctime is None:
            LOG.error(f"没有 created 字段: {local_file_path}")
            return

        if mtime is None:
            mtime = ctime

        try:
            os.utime(local_file_path, (ctime.timestamp(), mtime.timestamp()))
            LOG.info(f"正在处理 {local_file_path} 创建时间: {ctime} 更新时间: {mtime}")
        except Exception as ex:
            LOG.error(f"处理失败: {local_file_path} except: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="修复文件的创建时间和修改时间")
    parser.add_argument("-f", "--folder", required=True, help="文件夹路径")
    args = parser.parse_args()

    folder_path = Path(args.folder)

    if folder_path.is_file():
        if folder_path.suffix == ".md":
            fix_time_with_front_matter(folder_path)

        exit(0)

    for tg_file in folder_path.rglob('*.md'):  # 遍历文件夹下的所有 .md 文件
        fix_time_with_front_matter(tg_file)
