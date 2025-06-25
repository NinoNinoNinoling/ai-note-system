# backend/app/repositories/base_repository.py
"""
BaseRepository - 모든 레포지토리의 기본 클래스

기본 CRUD 작업, 공통 쿼리 패턴을 제공
"""

from config.database import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """모든 레포지토리의 기본 클래스"""
    
    def __init__(self, model):
        """
        Args:
            model: SQLAlchemy 모델 클래스 (예: Note)
        """
        self.model = model
        self.session = db.session
    
    def find_all(self, limit=None, offset=None):
        """모든 레코드 조회"""
        try:
            query = self.model.query
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
                
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding all {self.model.__name__}: {e}")
            raise
    
    def find_by_id(self, id):
        """ID로 레코드 조회"""
        try:
            return self.model.query.get(id)
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model.__name__} by id {id}: {e}")
            raise
    
    def create(self, **kwargs):
        """새 레코드 생성"""
        try:
            # Note 모델의 경우 태그를 별도 처리
            tags_value = None
            if hasattr(self.model, 'set_tags') and 'tags' in kwargs:
                tags_value = kwargs.pop('tags')  # kwargs에서 제거
            
            instance = self.model(**kwargs)
            
            # 태그 설정
            if tags_value is not None and hasattr(instance, 'set_tags'):
                instance.set_tags(tags_value)
            
            self.session.add(instance)
            self.session.commit()
            
            logger.info(f"Created {self.model.__name__} with id: {instance.id}")
            return instance
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def update(self, instance, **kwargs):
        """기존 레코드 업데이트"""
        try:
            # 태그 처리 (Note 모델의 경우)
            if hasattr(instance, 'set_tags') and 'tags' in kwargs:
                instance.set_tags(kwargs['tags'])
                # tags는 별도 처리했으므로 kwargs에서 제거
                kwargs = {k: v for k, v in kwargs.items() if k != 'tags'}
            
            # 나머지 필드들 업데이트
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.session.commit()
            
            logger.info(f"Updated {self.model.__name__} with id: {instance.id}")
            return instance
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    def delete(self, instance):
        """레코드 삭제"""
        try:
            self.session.delete(instance)
            self.session.commit()
            
            logger.info(f"Deleted {self.model.__name__} with id: {instance.id}")
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise
    
    def delete_by_id(self, id):
        """ID로 레코드 삭제"""
        try:
            instance = self.find_by_id(id)
            if not instance:
                return False
            
            return self.delete(instance)
            
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} by id {id}: {e}")
            raise
    
    def count(self):
        """전체 레코드 수"""
        try:
            return self.model.query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    def exists(self, id):
        """ID로 레코드 존재 확인"""
        try:
            return self.model.query.filter(self.model.id == id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            raise
    
    def find_by_field(self, field_name, value):
        """특정 필드값으로 조회"""
        try:
            if not hasattr(self.model, field_name):
                raise ValueError(f"Model {self.model.__name__} has no field '{field_name}'")
            
            field = getattr(self.model, field_name)
            return self.model.query.filter(field == value).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model.__name__} by {field_name}: {e}")
            raise
    
    def find_one_by_field(self, field_name, value):
        """특정 필드값으로 단일 레코드 조회"""
        try:
            if not hasattr(self.model, field_name):
                raise ValueError(f"Model {self.model.__name__} has no field '{field_name}'")
            
            field = getattr(self.model, field_name)
            return self.model.query.filter(field == value).first()
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model.__name__} by {field_name}: {e}")
            raise