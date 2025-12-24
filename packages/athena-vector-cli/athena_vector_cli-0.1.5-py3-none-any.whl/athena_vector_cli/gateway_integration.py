#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gateway 통합 모듈
- Gateway의 98개 도구를 HTTP API로 사용
"""

import os
import sys
from typing import Dict, List, Optional, Any
import json

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️ httpx가 설치되지 않았습니다. Gateway 통합을 사용하려면 'pip install httpx' 실행", file=sys.stderr)


class GatewayIntegration:
    """Gateway 통합 클래스"""
    
    def __init__(self, gateway_url: Optional[str] = None):
        """
        초기화
        
        Args:
            gateway_url: Gateway URL (기본값: 환경 변수에서 가져옴)
        """
        self.gateway_url = gateway_url or os.getenv("ATHENA_GATEWAY_URL", "http://localhost:8000")
        self.client = None
        
        if HTTPX_AVAILABLE:
            try:
                self.client = httpx.AsyncClient(timeout=10.0)
                print(f"✅ Gateway 통합 초기화: {self.gateway_url}", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Gateway 클라이언트 초기화 실패: {e}", file=sys.stderr)
        else:
            print("⚠️ httpx가 설치되지 않아 Gateway 통합을 사용할 수 없습니다.", file=sys.stderr)
    
    async def analyze_task(
        self,
        task: str,
        domain: str = "general",
        use_intelligent_routing: bool = True
    ) -> Dict[str, Any]:
        """
        작업 분석 (Gateway 도구)
        
        Args:
            task: 작업 설명
            domain: 도메인 (health, market, system, general)
            use_intelligent_routing: 지능형 라우팅 사용 여부
        
        Returns:
            분석 결과
        """
        if not self.client:
            return {"error": "Gateway 클라이언트가 초기화되지 않았습니다."}
        
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/analyze_task",
                json={
                    "task": task,
                    "domain": domain,
                    "use_intelligent_routing": use_intelligent_routing
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Gateway 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"Gateway 통신 실패: {e}"}
    
    async def gather_context(
        self,
        task: str,
        include_code: bool = True,
        include_memory: bool = True,
        include_web: bool = True,
        include_icd: bool = True
    ) -> Dict[str, Any]:
        """
        컨텍스트 통합 (Gateway 도구)
        
        Args:
            task: 작업 설명
            include_code: 코드 컨텍스트 포함
            include_memory: 장기기억 포함
            include_web: 웹 검색 포함
            include_icd: ICD 분석 포함
        
        Returns:
            통합 컨텍스트
        """
        if not self.client:
            return {"error": "Gateway 클라이언트가 초기화되지 않았습니다."}
        
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/gather_context",
                json={
                    "task": task,
                    "include_code": include_code,
                    "include_memory": include_memory,
                    "include_web": include_web,
                    "include_icd": include_icd
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Gateway 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"Gateway 통신 실패: {e}"}
    
    async def validate_code(
        self,
        code: str,
        language: str = "python",
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        코드 검증 (Gateway 도구)
        
        Args:
            code: 검증할 코드
            language: 언어
            auto_fix: 자동 수정 여부
        
        Returns:
            검증 결과
        """
        if not self.client:
            return {"error": "Gateway 클라이언트가 초기화되지 않았습니다."}
        
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/validate_code",
                json={
                    "code": code,
                    "language": language,
                    "auto_fix": auto_fix
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Gateway 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"Gateway 통신 실패: {e}"}
    
    async def get_code_dependencies(
        self,
        file_path: str,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        코드 의존성 추출 (Gateway 도구)
        
        Args:
            file_path: 파일 경로
            max_depth: 최대 깊이
        
        Returns:
            의존성 정보
        """
        if not self.client:
            return {"error": "Gateway 클라이언트가 초기화되지 않았습니다."}
        
        try:
            response = await self.client.post(
                f"{self.gateway_url}/api/get_code_dependencies",
                json={
                    "file_path": file_path,
                    "max_depth": max_depth
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Gateway 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"Gateway 통신 실패: {e}"}
    
    async def close(self):
        """리소스 정리"""
        if self.client:
            await self.client.aclose()

