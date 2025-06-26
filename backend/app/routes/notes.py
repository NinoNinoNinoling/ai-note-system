# backend/app/routes/notes.py
"""
Notes 라우트 - 디버깅 강화 버전

모든 요청/응답을 상세하게 로깅
"""

from flask import Blueprint, request, jsonify
from app.controllers.note_controller import NoteController
import logging
import json
from datetime import datetime

# 로거 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
notes_bp = Blueprint('notes', __name__)

# 컨트롤러 인스턴스 생성
controller = NoteController()


def log_request_details(endpoint_name):
    """요청 상세 정보 로깅"""
    print(f"\n{'='*50}")
    print(f"🚀 API 요청: {endpoint_name}")
    print(f"{'='*50}")
    print(f"📍 URL: {request.url}")
    print(f"📍 Method: {request.method}")
    print(f"📍 Path: {request.path}")
    print(f"📍 Remote Address: {request.remote_addr}")
    print(f"📍 User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    # 쿼리 파라미터
    if request.args:
        print(f"📋 Query Params: {dict(request.args)}")
    
    # 헤더 정보
    print(f"📋 Content-Type: {request.headers.get('Content-Type', 'None')}")
    print(f"📋 Accept: {request.headers.get('Accept', 'None')}")
    
    # JSON 데이터 (있으면)
    if request.is_json and request.get_json():
        print(f"📋 JSON Data: {request.get_json()}")
    
    print(f"{'='*50}\n")


def log_response_details(response_data, status_code=200):
    """응답 상세 정보 로깅"""
    print(f"\n{'='*50}")
    print(f"📤 API 응답")
    print(f"{'='*50}")
    print(f"📊 Status Code: {status_code}")
    print(f"📊 Response Type: {type(response_data)}")
    
    if isinstance(response_data, dict):
        print(f"📊 Response Keys: {list(response_data.keys())}")
        
        # 노트 데이터가 있으면 개수 확인
        if 'notes' in response_data:
            notes = response_data['notes']
            print(f"📊 Notes Count: {len(notes) if notes else 0}")
            
            if notes and len(notes) > 0:
                print(f"📊 First Note: {notes[0].get('title', 'No Title')} (ID: {notes[0].get('id', 'No ID')})")
            else:
                print(f"⚠️ Notes Array is Empty!")
        
        # 전체 응답 크기
        response_str = str(response_data)
        print(f"📊 Response Size: {len(response_str)} characters")
        
        # 처음 200자만 미리보기
        preview = response_str[:200] + "..." if len(response_str) > 200 else response_str
        print(f"📊 Response Preview: {preview}")
    
    print(f"{'='*50}\n")


# ====== 노트 CRUD ======

@notes_bp.route('/notes', methods=['GET'])
def get_notes():
    """노트 목록 조회 - 디버깅 강화"""
    
    log_request_details("GET /api/notes")
    
    try:
        print("🔍 Step 1: 쿼리 파라미터 추출 중...")
        
        # 쿼리 파라미터 추출
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        print(f"🔍 Step 1 완료: limit={limit}, offset={offset}")
        
        print("🔍 Step 2: NoteService.get_all_notes() 호출 중...")
        
        # 노트 조회
        notes = controller.service.get_all_notes(limit=limit, offset=offset)
        
        print(f"🔍 Step 2 완료: {len(notes) if notes else 0}개 노트 조회됨")
        print(f"🔍 Notes Type: {type(notes)}")
        
        if notes:
            print(f"🔍 First Note Type: {type(notes[0])}")
            print(f"🔍 First Note: {notes[0]}")
        
        print("🔍 Step 3: 노트 딕셔너리 변환 중...")
        
        # 응답 데이터 구성
        notes_dicts = []
        for i, note in enumerate(notes):
            try:
                note_dict = controller._note_to_dict(note)
                notes_dicts.append(note_dict)
                if i == 0:  # 첫 번째 노트만 로그
                    print(f"🔍 First Note Dict: {note_dict}")
            except Exception as convert_error:
                print(f"❌ 노트 {i} 변환 실패: {convert_error}")
                continue
        
        response_data = {
            "notes": notes_dicts,
            "total": len(notes_dicts),
            "limit": limit,
            "offset": offset
        }
        
        print(f"🔍 Step 3 완료: {len(notes_dicts)}개 노트 딕셔너리 변환됨")
        
        print("🔍 Step 4: 성공 응답 생성 중...")
        
        success_response = controller.success_response(
            data=response_data,
            message=f"{len(notes)}개의 노트를 조회했습니다"
        )
        
        print(f"🔍 Step 4 완료: 응답 생성됨")
        
        # 응답 로깅
        log_response_details(success_response[0].get_json() if hasattr(success_response[0], 'get_json') else success_response)
        
        return success_response
        
    except Exception as e:
        print(f"❌ 에러 발생: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"❌ 전체 트레이스백:")
        traceback.print_exc()
        
        error_response = controller.error_response(
            message="노트 목록 조회 실패",
            details=str(e),
            status=500
        )
        
        log_response_details(error_response[0].get_json() if hasattr(error_response[0], 'get_json') else error_response, 500)
        
        return error_response


@notes_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """특정 노트 조회"""
    log_request_details(f"GET /api/notes/{note_id}")
    
    try:
        note = controller.service.get_note_by_id(note_id)
        
        response = controller.success_response(
            data={"note": controller._note_to_dict(note)},
            message="노트를 조회했습니다"
        )
        
        log_response_details(response[0].get_json() if hasattr(response[0], 'get_json') else response)
        return response
        
    except ValueError as e:
        return controller.not_found_error("노트")
    except Exception as e:
        print(f"❌ 노트 조회 에러: {e}")
        return controller.error_response(
            message="노트 조회 실패",
            details=str(e),
            status=500
        )


# 간단한 테스트 엔드포인트
@notes_bp.route('/notes/test', methods=['GET'])
def test_notes():
    """테스트용 엔드포인트"""
    log_request_details("GET /api/notes/test")
    
    response_data = {
        "message": "Notes API Test Successful",
        "timestamp": str(datetime.now()),
        "test_notes": [
            {"id": 1, "title": "Test Note 1", "content": "Test Content 1"},
            {"id": 2, "title": "Test Note 2", "content": "Test Content 2"}
        ]
    }
    
    log_response_details(response_data)
    
    return jsonify(response_data), 200


# 나머지 엔드포인트들도 기본 로깅 추가
@notes_bp.route('/notes', methods=['POST'])
def create_note():
    """새 노트 생성"""
    log_request_details("POST /api/notes")
    return controller.create_note()


@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """노트 업데이트"""
    log_request_details(f"PUT /api/notes/{note_id}")
    return controller.update_note(note_id)


@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """노트 삭제"""
    log_request_details(f"DELETE /api/notes/{note_id}")
    
    try:
        success = controller.service.delete_note(note_id)
        
        if success:
            return controller.success_response(
                data={"deleted_id": note_id},
                message="노트가 성공적으로 삭제되었습니다"
            )
        else:
            return controller.error_response(
                message="노트 삭제 실패",
                status=500
            )
            
    except ValueError as e:
        return controller.not_found_error("노트")
    except Exception as e:
        return controller.error_response(
            message="노트 삭제 실패",
            details=str(e),
            status=500
        )