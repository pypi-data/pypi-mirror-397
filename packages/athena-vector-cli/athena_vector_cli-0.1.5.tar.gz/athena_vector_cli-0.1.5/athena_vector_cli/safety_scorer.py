#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전도 점수 계산 모듈
- 명령어 실행 전 안전도 점수 계산
- 수학적 검증 기반 안전 실행
"""

import os
import sys
import re
from typing import Dict, List, Optional, Any
from .core_integration import CoreIntegration
from .gateway_integration import GatewayIntegration


class SafetyScorer:
    """안전도 점수 계산 클래스"""
    
    # 위험한 명령어 패턴 (블랙리스트)
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+~",
        r"format\s+",
        r"del\s+/f\s+/s\s+/q",
        r"shutdown",
        r"reboot",
        r"mkfs",
        r"dd\s+if=",
        r">\s+/dev/sd",
        r"rm\s+-rf\s+\*",
        r"chmod\s+777",
        r"chown\s+root",
    ]
    
    # 안전한 명령어 패턴 (화이트리스트)
    SAFE_PATTERNS = [
        r"git\s+status",
        r"git\s+log",
        r"ls\s+-la",
        r"pwd",
        r"echo\s+",
        r"cat\s+",
        r"head\s+",
        r"tail\s+",
    ]
    
    def __init__(self, core: Optional[CoreIntegration] = None, gateway: Optional[GatewayIntegration] = None):
        """
        초기화
        
        Args:
            core: Core 엔진 통합 (선택적)
            gateway: Gateway 통합 (선택적)
        """
        self.core = core
        self.gateway = gateway
    
    def _evaluate_risk(self, command: str) -> float:
        """
        명령어 위험도 평가 (0.0 ~ 100.0)
        
        Args:
            command: 명령어 문자열
        
        Returns:
            위험도 점수 (0.0 = 안전, 100.0 = 매우 위험)
        """
        command_lower = command.lower()
        risk_score = 0.0
        
        # 위험한 패턴 확인
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower, re.IGNORECASE):
                risk_score = 100.0  # 매우 위험
                return risk_score
        
        # 안전한 패턴 확인 (화이트리스트 우선)
        is_safe_pattern = False
        for pattern in self.SAFE_PATTERNS:
            if re.search(pattern, command_lower, re.IGNORECASE):
                is_safe_pattern = True
                risk_score = 0.0  # 안전한 패턴이면 위험도 0
                break
        
        # 추가 위험 요소 확인
        # 1. sudo/관리자 권한
        if re.search(r"sudo\s+", command_lower):
            risk_score += 20.0
        
        # 2. 파일 삭제
        if re.search(r"rm\s+", command_lower):
            risk_score += 30.0
        
        # 3. 네트워크 관련
        if re.search(r"curl\s+.*http|wget\s+.*http", command_lower):
            risk_score += 10.0
        
        # 4. 데이터베이스 관련
        if re.search(r"drop\s+table|delete\s+from|truncate", command_lower):
            risk_score += 40.0
        
        # 5. 환경 변수 변경
        if re.search(r"export\s+.*=|set\s+.*=", command_lower):
            risk_score += 5.0
        
        return min(100.0, risk_score)
    
    async def get_success_rate(self, command: str) -> float:
        """
        과거 성공률 조회
        
        Args:
            command: 명령어
        
        Returns:
            성공률 (0.0 ~ 1.0)
        """
        if not self.core:
            return 0.8  # 기본값 (80%)
        
        try:
            # 장기기억에서 유사 명령어 검색
            results = await self.core.search_memory(f"successful execution of {command}", limit=10)
            
            if not results:
                return 0.8  # 기본값
            
            # 성공 관련 키워드 확인
            success_count = 0
            total_count = len(results)
            
            for result in results:
                content = result.get("content", "").lower()
                if any(keyword in content for keyword in ["success", "completed", "done", "executed", "succeeded"]):
                    success_count += 1
            
            return success_count / total_count if total_count > 0 else 0.8
        except Exception as e:
            print(f"⚠️ 성공률 조회 실패: {e}", file=sys.stderr)
            return 0.8
    
    async def validate_code(self, command: str) -> float:
        """
        코드 검증 (Gateway 도구 사용)
        
        Args:
            command: 명령어
        
        Returns:
            검증 점수 (0.0 ~ 100.0)
        """
        if not self.gateway:
            return 80.0  # 기본값 (80%)
        
        try:
            # Gateway로 코드 검증
            result = await self.gateway.validate_code(
                code=command,
                language="bash",  # 셸 명령어
                auto_fix=False
            )
            
            if result.get("error"):
                return 60.0  # 검증 실패 시 낮은 점수
            
            # 검증 결과에서 점수 추출
            validation_score = result.get("score", 80.0)
            return float(validation_score)
        except Exception as e:
            print(f"⚠️ 코드 검증 실패: {e}", file=sys.stderr)
            return 80.0
    
    async def get_dependency_impact(self, command: str) -> float:
        """
        의존성 영향도 분석
        
        Args:
            command: 명령어
        
        Returns:
            영향도 점수 (0.0 = 영향 없음, 100.0 = 매우 큰 영향)
        """
        # 간단한 영향도 분석
        command_lower = command.lower()
        impact_score = 0.0
        
        # 시스템 파일 변경
        if re.search(r"/etc/|/usr/|/bin/|/sbin/", command_lower):
            impact_score += 50.0
        
        # 환경 변수 변경
        if re.search(r"export\s+.*PATH|export\s+.*HOME", command_lower):
            impact_score += 30.0
        
        # 네트워크 설정 변경
        if re.search(r"iptables|firewall|ufw", command_lower):
            impact_score += 40.0
        
        # 서비스 시작/중지
        if re.search(r"systemctl\s+(start|stop|restart)", command_lower):
            impact_score += 20.0
        
        return min(100.0, impact_score)
    
    async def calculate_safety_score(self, command: str) -> Dict[str, Any]:
        """
        안전도 점수 계산
        
        Args:
            command: 명령어 문자열
        
        Returns:
            안전도 점수 및 상세 정보
        """
        # 1. 위험도 평가
        risk_score = self._evaluate_risk(command)
        
        # 위험도가 100점이면 즉시 0점 반환 (치명적 위험)
        if risk_score >= 100.0:
            return {
                "safety_score": 0.0,
                "risk_score": 100.0,
                "success_rate": 0.0,
                "validation_score": 0.0,
                "dependency_impact": 100.0,
                "level": "DANGEROUS",
                "recommendation": "실행 비권장 (치명적 위험)"
            }
        
        # 안전한 패턴 확인 (화이트리스트 우선)
        is_safe_pattern = False
        for pattern in self.SAFE_PATTERNS:
            if re.search(pattern, command.lower(), re.IGNORECASE):
                is_safe_pattern = True
                break
        
        # 안전한 패턴이면 높은 점수 반환
        if is_safe_pattern and risk_score == 0.0:
            return {
                "safety_score": 98.0,
                "risk_score": 0.0,
                "success_rate": 95.0,
                "validation_score": 95.0,
                "dependency_impact": 0.0,
                "level": "VERY_SAFE",
                "recommendation": "자동 실행 가능 (매우 안전)"
            }
        
        # 2. 과거 성공률 조회 (Core 엔진)
        success_rate = await self.get_success_rate(command)
        success_rate_percent = success_rate * 100.0
        
        # 3. 코드 검증 (Gateway 도구)
        validation_score = await self.validate_code(command)
        
        # 4. 의존성 영향도 분석
        dependency_impact = await self.get_dependency_impact(command)
        
        # 5. 최종 안전도 계산 (가중 평균)
        # 위험도가 높을수록 안전도 점수 감소
        safety_score = (
            (100.0 - risk_score) * 0.5 +      # 위험도 (50% - 가중치 증가)
            success_rate_percent * 0.25 +     # 성공률 (25%)
            validation_score * 0.15 +          # 검증 점수 (15%)
            (100.0 - dependency_impact) * 0.1  # 의존성 영향도 (10%)
        )
        
        # 안전도 점수를 0~100 범위로 제한
        safety_score = max(0.0, min(100.0, safety_score))
        
        return {
            "safety_score": round(safety_score, 1),
            "risk_score": round(risk_score, 1),
            "success_rate": round(success_rate_percent, 1),
            "validation_score": round(validation_score, 1),
            "dependency_impact": round(dependency_impact, 1),
            "level": self._get_safety_level(safety_score),
            "recommendation": self._get_recommendation(safety_score)
        }
    
    def _get_safety_level(self, safety_score: float) -> str:
        """
        안전도 레벨 반환
        
        Args:
            safety_score: 안전도 점수
        
        Returns:
            안전도 레벨
        """
        if safety_score >= 95:
            return "VERY_SAFE"
        elif safety_score >= 85:
            return "SAFE"
        elif safety_score >= 75:
            return "MODERATE"
        elif safety_score >= 60:
            return "RISKY"
        else:
            return "DANGEROUS"
    
    def _get_recommendation(self, safety_score: float) -> str:
        """
        실행 권장사항 반환
        
        Args:
            safety_score: 안전도 점수
        
        Returns:
            권장사항
        """
        if safety_score >= 95:
            return "자동 실행 가능 (매우 안전)"
        elif safety_score >= 85:
            return "간단한 확인 후 실행 권장"
        elif safety_score >= 75:
            return "명확한 확인 후 실행 권장"
        elif safety_score >= 60:
            return "신중한 검토 후 실행 권장"
        else:
            return "실행 비권장 (위험)"

