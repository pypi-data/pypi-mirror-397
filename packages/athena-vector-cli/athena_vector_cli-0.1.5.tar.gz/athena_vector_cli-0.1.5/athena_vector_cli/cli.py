#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Athena Vector Command CLI (Core + Gateway 통합 버전)
- 터미널에서 자연어 명령어를 벡터 시스템으로 실행
- Core 엔진 통합: 장기기억, 융합 추론
- Gateway 통합: 98개 도구 활용
- 사용법: athena "서버 상태 보여줘"
"""

import sys
import argparse
import asyncio
import os
from pathlib import Path

from . import __version__
from .pipeline import NaturalLanguageCommandPipeline
from .executor import execute_from_dsl, extract_command_from_dsl, extract_command_from_result
from .safety_scorer import SafetyScorer


async def execute_command(
    query: str, 
    auto_execute: bool = False, 
    confirm: bool = True, 
    use_gateway: bool = False,
    mode: str = "standard",  # 🆕 MKM 하이브리드 전략: "standard" or "turbo"
    show_safety: bool = False  # 🆕 안전도 점수 상세 표시
):
    """
    자연어 명령어 실행 (Core + Gateway 통합)
    
    MKM 하이브리드 아키텍처:
    - 사고 레이어: MKM12 벡터 이론 (내부 분석)
    - 출력 레이어: 표준 코드 (호환성 100%)
    
    Args:
        query: 자연어 명령어
        auto_execute: 자동 실행 여부 (--execute 플래그)
        confirm: 실행 전 확인 여부
        use_gateway: Gateway 사용 여부
        mode: 코드 생성 모드 ("standard" = 표준 코드, 기본값) or "turbo" (벡터 직접 실행, v0.2.0 예정)
        show_safety: 안전도 점수 상세 표시 여부
    """
    print(f"🔍 검색 중: '{query}'")
    
    # Pipeline 초기화 (Core + Gateway 통합)
    pipeline = NaturalLanguageCommandPipeline(training_mode=False, use_gateway=use_gateway)
    
    try:
        # Pipeline 처리 (Core + Gateway 통합)
        pipeline_result = await pipeline.process(
            query,
            use_vector_reuse=True,
            similarity_threshold=0.7,
            mode=mode  # 🆕 MKM 하이브리드 전략 전달
        )
        
        # 모드 정보 표시
        if mode == "turbo":
            print(f"\n🚀 Turbo Mode (벡터 직접 실행): v0.2.0에서 추가될 예정입니다.")
            print(f"💡 현재는 'standard' 모드로 작동합니다.")
        
        # Pipeline 결과 처리
        if pipeline_result.get("type") == "reuse":
            # 융합 추론으로 찾은 명령어 재사용
            vector_tag = pipeline_result.get("vector_tag")
            dsl = pipeline_result.get("dsl")
            result = pipeline_result.get("result")
            similarity = pipeline_result.get("similarity", 0.0)
            fused = pipeline_result.get("fused", False)
            memory_count = pipeline_result.get("memory_count", 0)
            
            print(f"\n✅ 유사 명령어 발견:")
            if fused:
                print(f"   🧠 융합 추론 사용 (장기기억 {memory_count}개 + 벡터 검색)")
            if pipeline.gateway:
                print(f"   🏛️ Gateway: Analyzing Context...")
                print(f"   🧠 Core: Retrieving Memory...")
            print(f"   벡터 태그: {vector_tag}")
            print(f"   유사도: {similarity:.2f}")
            
            # 명령어 추출 및 실행
            command = extract_command_from_dsl(dsl) or extract_command_from_result(result)
            
            if command:
                print(f"\n📋 추출된 명령어:")
                print(f"   {command}")
                
                # 안전도 점수 계산
                safety_scorer = SafetyScorer(core=pipeline.core, gateway=pipeline.gateway)
                safety_result = await safety_scorer.calculate_safety_score(command)
                safety_score = safety_result.get("safety_score", 0.0)
                safety_level = safety_result.get("level", "UNKNOWN")
                recommendation = safety_result.get("recommendation", "")
                
                # 안전도 점수 표시 (Rich 라이브러리 스타일)
                if show_safety or safety_score < 85:
                    # 상세 분석 표시
                    print(f"\n{'='*60}")
                    print(f"🛡️ 안전도 분석")
                    print(f"{'='*60}")
                    print(f"Safety Score: {safety_score}/100 ({safety_level})")
                    print(f"위험도: {safety_result.get('risk_score', 0.0)}/100")
                    print(f"성공률: {safety_result.get('success_rate', 0.0)}%")
                    print(f"검증 점수: {safety_result.get('validation_score', 0.0)}/100")
                    print(f"의존성 영향도: {safety_result.get('dependency_impact', 0.0)}/100")
                    print(f"권장사항: {recommendation}")
                    print(f"{'='*60}")
                else:
                    # 간단한 표시 (85점 이상)
                    level_emoji = "🟢" if safety_score >= 95 else "🟡"
                    print(f"\n{level_emoji} Safety Score: {safety_score}/100 ({safety_level})")
                
                # 안전도에 따른 실행 레벨 결정
                execution_level = None
                if safety_score >= 95:
                    # Level 1: 완전 자동 실행
                    execution_level = "AUTO"
                    if not auto_execute:
                        print(f"\n🟢 Autonomy Level 1: Auto-Execute")
                        print(f"💡 안전도 점수가 95점 이상입니다. 자동 실행 가능합니다.")
                elif safety_score >= 85:
                    # Level 2: 간단한 확인
                    execution_level = "CONFIRM_SIMPLE"
                    print(f"\n🟡 Autonomy Level 2: Simple Confirmation")
                elif safety_score >= 75:
                    # Level 3: 명확한 확인
                    execution_level = "CONFIRM_STRICT"
                    print(f"\n🟠 Autonomy Level 3: Strict Confirmation")
                else:
                    # Level 4: 강제 확인
                    execution_level = "CONFIRM_FORCE"
                    print(f"\n🔴 Autonomy Level 4: Force Confirmation")
                    print(f"⚠️ 안전도 점수가 낮습니다 ({safety_score}/100). 신중히 검토하세요.")
                
                # 실행 옵션 확인 (안전도 점수 기반)
                should_confirm = True
                should_auto_execute = False
                
                if execution_level == "AUTO" and auto_execute:
                    # Level 1: 완전 자동 실행
                    should_confirm = False
                    should_auto_execute = True
                elif execution_level == "CONFIRM_SIMPLE":
                    # Level 2: 간단한 확인
                    should_confirm = True
                    should_auto_execute = auto_execute
                elif execution_level == "CONFIRM_STRICT":
                    # Level 3: 명확한 확인
                    should_confirm = True
                    should_auto_execute = False
                elif execution_level == "CONFIRM_FORCE":
                    # Level 4: 강제 확인
                    should_confirm = True
                    should_auto_execute = False
                
                if should_auto_execute or should_confirm:
                    exec_result = execute_from_dsl(
                        dsl=dsl,
                        result=result,
                        confirm=should_confirm and not should_auto_execute,
                        auto_execute=should_auto_execute
                    )
                    
                    if exec_result.get("success"):
                        print(f"\n✅ 명령어 실행 완료")
                        return True
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
                    print(f"\n💡 이 명령어를 실행하려면 --execute 플래그를 사용하세요")
            else:
                print(f"\n📋 저장된 정보:")
                print(f"   DSL: {dsl}")
                if result:
                    print(f"   결과: {result}")
                print(f"\n💡 DSL에서 실행 가능한 명령어를 추출할 수 없습니다.")
            
            return True
        
        elif pipeline_result.get("type") == "new":
            # 새로운 명령어
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
                    
                    # CommandVectorServer를 통해 저장
                    from .server import CommandVectorServer
                    server = CommandVectorServer()
                    
                    vector_tag = await server.store_command(
                        natural_language=query,
                        dsl=dsl,
                        result=result
                    )
                    
                    if vector_tag:
                        print(f"✅ 명령어 저장 완료: {vector_tag}")
                        # Core 엔진에도 저장
                        await pipeline.core.store_memory(
                            content=f"Command stored: {query} -> {vector_tag}",
                            category="command_storage",
                            tags=["cli", "command", vector_tag]
                        )
                        return True
                except Exception as e:
                    print(f"❌ 저장 실패: {e}")
                    return False
            
            return False
        
        elif pipeline_result.get("type") == "error":
            print(f"❌ 처리 실패: {pipeline_result.get('error')}")
            return False
        
        else:
            print(f"⚠️ 알 수 없는 결과 타입: {pipeline_result.get('type')}")
            return False
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        if os.getenv("ATHENA_DEBUG"):
            import traceback
            traceback.print_exc(file=sys.stderr)
        return False
    
    finally:
        # 리소스 정리
        if pipeline.core:
            await pipeline.core.close()
        if pipeline.gateway:
            await pipeline.gateway.close()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        prog="athena",
        description="🏛️ Athena Vector CLI - Your Personal AI Command Brain (Core + Gateway 통합)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  athena "서버 상태 보여줘"
  athena "Git 저장소 상태 확인"
  athena "Docker 컨테이너 목록"
  athena --gateway "서버 로그 분석해서 에러 원인 찾고 고쳐줘"

환경 변수:
  VPS_QDRANT_URL 또는 QDRANT_URL 설정 필요
  ATHENA_GATEWAY_URL: Gateway URL (기본값: http://localhost:8000)
  ATHENA_USE_GATEWAY: Gateway 사용 여부 (true/false)
  
더 많은 정보: https://github.com/mkmlab-hq/athena-vector-cli
        """,
    )
    
    # 위치 인자 (자연어 명령어)
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
    
    parser.add_argument(
        "--gateway",
        action="store_true",
        help="Gateway 통합 사용 (98개 도구 활용)"
    )
    
    parser.add_argument(
        "--show-safety",
        action="store_true",
        help="안전도 점수 상세 표시"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["standard", "turbo"],
        default="standard",
        help="코드 생성 모드: standard (표준 코드, 기본값) or turbo (벡터 직접 실행, v0.2.0 예정)"
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
        confirm = args.execute and not args.yes
        use_gateway = args.gateway or os.getenv("ATHENA_USE_GATEWAY", "false").lower() == "true"
        
        success = asyncio.run(execute_command(
            args.query,
            auto_execute=auto_execute,
            confirm=confirm,
            use_gateway=use_gateway,
            mode=args.mode,  # 🆕 MKM 하이브리드 전략
            show_safety=args.show_safety
        ))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자 중단", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        error_msg = str(e)
        if "QDRANT_URL" in error_msg or "environment variable" in error_msg:
            print("❌ 설정 오류: 환경 변수가 설정되지 않았습니다.", file=sys.stderr)
            print("💡 환경 변수 VPS_QDRANT_URL 또는 QDRANT_URL을 설정해주세요.", file=sys.stderr)
            print("   예시: export VPS_QDRANT_URL=http://your-qdrant-server:6333", file=sys.stderr)
        else:
            print(f"❌ 설정 오류: {error_msg}", file=sys.stderr)
        sys.exit(1)
    except (ConnectionError, OSError) as e:
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
        if os.getenv("ATHENA_DEBUG"):
            import traceback
            traceback.print_exc(file=sys.stderr)
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        print("💡 자세한 정보는 ATHENA_DEBUG=1 환경 변수를 설정하고 다시 실행해주세요.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

