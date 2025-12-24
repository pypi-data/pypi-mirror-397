#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자연어 → 벡터 → 명령어 파이프라인
- 자연어 입력 처리
- 벡터 명령어 재사용 검색
- 벡터 명령어 저장
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

from .server import CommandVectorServer
from .core_integration import CoreIntegration
from .gateway_integration import GatewayIntegration


class NaturalLanguageCommandPipeline:
    """자연어 → 벡터 → 명령어 파이프라인 (Core 엔진 + Gateway 통합)"""
    
    def __init__(self, training_mode: bool = False, use_gateway: bool = False):
        """
        초기화
        
        Args:
            training_mode: 학습 모드 활성화 여부 (기본값: False)
            use_gateway: Gateway 사용 여부 (기본값: False)
        """
        self.command_vector_server = CommandVectorServer()
        self.core = CoreIntegration(use_gateway=use_gateway)  # Core 엔진 통합
        self.gateway = GatewayIntegration() if use_gateway else None  # Gateway 통합 (선택적)
        self.use_vector_reuse = True  # 벡터 재사용 활성화
        self.training_mode = training_mode  # 학습 모드
        self.learning_history = []  # 학습 이력 추적
    
    async def process(
        self,
        natural_language: str,
        use_vector_reuse: bool = True,
        similarity_threshold: float = 0.85,
        mode: str = "standard"  # 🆕 MKM 하이브리드 전략: "standard" or "turbo"
    ) -> Dict[str, Any]:
        """
        자연어 입력 처리
        
        Args:
            natural_language: 자연어 입력
            use_vector_reuse: 벡터 재사용 활성화 여부
            similarity_threshold: 유사도 임계값
        
        Returns:
            처리 결과
        """
        try:
            # 0. Gateway로 작업 분석 (선택적)
            task_analysis = None
            context = None
            if self.gateway:
                try:
                    task_analysis = await self.gateway.analyze_task(natural_language)
                    context = await self.gateway.gather_context(
                        natural_language,
                        include_code=False,  # CLI에서는 코드베이스 검색 불필요
                        include_memory=True,
                        include_web=False,  # CLI에서는 웹 검색 불필요
                        include_icd=False
                    )
                except Exception as e:
                    print(f"⚠️ Gateway 분석 실패 (계속 진행): {e}", file=sys.stderr)
            
            # 학습 모드: 자연어 입력 시 학습 카드 생성
            if self.training_mode:
                # 1. 벡터 추천
                suggestions = await self.suggest_vector_id(natural_language, limit=5)
                
                # 2. 학습 카드 생성
                learning_card = {
                    "input": natural_language,
                    "suggested_vectors": suggestions,
                    "tip": "다음엔 이 벡터를 직접 입력하세요",
                    "timestamp": datetime.now().isoformat()
                }
                
                # 3. 학습 이력 저장
                self.learning_history.append(learning_card)
                
                return {
                    "type": "learning",
                    "learning_card": learning_card,
                    "suggestions": suggestions,
                    "message": "📚 학습 모드: 벡터 매핑을 학습하세요"
                }
            
            # 1. Core 엔진으로 장기기억 검색
            memory_results = await self.core.search_memory(natural_language, limit=3)
            
            # 2. Gateway 컨텍스트에서 메모리 결과 추가 (있는 경우)
            if context and context.get("memory_results"):
                gateway_memory = context.get("memory_results", [])
                if isinstance(gateway_memory, list):
                    memory_results.extend(gateway_memory)
            
            # 3. 벡터 명령어 검색 (재사용 가능한 명령어 찾기)
            vector_results = []
            if use_vector_reuse:
                similar_commands = await self.command_vector_server.search_similar_command(
                    natural_language,
                    limit=3,
                    threshold=similarity_threshold
                )
                vector_results = similar_commands
            
            # 4. 융합 추론 (Core 엔진)
            # Gateway 분석 결과도 포함
            sources = [memory_results, vector_results]
            if task_analysis:
                sources.append([task_analysis])  # 작업 분석 결과도 포함
            fused_result = await self.core.fuse_inference(*sources)
            
            # 4. 유사도가 높으면 재사용
            if fused_result.get("results"):
                best_match = fused_result["results"][0]
                
                # 벡터 태그가 있으면 재사용
                vector_tag = best_match.get('vector_tag')
                if vector_tag:
                    reused = await self.command_vector_server.reuse_command(vector_tag)
                    
                    if reused:
                        # 사용률 추적
                        await self.command_vector_server.track_usage(vector_tag)
                        
                        # 장기기억에 저장 (학습)
                        await self.core.store_memory(
                            content=f"Command executed: {natural_language} -> {vector_tag}",
                            category="command_execution",
                            tags=["cli", "command", vector_tag]
                        )
                        
                        return {
                            "type": "reuse",
                            "vector_tag": vector_tag,
                            "similarity": best_match.get('score', best_match.get('similarity', 0.0)),
                            "dsl": reused.get('dsl'),
                            "result": reused.get('result'),
                            "message": f"✅ 벡터 명령어 재사용 (융합 추론): {vector_tag}",
                            "fused": True,
                            "memory_count": len(memory_results)
                        }
            
            # 3. 재사용 불가능하면 새로 생성
            return {
                "type": "new",
                "natural_language": natural_language,
                "message": "⚠️ 새로운 명령어입니다. 학습 모드로 저장하세요."
            }
            
        except Exception as e:
            return {
                "type": "error",
                "error": str(e),
                "message": f"❌ 처리 실패: {e}"
            }
    
    async def suggest_vector_id(
        self,
        natural_language: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        자연어 입력에 대한 벡터 ID 추천
        
        Args:
            natural_language: 자연어 입력
            limit: 최대 추천 개수
        
        Returns:
            추천 벡터 목록
        """
        try:
            # 유사 명령어 검색
            similar = await self.command_vector_server.search_similar_command(
                natural_language,
                limit=limit,
                threshold=0.5  # 낮은 임계값으로 넓게 검색
            )
            
            suggestions = []
            for cmd in similar:
                suggestions.append({
                    "vector_tag": cmd.get('vector_tag'),
                    "natural_language": cmd.get('natural_language'),
                    "similarity": cmd.get('score', 0.0)
                })
            
            return suggestions
            
        except Exception as e:
            print(f"⚠️ 벡터 추천 실패: {e}", file=sys.stderr)
            return []

