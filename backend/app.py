# backend/app.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 환경변수에서 설정 읽기
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 노트 모델
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 라우트
@app.route('/')
def index():
    note_count = Note.query.count()
    return jsonify({
        "message": "AI Note System", 
        "status": "running",
        "total_notes": note_count
    })

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([{
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat()
    } for note in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    from flask import request
    data = request.get_json()
    
    note = Note(
        title=data.get('title', '제목 없음'),
        content=data.get('content', '')
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat()
    }), 201

@app.route('/test-db')
def test_db():
    # DB 테이블 생성
    db.create_all()
    
    # 테스트 노트 생성
    test_note = Note(title="첫 번째 노트", content="DB 테스트입니다!")
    db.session.add(test_note)
    db.session.commit()
    
    return jsonify({
        "status": "✅ DB 테스트 성공!",
        "note_id": test_note.id,
        "note_count": Note.query.count()
    })

if __name__ == '__main__':
    print("🧠 AI Note System 시작!")
    print("📍 http://localhost:5000")
    app.run(debug=True)