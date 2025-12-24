#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
벡터 명령어 재사용 시스템
- 자연어 명령어를 벡터화하여 저장
- 유사 명령어 검색 및 재사용
- 하이브리드 벡터화 (4차원 벡터 + DCV) 적용
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# 보안: 환경 변수만 사용 (하드코딩된 IP 주소 제거)
# 모듈 레벨에서 ValueError를 발생시키지 않고, 초기화 시점에 검증
def get_qdrant_url() -> Optional[str]:
    """Qdrant URL 가져오기 (설정 파일 우선, 환경 변수 fallback)"""
    try:
        from .config import get_qdrant_url as get_config_qdrant_url
        config_url = get_config_qdrant_url()
        if config_url:
            return config_url
    except Exception:
        pass
    
    # 환경 변수 fallback
    return os.getenv("VPS_QDRANT_URL") or os.getenv("QDRANT_URL")

VPS_QDRANT_URL = None  # 지연 평가를 위해 None으로 설정
COLLECTION_NAME = "command_vectors"
VECTOR_DIMENSION = 768  # all-mpnet-base-v2 차원

# 임베딩 모델 (선택적)
try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer('all-mpnet-base-v2')
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    MODEL = None
    print("⚠️ 임베딩 모델 없음, 해시 기반 벡터 사용", file=sys.stderr)

# 하이브리드 벡터화 (선택적)
HYBRID_VECTORIZATION_AVAILABLE = False  # 패키지에서는 선택적 기능


