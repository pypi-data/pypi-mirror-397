#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
명령어 실행 모듈
- DSL에서 실제 명령어 추출
- 안전 검증
- subprocess로 실행
"""

import subprocess
import sys
import os
from typing import Dict, Any, Optional, List


# 위험한 명령어 패턴 (블랙리스트)
DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "format",
    "del /f /s /q",
    "shutdown",
    "reboot",
    "mkfs",
    "dd if=",
    "> /dev/sd",
]


def is_dangerous_command(command: str) -> bool:
    """
    위험한 명령어인지 확인
    
    Args:
        command: 명령어 문자열
        
    Returns:
        위험 여부
    """
    command_lower = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in command_lower:
            return True
    return False


def extract_command_from_dsl(dsl: Dict[str, Any]) -> Optional[str]:
    """
    DSL에서 실제 명령어 추출
    
    Args:
        dsl: DSL 객체
        
    Returns:
        명령어 문자열 또는 None
    """
    if not dsl:
        return None
    
    # DSL 구조에 따라 명령어 추출
    # 일반적인 DSL 구조: {"command": "...", "args": [...]}
    if isinstance(dsl, dict):
        # 1. command 필드 확인
        if "command" in dsl:
            cmd = dsl["command"]
            args = dsl.get("args", [])
            if args:
                return f"{cmd} {' '.join(str(a) for a in args)}"
            return str(cmd)
        
        # 2. shell 필드 확인
        if "shell" in dsl:
            return str(dsl["shell"])
        
        # 3. exec 필드 확인
        if "exec" in dsl:
            return str(dsl["exec"])
        
        # 4. 첫 번째 값이 문자열이면 명령어로 간주
        if len(dsl) == 1:
            first_value = list(dsl.values())[0]
            if isinstance(first_value, str):
                return first_value
    
    # DSL이 문자열이면 그대로 반환
    if isinstance(dsl, str):
        return dsl
    
    return None


def extract_command_from_result(result: Any) -> Optional[str]:
    """
    결과에서 명령어 추출 (fallback)
    
    Args:
        result: 결과 객체
        
    Returns:
        명령어 문자열 또는 None
    """
    if isinstance(result, str):
        # 결과가 명령어처럼 보이면 반환
        if result.strip().startswith(("git ", "docker ", "kubectl ", "npm ", "pip ")):
            return result.strip()
    return None


def execute_shell_command(
    command: str,
    confirm: bool = True,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    셸 명령어 실행
    
    Args:
        command: 실행할 명령어
        confirm: 실행 전 확인 여부
        timeout: 타임아웃 (초)
        
    Returns:
        실행 결과
    """
    # 1. 위험한 명령어 확인
    if is_dangerous_command(command):
        return {
            "success": False,
            "error": "위험한 명령어입니다. 실행이 차단되었습니다.",
            "command": command,
            "blocked": True
        }
    
    # 2. 실행 전 확인
    if confirm:
        print(f"\n⚠️ 다음 명령어를 실행하시겠습니까?")
        print(f"   {command}")
        print(f"\n실행하려면 'y' 또는 'yes'를 입력하세요: ", end="", flush=True)
        
        try:
            response = input().strip().lower()
            if response not in ['y', 'yes']:
                return {
                    "success": False,
                    "error": "사용자가 실행을 취소했습니다.",
                    "command": command,
                    "cancelled": True
                }
        except (EOFError, KeyboardInterrupt):
            return {
                "success": False,
                "error": "사용자가 실행을 취소했습니다.",
                "command": command,
                "cancelled": True
            }
    
    # 3. 명령어 실행
    try:
        print(f"\n🚀 명령어 실행 중...", flush=True)
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        # 4. 결과 출력
        if result.stdout:
            print(result.stdout, end="")
        
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        
        # 5. 반환
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"명령어 실행 시간 초과 ({timeout}초)",
            "command": command,
            "timeout": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }


def execute_from_dsl(
    dsl: Dict[str, Any],
    result: Any = None,
    confirm: bool = True,
    auto_execute: bool = False
) -> Dict[str, Any]:
    """
    DSL에서 명령어를 추출하여 실행
    
    Args:
        dsl: DSL 객체
        result: 결과 객체 (fallback)
        confirm: 실행 전 확인 여부
        auto_execute: 자동 실행 여부 (confirm 무시)
        
    Returns:
        실행 결과
    """
    # 1. DSL에서 명령어 추출
    command = extract_command_from_dsl(dsl)
    
    # 2. DSL에서 추출 실패 시 result에서 시도
    if not command and result:
        command = extract_command_from_result(result)
    
    # 3. 명령어를 찾을 수 없음
    if not command:
        return {
            "success": False,
            "error": "DSL에서 실행 가능한 명령어를 추출할 수 없습니다.",
            "dsl": dsl,
            "result": result
        }
    
    # 4. 실행 (auto_execute가 True면 confirm=False)
    return execute_shell_command(
        command,
        confirm=confirm and not auto_execute,
        timeout=30
    )


