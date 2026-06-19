from fastapi import APIRouter
from pydantic import BaseModel
import re
from language_conversions_data import language_conversions

router = APIRouter()

# 1. BẢNG DICT DATA TỪ FRONTEND CHUYỂN SANG:

# 2. MODELS YÊU CẦU API
class ConvertReq(BaseModel):
    certificate: str
    score: str

class ToeicReq(BaseModel):
    listening: str
    reading: str
    speaking: str
    writing: str

# 3. LÕI HÀM XỬ LÝ (Từ Frontend chuyển vào)
def get_conversion_logic(certificate: str, score: str):
    conversion = next((c for c in language_conversions if c["certificate"] == certificate), None)
    if not conversion:
        return {"convertedScore": 0.0, "bonusScore": 0.0}
    
    score_str = str(score).strip()
    
    for r in conversion["scoreRanges"]:
        # Khớp tuyệt đối
        if score_str == r["value"]:
            return {"convertedScore": float(r["convertedScore"]), "bonusScore": float(r["bonusScore"])}
        
        # Khớp theo dải điểm "a-b"
        match = re.match(r"^(\d+(\.\d+)?)-(\d+(\.\d+)?)$", r["value"])
        if match:
            start = float(match.group(1))
            end = float(match.group(3))
            try:
                num_score = float(score_str)
                if start <= num_score <= end:
                    return {"convertedScore": float(r["convertedScore"]), "bonusScore": float(r["bonusScore"])}
            except ValueError:
                pass
                
    return {"convertedScore": 0.0, "bonusScore": 0.0}

# 4. CÁC ĐƯỜNG DẪN API
@router.get("/api/language-dict")
def get_language_dict():
    """Trả về bảng dữ liệu dictionary cho file ScoreInputForm map Key-Value"""
    return language_conversions

@router.post("/api/convert-score")
def convert_score(req: ConvertReq):
    """Thay thế hàm convertLanguageScore"""
    return get_conversion_logic(req.certificate, req.score)

@router.post("/api/convert-toeic")
def convert_toeic(req: ToeicReq):
    """Thay thế hàm convertToeicAllSkills"""
    skills = [
        ("TOEIC Listening", req.listening),
        ("TOEIC Reading", req.reading),
        ("TOEIC Speaking", req.speaking),
        ("TOEIC Writing", req.writing)
    ]
    total_converted = 0
    total_bonus = 0
    
    for cert, score in skills:
        res = get_conversion_logic(cert, score)
        total_converted += res["convertedScore"]
        total_bonus += res["bonusScore"]
        
    return {
        "convertedScore": round(total_converted / 4, 2),
        "bonusScore": round(total_bonus / 4, 2)
    }
