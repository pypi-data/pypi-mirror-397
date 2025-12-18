#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.env を読み込むためのユーティリティクラス。

`_tool_/test/config.env` で使っている読み込み・プレースホルダ置換・AWSリージョン設定処理を
ライブラリとして提供する。
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from dotenv import dotenv_values


class EnvConfigLoader:
    """
    dotenv 形式の設定ファイルを読み込むユーティリティ。
    
    - キーごとのデフォルト値マージ
    - %YYYYMMDDhhmmssSSS% 形式のプレースホルダ置換
    - AWS_REGION の環境変数設定（boto3の NoRegionError 回避用）
    をひとまとめにする。
    """

    @classmethod
    def load(cls, config_path: Path) -> Dict[str, str]:
        """
        dotenv 形式のファイルを読み込む。
        
        Args:
            config_path: 設定ファイルへのパス
        
        Returns:
            キーと値の辞書（値が None の項目は除外）
        """
        config_path = Path(config_path)
        if not config_path.exists():
            return {}
        return {
            key: value
            for key, value in dotenv_values(dotenv_path=str(config_path)).items()
            if value is not None
        }

    @staticmethod
    def replace_placeholders(value: str, now: datetime) -> str:
        """
        %YYYYMMDDhhmmssSSS% のようなプレースホルダを日時で置換する。
        部分指定（%YYYYMMDD% など）も置換可能。
        """
        if not value:
            return value

        def _repl(match: re.Match) -> str:
            token = match.group(1)
            replacements = {
                "YYYY": f"{now:%Y}",
                "MM": f"{now:%m}",
                "DD": f"{now:%d}",
                "hh": f"{now:%H}",
                "mm": f"{now:%M}",
                "ss": f"{now:%S}",
                "SSS": f"{now.microsecond // 1000:03d}",
            }
            result = token
            for key, val in replacements.items():
                result = result.replace(key, val)
            return result

        return re.sub(r"%([YMDhmsS]+)%", _repl, value)

    @classmethod
    def resolve(
        cls,
        raw_config: Dict[str, str],
        *,
        defaults: Optional[Dict[str, str]] = None,
        placeholder_keys: Optional[Iterable[str]] = None,
        now: Optional[datetime] = None,
        apply_region_env: bool = True,
    ) -> Dict[str, str]:
        """
        読み込んだ設定にデフォルト値をマージし、必要なキーのプレースホルダを置換する。
        
        Args:
            raw_config: `load` で読み込んだ設定
            defaults: デフォルト値（raw_config のキーで上書きされる）
            placeholder_keys: プレースホルダ置換を適用するキー一覧
            now: プレースホルダ置換に使用する日時（未指定なら現在時刻）
            apply_region_env: AWS_REGION があれば環境変数にセットするか
        
        Returns:
            置換・マージ後の設定辞書
        """
        merged = {**(defaults or {}), **(raw_config or {})}
        now = now or datetime.now()

        placeholder_keys = set(placeholder_keys or [])
        for key in placeholder_keys:
            if key in merged:
                merged[key] = cls.replace_placeholders(merged.get(key, ""), now)

        if apply_region_env:
            region = merged.get("AWS_REGION")
            if region:
                os.environ.setdefault("AWS_REGION", region)
                os.environ.setdefault("AWS_DEFAULT_REGION", region)

        return merged


