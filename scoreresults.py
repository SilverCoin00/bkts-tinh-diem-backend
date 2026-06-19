from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from program_data import programs_data # Import data từ file data.py (hoặc đọc từ JSON)

router = APIRouter()

# 1. Định nghĩa cấu trúc dữ liệu nhận từ Frontend (Tương đương interface ScoreResult)
class Combination(BaseModel):
    code: str
    score: float

class ScoreResultInput(BaseModel):
    xetTuyenTN: Optional[float] = None
    diemTSA: Optional[float] = None
    diemXTTN12: Optional[float] = None
    combinations: List[Combination] = []

# 2. Logic tính toán và trả kết quả
@router.post("/api/suggest-programs")
def suggest_programs(results: ScoreResultInput):
    suitable_programs = []
    K01_SUB_COMBOS = ["K01_LY", "K01_HOA", "K01_SINH", "K01_TIN"]

    for prog in programs_data:
        is_eligible = False
        highest_score = 0.0

        # Tiêu chí 1: XTTN 1.3
        if results.xetTuyenTN is not None and prog.get("xttn3Predict") is not None:
            if results.xetTuyenTN >= prog["xttn3Predict"]:
                is_eligible = True
                highest_score = max(highest_score, results.xetTuyenTN)

        # Tiêu chí 2: TSA
        if results.diemTSA is not None and prog.get("tsaPredict") is not None:
            if results.diemTSA >= prog["tsaPredict"]:
                is_eligible = True
                highest_score = max(highest_score, results.diemTSA)

        # Tiêu chí 3: XTTN 1.2
        if results.diemXTTN12 is not None and prog.get("xttn2Predict") is not None:
            if results.diemXTTN12 >= prog["xttn2Predict"]:
                is_eligible = True
                highest_score = max(highest_score, results.diemXTTN12)

        # Tiêu chí 4: Tổ hợp môn
        prog_combos = prog.get("combinations", [])
        admission_predict = prog.get("admissionPredict")

        if admission_predict is not None and prog_combos:
            for user_combo in results.combinations:
                is_match = False
                
                # Kiểm tra tổ hợp con của K01
                if user_combo.code in K01_SUB_COMBOS and "K01" in prog_combos:
                    if user_combo.score >= admission_predict:
                        is_match = True
                # Kiểm tra tổ hợp bình thường
                elif user_combo.code in prog_combos:
                    if user_combo.score >= admission_predict:
                        is_match = True

                if is_match:
                    is_eligible = True
                    highest_score = max(highest_score, user_combo.score)

        # Nếu thoả mãn ít nhất 1 tiêu chí, đưa vào danh sách phù hợp
        if is_eligible:
            matched_prog = prog.copy() # Tránh thay đổi data gốc
            matched_prog["calculatedScore"] = highest_score
            suitable_programs.append(matched_prog)

    # 3. Thuật toán Sắp xếp (Ưu tiên ngành Điện -> Điểm chuẩn giảm dần)
    def sort_key(p):
        is_electrical = p.get("isElectrical", False)
        # Python sort tăng dần. Mẹo: dùng số âm để sort giảm dần.
        if is_electrical:
            # Ngành điện lên đầu (ưu tiên 0), sort giảm dần theo admissionPredict
            score = p.get("admissionPredict") or 0.0
            return (0, -score)
        else:
            # Ngành khác xuống dưới (ưu tiên 1), sort giảm dần theo tsaPredict
            score = p.get("tsaPredict") or 0.0
            return (1, -score)

    suitable_programs.sort(key=sort_key)

    return suitable_programs

# Chạy server: uvicorn main:app --reload