class CommandVectorServer:
    """벡터 명령어 저장 및 재사용 시스템"""
    
    def __init__(self, qdrant_url: Optional[str] = None, collection_name: Optional[str] = None):
        """
        초기화
        
        Args:
            qdrant_url: Qdrant 서버 URL (기본값: 설정 파일 또는 환경 변수에서 가져옴)
            collection_name: 컬렉션 이름 (기본값: 설정 파일 또는 기본값)
        """
        self.qdrant_client = None
        
        # 컬렉션 이름 결정 (설정 파일 우선)
        if not collection_name:
            try:
                from .config import get_collection_name
                collection_name = get_collection_name()
            except Exception:
                collection_name = COLLECTION_NAME
        self.collection_name = collection_name
        
        # Qdrant URL 결정 (지연 평가, 설정 파일 우선)
        if not qdrant_url:
            qdrant_url = get_qdrant_url()
        if not qdrant_url:
            raise ValueError(
                "Qdrant URL이 설정되지 않았습니다. 다음 중 하나를 설정해주세요:\n"
                "  1. 설정 파일: ~/.athena/config.yaml 또는 .athenarc\n"
                "  2. 환경 변수: VPS_QDRANT_URL 또는 QDRANT_URL\n"
                "예시: export VPS_QDRANT_URL=http://your-qdrant-server:6333"
            )
        
        # Qdrant 클라이언트 초기화
        try:
            self.qdrant_client = QdrantClient(
                url=qdrant_url,
                timeout=3.0
            )
            self._ensure_collection()
            print("✅ CommandVectorServer 초기화 완료", file=sys.stderr)
        except Exception as e:
            error_msg = str(e)
            # 네트워크 오류 감지
            if "getaddrinfo" in error_msg or "connection" in error_msg.lower() or "refused" in error_msg.lower():
                # 네트워크 오류는 상위에서 처리하므로 여기서는 간단히 처리
                print(f"⚠️ Qdrant 연결 실패: 네트워크 오류", file=sys.stderr)
            else:
                print(f"⚠️ Qdrant 연결 실패: {error_msg}", file=sys.stderr)
            self.qdrant_client = None
    
    def _ensure_collection(self):
        """컬렉션 생성 (없으면)"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ 컬렉션 생성: {self.collection_name}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 컬렉션 생성 실패: {e}", file=sys.stderr)
    
    def _generate_vector_tag(self, natural_language: str, dsl: Optional[Dict[str, Any]] = None) -> str:
        """벡터 태그 생성"""
        # 자연어에서 키워드 추출
        keywords = self._extract_keywords(natural_language)
        
        # DSL에서 액션 타입 추출
        action_type = "general"
        if dsl:
            action_type = dsl.get("action", "general")
        
        # 해시 기반 고유 ID 생성
        hash_obj = hashlib.md5(f"{natural_language}{action_type}".encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:6]
        
        # 벡터 태그 형식: {action_type}_{keyword}_{hash}
        tag = f"{action_type}_{keywords[0] if keywords else 'cmd'}_{hash_hex}"
        return tag.lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출 (간단한 버전)"""
        import re
        # 한글 단어 추출
        korean_words = re.findall(r'[가-힣]+', text)
        # 영어 단어 추출 (2글자 이상)
        english_words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        
        keywords = korean_words[:2] + english_words[:2]
        return keywords[:3]  # 최대 3개
    
    def _create_embedding(self, text: str) -> List[float]:
        """임베딩 생성"""
        if not EMBEDDING_AVAILABLE or MODEL is None:
            # Fallback: 간단한 해시 기반 벡터
            hash_obj = hashlib.sha256(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            # 768차원으로 변환
            vector = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(768*2, len(hash_hex)), 2)]
            if len(vector) < VECTOR_DIMENSION:
                vector.extend([0.0] * (VECTOR_DIMENSION - len(vector)))
            return vector[:VECTOR_DIMENSION]
        
        try:
            embedding = MODEL.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️ 임베딩 생성 실패: {e}", file=sys.stderr)
            # Fallback
            hash_obj = hashlib.sha256(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            vector = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(768*2, len(hash_hex)), 2)]
            if len(vector) < VECTOR_DIMENSION:
                vector.extend([0.0] * (VECTOR_DIMENSION - len(vector)))
            return vector[:VECTOR_DIMENSION]
    
    async def store_command(
        self,
        natural_language: str,
        dsl: Dict[str, Any],
        result: Any = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        명령어 벡터 저장
        
        Args:
            natural_language: 자연어 명령어
            dsl: DSL (IR) 객체
            result: 실행 결과
            tags: 추가 태그
        
        Returns:
            벡터 태그 또는 None
        """
        if not self.qdrant_client:
            print("⚠️ Qdrant 클라이언트 없음, 저장 불가", file=sys.stderr)
            return None
        
        try:
            # 1. 벡터 태그 생성
            vector_tag = self._generate_vector_tag(natural_language, dsl)
            
            # 2. 임베딩 생성
            semantic_vector = self._create_embedding(natural_language)
            
            # 3. 하이브리드 벡터화 (기본값)
            vector_4d = {'S': 0.5, 'L': 0.5, 'K': 0.5, 'M': 0.5}
            dcv_data = {'PD': 'L', 'SD': 'S', 'dcv': 0.5}
            pattern_type = 'Type C'
            
            # 4. Qdrant에 저장
            point = PointStruct(
                id=hash(vector_tag) % (2**63),  # Qdrant ID는 정수
                vector=semantic_vector,
                payload={
                    "vector_tag": vector_tag,
                    "natural_language": natural_language,
                    "dsl": dsl,
                    "result": str(result) if result else None,
                    "tags": tags or [],
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat(),
                    "vector_4d_S": vector_4d['S'],
                    "vector_4d_L": vector_4d['L'],
                    "vector_4d_K": vector_4d['K'],
                    "vector_4d_M": vector_4d['M'],
                    "dcv": dcv_data.get('dcv', 0.5),
                    "pattern_type": pattern_type
                }
            )
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ 명령어 벡터 저장 완료: {vector_tag}", file=sys.stderr)
            return vector_tag
            
        except Exception as e:
            error_msg = str(e)
            # 디버그 모드에서만 스택 트레이스 출력
            if os.getenv("ATHENA_DEBUG"):
                import traceback
                traceback.print_exc(file=sys.stderr)
            print(f"❌ 명령어 벡터 저장 실패: {error_msg}", file=sys.stderr)
            return None
    
    async def search_similar_command(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        유사 명령어 검색
        
        Args:
            query: 검색 쿼리 (자연어)
            limit: 최대 결과 수
            threshold: 유사도 임계값
        
        Returns:
            유사 명령어 목록
        """
        if not self.qdrant_client:
            return []
        
        try:
            # 1. 쿼리 벡터화
            query_vector = self._create_embedding(query)
            
            # 2. Qdrant 검색 (query_points API 사용 - 최신 버전)
            try:
                # 최신 API: query_points
                if hasattr(self.qdrant_client, 'query_points'):
                    query_result = self.qdrant_client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        limit=limit,
                        with_payload=True
                    )
                    
                    # 결과 추출
                    if hasattr(query_result, 'points'):
                        results = list(query_result.points) if query_result.points else []
                    else:
                        results = list(query_result) if query_result else []
                    
                    # score_threshold 필터링 (query_points는 직접 지원하지 않으므로 수동 필터링)
                    if threshold is not None and results:
                        results = [r for r in results if hasattr(r, 'score') and r.score >= threshold]
                
                # 구버전 호환: search API
                elif hasattr(self.qdrant_client, 'search'):
                    results = self.qdrant_client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=limit,
                        score_threshold=threshold
                    )
                else:
                    print(f"⚠️ Qdrant 클라이언트에 검색 메서드가 없습니다.", file=sys.stderr)
                    return []
                
            except AttributeError as ae:
                # query_points가 없으면 search로 폴백
                if hasattr(self.qdrant_client, 'search'):
                    results = self.qdrant_client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=limit,
                        score_threshold=threshold
                    )
                else:
                    print(f"⚠️ Qdrant 검색 API 사용 불가: {ae}", file=sys.stderr)
                    return []
            
            # 3. 결과 변환
            similar_commands = []
            for result in results:
                # query_points와 search의 결과 구조가 다를 수 있음
                if hasattr(result, 'payload'):
                    payload = result.payload
                    score = getattr(result, 'score', 0.0)
                elif isinstance(result, dict):
                    payload = result.get('payload', {})
                    score = result.get('score', 0.0)
                else:
                    continue
                
                similar_commands.append({
                    "vector_tag": payload.get("vector_tag") if isinstance(payload, dict) else getattr(payload, 'vector_tag', None),
                    "natural_language": payload.get("natural_language") if isinstance(payload, dict) else getattr(payload, 'natural_language', None),
                    "dsl": payload.get("dsl") if isinstance(payload, dict) else getattr(payload, 'dsl', None),
                    "score": score,
                    "tags": payload.get("tags", []) if isinstance(payload, dict) else getattr(payload, 'tags', [])
                })
            
            return similar_commands
            
        except Exception as e:
            error_msg = str(e)
            # 네트워크 오류는 상위에서 처리하므로 여기서는 간단히 처리
            if "getaddrinfo" in error_msg or "connection" in error_msg.lower():
                # 네트워크 오류는 상위에서 처리됨
                pass
            else:
                # 기타 오류는 디버그 모드에서만 상세 출력
                if os.getenv("ATHENA_DEBUG"):
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                print(f"⚠️ 유사 명령어 검색 실패: {error_msg}", file=sys.stderr)
            return []
    
    async def reuse_command(self, vector_tag: str) -> Optional[Dict[str, Any]]:
        """
        벡터 태그로 명령어 재사용
        
        Args:
            vector_tag: 벡터 태그
        
        Returns:
            DSL 객체 또는 None
        """
        if not self.qdrant_client:
            return None
        
        try:
            # Qdrant에서 조회
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter={
                    "must": [{
                        "key": "vector_tag",
                        "match": {"value": vector_tag}
                    }]
                },
                limit=1
            )
            
            if results[0]:  # results는 (points, next_page_offset) 튜플
                point = results[0][0]
                return {
                    "vector_tag": point.payload.get("vector_tag"),
                    "natural_language": point.payload.get("natural_language"),
                    "dsl": point.payload.get("dsl"),
                    "result": point.payload.get("result")
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ 명령어 재사용 실패: {e}", file=sys.stderr)
            return None
    
    async def track_usage(self, vector_tag: str, user_id: str = "default"):
        """
        명령어 사용률 추적
        
        Args:
            vector_tag: 벡터 태그
            user_id: 사용자 ID
        """
        if not self.qdrant_client:
            return
        
        try:
            # Qdrant에서 조회
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter={
                    "must": [{
                        "key": "vector_tag",
                        "match": {"value": vector_tag}
                    }]
                },
                limit=1
            )
            
            if results[0]:
                point = results[0][0]
                payload = point.payload
                
                # 사용률 증가
                usage_count = payload.get("usage_count", 0) + 1
                
                # 업데이트
                updated_payload = payload.copy()
                updated_payload["usage_count"] = usage_count
                updated_payload["updated"] = datetime.now().isoformat()
                
                # Upsert
                updated_point = PointStruct(
                    id=point.id,
                    vector=point.vector,
                    payload=updated_payload
                )
                
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=[updated_point]
                )
                
        except Exception as e:
            print(f"⚠️ 사용률 추적 실패: {e}", file=sys.stderr)
    
    async def get_usage_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """
        사용률 통계 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            통계 정보
        """
        if not self.qdrant_client:
            return {}
        
        try:
            # 모든 포인트 조회
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000
            )
            
            stats = {
                "total_commands": 0,
                "most_used": [],
                "recent_commands": []
            }
            
            if results[0]:
                points = results[0]
                stats["total_commands"] = len(points)
                
                # 사용률 기준 정렬
                usage_list = []
                for point in points:
                    usage_count = point.payload.get("usage_count", 0)
                    if usage_count > 0:
                        usage_list.append({
                            "vector_tag": point.payload.get("vector_tag"),
                            "natural_language": point.payload.get("natural_language"),
                            "usage_count": usage_count
                        })
                
                usage_list.sort(key=lambda x: x["usage_count"], reverse=True)
                stats["most_used"] = usage_list[:10]
            
            return stats
            
        except Exception as e:
            print(f"⚠️ 통계 조회 실패: {e}", file=sys.stderr)
            return {}

