# backend/utils/date_utils.py - 날짜 처리 유틸
"""
날짜/시간 관련 유틸리티 함수들
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
import re


def format_datetime(dt: datetime, format_type: str = 'iso') -> str:
    """날짜시간 포맷팅"""
    if not dt:
        return ""
    
    if format_type == 'iso':
        return dt.isoformat()
    elif format_type == 'human':
        return dt.strftime('%Y년 %m월 %d일 %H:%M')
    elif format_type == 'date':
        return dt.strftime('%Y-%m-%d')
    elif format_type == 'time':
        return dt.strftime('%H:%M:%S')
    elif format_type == 'korean':
        return dt.strftime('%Y년 %m월 %d일')
    else:
        return dt.isoformat()


def parse_date_string(date_str: str) -> Optional[datetime]:
    """문자열을 datetime으로 변환"""
    if not date_str:
        return None
    
    # 지원하는 날짜 형식들
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y/%m/%d',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def get_relative_time(dt: datetime) -> str:
    """상대적 시간 표현 (예: 2시간 전, 3일 전)"""
    if not dt:
        return "알 수 없음"
    
    now = datetime.now()
    
    # 미래 시간인 경우
    if dt > now:
        diff = dt - now
        if diff.days > 0:
            return f"{diff.days}일 후"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 후"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 후"
        else:
            return "잠시 후"
    
    # 과거 시간인 경우
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}년 전"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}개월 전"
    elif diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"


def get_date_range(range_type: str) -> tuple:
    """날짜 범위 생성"""
    now = datetime.now()
    
    if range_type == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif range_type == 'yesterday':
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif range_type == 'this_week':
        # 이번 주 월요일부터 일요일까지
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif range_type == 'this_month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = now.replace(year=now.year+1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end = now.replace(month=now.month+1, day=1) - timedelta(microseconds=1)
    
    elif range_type == 'last_30_days':
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    elif range_type == 'this_year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    
    else:
        # 기본값: 최근 7일
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    return start, end


def group_by_date(items: List[Dict], date_field: str = 'created_at') -> Dict[str, List]:
    """날짜별로 아이템 그룹화"""
    groups = {}
    
    for item in items:
        date_value = item.get(date_field)
        
        if isinstance(date_value, str):
            date_value = parse_date_string(date_value)
        
        if isinstance(date_value, datetime):
            date_key = date_value.strftime('%Y-%m-%d')
        else:
            date_key = '날짜 없음'
        
        if date_key not in groups:
            groups[date_key] = []
        
        groups[date_key].append(item)
    
    return groups


def get_activity_stats(notes: List[Dict]) -> Dict:
    """노트 작성 활동 통계"""
    if not notes:
        return {
            "total_notes": 0,
            "notes_today": 0,
            "notes_this_week": 0,
            "notes_this_month": 0,
            "daily_average": 0,
            "most_active_day": None
        }
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start, _ = get_date_range('this_week')
    month_start, _ = get_date_range('this_month')
    
    notes_today = 0
    notes_this_week = 0
    notes_this_month = 0
    daily_counts = {}
    
    for note in notes:
        created_at = note.get('created_at')
        if isinstance(created_at, str):
            created_at = parse_date_string(created_at)
        
        if not isinstance(created_at, datetime):
            continue
        
        # 오늘 작성된 노트
        if created_at >= today_start:
            notes_today += 1
        
        # 이번 주 작성된 노트
        if created_at >= week_start:
            notes_this_week += 1
        
        # 이번 달 작성된 노트
        if created_at >= month_start:
            notes_this_month += 1
        
        # 일별 카운트
        date_key = created_at.strftime('%Y-%m-%d')
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    # 가장 활발했던 날
    most_active_day = None
    if daily_counts:
        most_active_date = max(daily_counts, key=daily_counts.get)
        most_active_day = {
            "date": most_active_date,
            "count": daily_counts[most_active_date]
        }
    
    # 일평균 계산 (최근 30일 기준)
    recent_days = len([d for d in daily_counts.keys() 
                      if parse_date_string(d) and parse_date_string(d) >= now - timedelta(days=30)])
    daily_average = round(sum(daily_counts.values()) / max(recent_days, 1), 1)
    
    return {
        "total_notes": len(notes),
        "notes_today": notes_today,
        "notes_this_week": notes_this_week,
        "notes_this_month": notes_this_month,
        "daily_average": daily_average,
        "most_active_day": most_active_day,
        "daily_counts": daily_counts
    }


def validate_date_range(start_date: str, end_date: str) -> tuple:
    """날짜 범위 유효성 검사"""
    start_dt = parse_date_string(start_date)
    end_dt = parse_date_string(end_date)
    
    errors = []
    
    if start_date and not start_dt:
        errors.append("시작 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    if end_date and not end_dt:
        errors.append("종료 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    if start_dt and end_dt and start_dt > end_dt:
        errors.append("시작 날짜는 종료 날짜보다 빨라야 합니다")
    
    # 너무 넓은 범위 체크 (1년 초과)
    if start_dt and end_dt and (end_dt - start_dt).days > 365:
        errors.append("날짜 범위는 1년을 초과할 수 없습니다")
    
    return start_dt, end_dt, errors


def get_time_periods() -> List[Dict]:
    """시간 구간 옵션 목록"""
    return [
        {"value": "today", "label": "오늘", "description": "오늘 작성된 노트"},
        {"value": "yesterday", "label": "어제", "description": "어제 작성된 노트"},
        {"value": "this_week", "label": "이번 주", "description": "이번 주 작성된 노트"},
        {"value": "this_month", "label": "이번 달", "description": "이번 달 작성된 노트"},
        {"value": "last_30_days", "label": "최근 30일", "description": "최근 30일간 작성된 노트"},
        {"value": "this_year", "label": "올해", "description": "올해 작성된 노트"}
    ]


def format_duration(seconds: int) -> str:
    """초를 사람이 읽기 쉬운 형태로 변환"""
    if seconds < 60:
        return f"{seconds}초"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}분"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}시간 {minutes}분"
        return f"{hours}시간"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if hours > 0:
            return f"{days}일 {hours}시간"
        return f"{days}일"


# 편의 함수들
def now_iso() -> str:
    """현재 시간을 ISO 형식으로 반환"""
    return datetime.now().isoformat()


def today_range() -> tuple:
    """오늘 날짜 범위 반환"""
    return get_date_range('today')


def is_recent(dt: datetime, hours: int = 24) -> bool:
    """최근 N시간 내인지 확인"""
    if not dt:
        return False
    
    now = datetime.now()
    threshold = now - timedelta(hours=hours)
    return dt >= threshold