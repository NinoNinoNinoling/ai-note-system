# backend/models/note.py
from datetime import datetime
import json
from config.database import db

class Note(db.Model):
    """노트 모델"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500))  # JSON 문자열로 저장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환 (API 응답용)"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_tags(self, tags_list):
        """태그 리스트를 JSON 문자열로 저장"""
        if isinstance(tags_list, list):
            self.tags = json.dumps(tags_list, ensure_ascii=False)
        elif isinstance(tags_list, str):
            # 콤마로 구분된 문자열을 리스트로 변환
            tag_list = [tag.strip() for tag in tags_list.split(',') if tag.strip()]
            self.tags = json.dumps(tag_list, ensure_ascii=False)
        else:
            self.tags = json.dumps([], ensure_ascii=False)
    
    def get_tags(self):
        """저장된 태그를 리스트로 반환"""
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_tag(self, tag):
        """태그 추가"""
        current_tags = self.get_tags()
        if tag not in current_tags:
            current_tags.append(tag)
            self.set_tags(current_tags)
    
    def remove_tag(self, tag):
        """태그 제거"""
        current_tags = self.get_tags()
        if tag in current_tags:
            current_tags.remove(tag)
            self.set_tags(current_tags)
    
    def has_tag(self, tag):
        """특정 태그 포함 여부 확인"""
        return tag in self.get_tags()
    
    @classmethod
    def search_by_content(cls, query):
        """내용으로 노트 검색"""
        return cls.query.filter(
            cls.title.contains(query) | cls.content.contains(query)
        ).order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def search_by_tag(cls, tag):
        """태그로 노트 검색"""
        return cls.query.filter(cls.tags.contains(f'"{tag}"')).order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_all_tags(cls):
        """모든 노트의 태그 목록 반환"""
        notes = cls.query.all()
        all_tags = set()
        
        for note in notes:
            all_tags.update(note.get_tags())
        
        return sorted(list(all_tags))
    
    @classmethod
    def get_recent_notes(cls, limit=10):
        """최근 노트 목록"""
        return cls.query.order_by(cls.updated_at.desc()).limit(limit).all()

class ChatHistory(db.Model):
    """채팅 히스토리 모델"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100), default='Claude')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    note = db.relationship('Note', backref='chat_sessions')
    
    def __repr__(self):
        return f'<ChatHistory {self.id}: {self.user_message[:50]}...>'
    
    def to_dict(self):
        """딕셔너리 형태로 변환"""
        return {
            'id': self.id,
            'note_id': self.note_id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_recent_chats(cls, note_id=None, limit=20):
        """최근 채팅 기록"""
        query = cls.query
        if note_id:
            query = query.filter_by(note_id=note_id)
        return query.order_by(cls.created_at.desc()).limit(limit).all()