#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 파일 관리 모듈
- ~/.athena/config.yaml 또는 .athenarc 파일 읽기
- 환경 변수와 설정 파일 통합
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Path:
    """
    설정 파일 경로 가져오기
    
    Returns:
        설정 파일 경로
    """
    # 1. 홈 디렉토리의 .athena/config.yaml
    home = Path.home()
    config_dir = home / ".athena"
    config_file = config_dir / "config.yaml"
    
    # 2. 현재 디렉토리의 .athenarc
    current_dir = Path.cwd()
    athenarc = current_dir / ".athenarc"
    
    # 우선순위: .athenarc > ~/.athena/config.yaml
    if athenarc.exists():
        return athenarc
    elif config_file.exists():
        return config_file
    else:
        # 기본값: 홈 디렉토리 설정 파일
        return config_file


def load_config() -> Dict[str, Any]:
    """
    설정 파일 로드
    
    Returns:
        설정 딕셔너리
    """
    config = {}
    config_path = get_config_path()
    
    # 설정 파일이 없으면 기본값 반환
    if not config_path.exists():
        return get_default_config()
    
    # YAML 파일 읽기
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except ImportError:
        # pyyaml이 없으면 JSON으로 시도
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f) or {}
        except Exception as e:
            print(f"⚠️ 설정 파일 읽기 실패: {e}", file=sys.stderr)
            return get_default_config()
    except Exception as e:
        print(f"⚠️ 설정 파일 읽기 실패: {e}", file=sys.stderr)
        return get_default_config()
    
    # 기본값과 병합
    default_config = get_default_config()
    default_config.update(config)
    
    return default_config


def get_default_config() -> Dict[str, Any]:
    """
    기본 설정 가져오기
    
    Returns:
        기본 설정 딕셔너리
    """
    return {
        "qdrant": {
            "url": os.getenv("VPS_QDRANT_URL") or os.getenv("QDRANT_URL") or None,
            "collection": os.getenv("QDRANT_COLLECTION_NAME", "command_vectors"),
            "timeout": 3.0
        },
        "model": {
            "name": os.getenv("SENTENCE_TRANSFORMER_MODEL", "snunlp/KR-SBERT-V40K-klueNLI-aug-sts")
        },
        "search": {
            "similarity_threshold": 0.85,
            "max_results": 5
        },
        "execution": {
            "confirm_by_default": True,
            "timeout": 30
        }
    }


def get_qdrant_url() -> Optional[str]:
    """
    Qdrant URL 가져오기 (설정 파일 우선)
    
    Returns:
        Qdrant URL 또는 None
    """
    config = load_config()
    return config.get("qdrant", {}).get("url")


def get_collection_name() -> str:
    """
    컬렉션 이름 가져오기
    
    Returns:
        컬렉션 이름
    """
    config = load_config()
    return config.get("qdrant", {}).get("collection", "command_vectors")


def get_similarity_threshold() -> float:
    """
    유사도 임계값 가져오기
    
    Returns:
        유사도 임계값
    """
    config = load_config()
    return config.get("search", {}).get("similarity_threshold", 0.85)


def create_default_config_file(path: Optional[Path] = None) -> Path:
    """
    기본 설정 파일 생성
    
    Args:
        path: 설정 파일 경로 (None이면 기본 경로 사용)
        
    Returns:
        생성된 설정 파일 경로
    """
    if path is None:
        path = get_config_path()
    
    # 디렉토리 생성
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 기본 설정 내용
    default_config = {
        "qdrant": {
            "url": "http://localhost:6333",
            "collection": "command_vectors",
            "timeout": 3.0
        },
        "model": {
            "name": "snunlp/KR-SBERT-V40K-klueNLI-aug-sts"
        },
        "search": {
            "similarity_threshold": 0.85,
            "max_results": 5
        },
        "execution": {
            "confirm_by_default": True,
            "timeout": 30
        }
    }
    
    # YAML로 저장 시도
    try:
        import yaml
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    except ImportError:
        # pyyaml이 없으면 JSON으로 저장
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    return path


