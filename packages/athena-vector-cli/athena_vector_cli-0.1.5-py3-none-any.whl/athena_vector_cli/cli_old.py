#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Athena Vector Command CLI
- 터미널에서 자연어 명령어를 벡터 시스템으로 실행
- 사용법: athena "서버 상태 보여줘"
"""

import sys
import argparse
import asyncio
import os
from pathlib import Path

from . import __version__
from .server import CommandVectorServer
from .pipeline import NaturalLanguageCommandPipeline
from .executor import execute_from_dsl, extract_command_from_dsl, extract_command_from_result
from .core_integration import CoreIntegration

async def execute_command(query: str, auto_execute: bool = False, confirm: bool = True):
    """
    자연어 명령어 실행
    
    Args:
        query: 자연어 명령어
        auto_execute: 자동 실행 여부 (--execute 플래그)
        confirm: 실행 전 확인 여부
    """
    print(f"🔍 검색 중: '{query}'")
    
    # Pipeline 초기화 (Core 엔진 통합)
    use_gateway = os.getenv("ATHENA_USE_GATEWAY", "false").lower() == "true"
    pipeline = NaturalLanguageCommandPipeline(training_mode=False, use_gateway=use_gateway)
    server = CommandVectorServer()
    
    if not server.qdrant_client:
        print("❌ Qdrant 연결 실패", file=sys.stderr)
        print("💡 환경 변수 VPS_QDRANT_URL 또는 QDRANT_URL을 설정해주세요.", file=sys.stderr)
        return False
    
    # 1. 유사 명령어 검색
    try:
        similar = await server.search_similar_command(
            query,
            limit=3,
            threshold=0.7
        )
    except (ConnectionError, OSError) as e:
        error_msg = str(e)
        if "getaddrinfo" in error_msg or "connection" in error_msg.lower():
            print("❌ 네트워크 연결 실패: Qdrant 서버에 연결할 수 없습니다.", file=sys.stderr)
            print("💡 다음을 확인해주세요:", file=sys.stderr)
            print("   1. 네트워크 연결 상태", file=sys.stderr)
            print("   2. Qdrant 서버 URL이 올바른지 확인", file=sys.stderr)
            print("   3. Qdrant 서버가 실행 중인지 확인", file=sys.stderr)
        else:
            print(f"❌ 네트워크 오류: {error_msg}", file=sys.stderr)
        return False
    except Exception as e:
        # 기타 오류는 상위에서 처리
        raise
    
    if not similar:
        print("⚠️ 유사한 명령어를 찾을 수 없습니다.")
        print("💡 새로운 명령어로 학습 모드로 저장하시겠습니까? (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            print("📝 DSL을 입력해주세요 (JSON 형식):")
            dsl_str = input().strip()
            try:
                import json
                dsl = json.loads(dsl_str)
                
                print("📝 결과를 입력해주세요:")
                result = input().strip()
                
                vector_tag = await server.store_command(
                    natural_language=query,
                    dsl=dsl,
                    result=result
                )
                
                if vector_tag:
                    print(f"✅ 명령어 저장 완료: {vector_tag}")
                    return True
            except Exception as e:
                print(f"❌ 저장 실패: {e}")
                return False
        
        return False
    
    # 2. 가장 유사한 명령어 선택
    best_match = similar[0]
    print(f"\n✅ 유사 명령어 발견:")
    print(f"   벡터 태그: {best_match['vector_tag']}")
    print(f"   설명: {best_match['natural_language']}")
    print(f"   유사도: {best_match['score']:.2f}")
    
    # 3. 명령어 재사용
    reused = await server.reuse_command(best_match['vector_tag'])
    
    if reused:
        dsl = reused.get('dsl', {})
        result = reused.get('result')
        
        print(f"\n✅ 유사 명령어 발견:")
        print(f"   벡터 태그: {best_match['vector_tag']}")
        print(f"   설명: {best_match['natural_language']}")
        print(f"   유사도: {best_match['score']:.2f}")
        
        # 4. 명령어 추출 및 실행
        command = extract_command_from_dsl(dsl) or extract_command_from_result(result)
        
        if command:
            print(f"\n📋 추출된 명령어:")
            print(f"   {command}")
            
            # 실행 옵션 확인
            if auto_execute or confirm:
                # 실제 명령어 실행
                exec_result = execute_from_dsl(
                    dsl=dsl,
                    result=result,
                    confirm=confirm and not auto_execute,
                    auto_execute=auto_execute
                )
                
                if exec_result.get("success"):
                    print(f"\n✅ 명령어 실행 완료")
                elif exec_result.get("cancelled"):
                    print(f"\n⚠️ 실행 취소됨")
                    return False
                elif exec_result.get("blocked"):
                    print(f"\n❌ {exec_result.get('error')}")
                    return False
                else:
                    print(f"\n❌ 실행 실패: {exec_result.get('error')}")
                    return False
            else:
                # 실행하지 않고 명령어만 표시
                print(f"\n💡 이 명령어를 실행하려면 --execute 플래그를 사용하세요")
        else:
            # 명령어를 추출할 수 없음
            print(f"\n📋 저장된 정보:")
            print(f"   DSL: {dsl}")
            if result:
                print(f"   결과: {result}")
            print(f"\n💡 DSL에서 실행 가능한 명령어를 추출할 수 없습니다.")
        
        # 5. 사용률 추적
        await server.track_usage(best_match['vector_tag'])
        
        return True
    else:
        print("❌ 명령어 재사용 실패")
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        prog="athena",
        description="🏛️ Athena Vector CLI - Your Personal AI Command Brain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  athena "서버 상태 보여줘"
  athena "Git 저장소 상태 확인"
  athena "Docker 컨테이너 목록"

환경 변수:
  VPS_QDRANT_URL 또는 QDRANT_URL 설정 필요
  
더 많은 정보: https://github.com/mkmlab-hq/athena-vector-cli
        """,
    )
    
    # 위치 인자 (자연어 명령어) - 선택적 (대화형 모드 고려)
    parser.add_argument(
        "query",
        nargs="?",
        help="자연어 명령어 (예: \"서버 상태 보여줘\")"
    )
    
    # 옵션
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Athena CLI v{__version__}",
        help="버전 정보 출력"
    )
    
    parser.add_argument(
        "-e", "--execute",
        action="store_true",
        help="검색된 명령어를 자동으로 실행 (실행 전 확인 프롬프트 표시)"
    )
    
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="실행 전 확인 없이 자동 실행 (--execute와 함께 사용)"
    )
    
    # 인자 파싱
    args = parser.parse_args()
    
    # 쿼리가 없으면 도움말 출력
    if not args.query:
        parser.print_help()
        sys.exit(0)
    
    # 자연어 명령어 실행
    try:
        auto_execute = args.execute or args.yes
        confirm = args.execute and not args.yes  # --execute만 있으면 확인, --yes가 있으면 확인 없음
        
        success = asyncio.run(execute_command(
            args.query,
            auto_execute=auto_execute,
            confirm=confirm
        ))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자 중단", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        # 환경 변수 오류 등 설정 오류
        error_msg = str(e)
        if "QDRANT_URL" in error_msg or "environment variable" in error_msg:
            print("❌ 설정 오류: 환경 변수가 설정되지 않았습니다.", file=sys.stderr)
            print("💡 환경 변수 VPS_QDRANT_URL 또는 QDRANT_URL을 설정해주세요.", file=sys.stderr)
            print("   예시: export VPS_QDRANT_URL=http://your-qdrant-server:6333", file=sys.stderr)
        else:
            print(f"❌ 설정 오류: {error_msg}", file=sys.stderr)
        sys.exit(1)
    except (ConnectionError, OSError) as e:
        # 네트워크 오류
        error_msg = str(e)
        if "getaddrinfo" in error_msg or "connection" in error_msg.lower() or "refused" in error_msg.lower():
            print("❌ 네트워크 연결 실패: Qdrant 서버에 연결할 수 없습니다.", file=sys.stderr)
            print("💡 다음을 확인해주세요:", file=sys.stderr)
            print("   1. 네트워크 연결 상태", file=sys.stderr)
            print("   2. Qdrant 서버 URL이 올바른지 확인", file=sys.stderr)
            print("   3. Qdrant 서버가 실행 중인지 확인", file=sys.stderr)
        else:
            print(f"❌ 네트워크 오류: {error_msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # 기타 오류 (디버그 모드에서만 스택 트레이스)
        if os.getenv("ATHENA_DEBUG"):
            import traceback
            traceback.print_exc(file=sys.stderr)
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        print("💡 자세한 정보는 ATHENA_DEBUG=1 환경 변수를 설정하고 다시 실행해주세요.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

