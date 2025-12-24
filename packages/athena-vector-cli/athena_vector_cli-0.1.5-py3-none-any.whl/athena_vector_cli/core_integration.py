#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core 엔진 통합 모듈
- athena-brain-core 또는 Gateway를 통해 Core 기능 사용
"""

import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

# athena-brain-core 직접 사용 시도
CORE_AVAILABLE = False
try:
    from athena_brain import AthenaBrain
    CORE_AVAILABLE = True
except ImportError:
    # Gateway를 통한 간접 사용
    CORE_AVAILABLE = False


class CoreIntegration:
    """Core 엔진 통합 클래스"""
    
    def __init__(self, use_gateway: bool = False, gateway_url: Optional[str] = None):
        """
        초기화
        
        Args:
            use_gateway: Gateway를 통한 사용 여부 (기본값: False, 직접 사용 시도)
            gateway_url: Gateway URL (기본값: 환경 변수에서 가져옴)
        """
        self.use_gateway = use_gateway
        self.gateway_url = gateway_url or os.getenv("ATHENA_GATEWAY_URL", "http://localhost:8000")
        self.brain = None
        self.gateway_client = None
        
        # 직접 사용 가능하면 직접 사용
        if not use_gateway and CORE_AVAILABLE:
            try:
                self.brain = AthenaBrain()
                print("✅ Core 엔진 직접 사용 (athena-brain-core)", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Core 엔진 직접 사용 실패, Gateway 사용: {e}", file=sys.stderr)
                self.use_gateway = True
        
        # Gateway 사용
        if self.use_gateway or not CORE_AVAILABLE:
            try:
                import httpx
                self.gateway_client = httpx.AsyncClient(timeout=10.0)
                print("✅ Core 엔진 Gateway 통합 사용", file=sys.stderr)
            except ImportError:
                print("⚠️ httpx가 설치되지 않았습니다. 'pip install httpx' 실행", file=sys.stderr)
                self.gateway_client = None
    
    async def search_memory(
        self, 
        query: str, 
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        장기기억 검색
        
        Args:
            query: 검색 쿼리
            limit: 최대 결과 수
            category: 카테고리 필터 (선택)
        
        Returns:
            검색 결과 리스트
        """
        if self.brain:
            # 직접 사용
            try:
                results = await self.brain.search_memory(query, limit=limit)
                return results
            except Exception as e:
                print(f"⚠️ Core 직접 검색 실패: {e}", file=sys.stderr)
                return []
        
        if self.gateway_client:
            # Gateway를 통한 사용
            try:
                response = await self.gateway_client.post(
                    f"{self.gateway_url}/api/search_memory",
                    json={
                        "query": query,
                        "limit": limit,
                        "category": category
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
            except Exception as e:
                print(f"⚠️ Gateway 검색 실패: {e}", file=sys.stderr)
        
        return []
    
    async def store_memory(
        self,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        장기기억 저장
        
        Args:
            content: 저장할 내용
            category: 카테고리
            tags: 태그 리스트
        
        Returns:
            메모리 ID 또는 None
        """
        if self.brain:
            # 직접 사용
            try:
                memory_id = await self.brain.store_memory(content, category, tags)
                return memory_id
            except Exception as e:
                print(f"⚠️ Core 직접 저장 실패: {e}", file=sys.stderr)
                return None
        
        if self.gateway_client:
            # Gateway를 통한 사용
            try:
                response = await self.gateway_client.post(
                    f"{self.gateway_url}/api/store_memory",
                    json={
                        "content": content,
                        "category": category,
                        "tags": tags or []
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("memory_id")
            except Exception as e:
                print(f"⚠️ Gateway 저장 실패: {e}", file=sys.stderr)
        
        return None
    
    async def fuse_inference(
        self,
        *sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        융합 추론 (여러 소스 통합)
        
        Args:
            *sources: 여러 검색 결과 소스
        
        Returns:
            융합된 결과
        """
        # 간단한 융합 로직 (우선순위 기반)
        fused_results = []
        seen_commands = set()
        
        for source in sources:
            if isinstance(source, list):
                for item in source:
                    if isinstance(item, dict):
                        command = item.get("command") or item.get("vector_tag") or item.get("content")
                        if command and command not in seen_commands:
                            seen_commands.add(command)
                            fused_results.append(item)
        
        # 유사도 순으로 정렬
        fused_results.sort(
            key=lambda x: x.get("score", x.get("similarity", 0.0)),
            reverse=True
        )
        
        return {
            "type": "fused",
            "results": fused_results[:5],  # 상위 5개만
            "count": len(fused_results)
        }
    
    async def get_success_rate(self, command: str) -> float:
        """
        과거 성공률 조회
        
        Args:
            command: 명령어
        
        Returns:
            성공률 (0.0 ~ 1.0)
        """
        # 장기기억에서 유사 명령어 검색
        results = await self.search_memory(f"successful execution of {command}", limit=10)
        
        if not results:
            return 0.8  # 기본값 (80%)
        
        # 성공 관련 키워드 확인
        success_count = 0
        total_count = len(results)
        
        for result in results:
            content = result.get("content", "").lower()
            if any(keyword in content for keyword in ["success", "completed", "done", "executed"]):
                success_count += 1
        
        return success_count / total_count if total_count > 0 else 0.8
    
    async def close(self):
        """리소스 정리"""
        if self.gateway_client:
            await self.gateway_client.aclose()

