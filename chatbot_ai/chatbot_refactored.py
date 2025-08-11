import os
import json
import re
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests
import faiss
from sentence_transformers import SentenceTransformer
import unicodedata
import colorama
from colorama import Fore, Style

# Initialize colorama on all platforms
colorama.init(autoreset=True)

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_chatbot.json")
VUE_DATA_FILE = os.path.join(BASE_DIR, "data_nganh_vue.json")
EMBEDDING_FILE = os.path.join(BASE_DIR, "nganh_embeddings.npy")
INDEX_FILE = os.path.join(BASE_DIR, "nganh_faiss.index")
ID_FILE = os.path.join(BASE_DIR, "nganh_ids.json")
CACHE_META_FILE = os.path.join(BASE_DIR, "nganh_cache_meta.json")
CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "chat_sessions.json")

# Models and RAG
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5
MIN_SIMILARITY_SCORE = 0.4
LLM_TIMEOUT = 60
MAX_HISTORY_LENGTH = 15

# Improved alias map
ALIAS_MAP: Dict[str, str] = {
    # CNTT
    'cntt': '7480201', 'it': '7480201', 'cong nghe thong tin': '7480201',
    'information technology': '7480201', 'tin hoc': '7480201', 'c.n.t.t': '7480201',
    'công nghệ thông tin': '7480201', 'it major': '7480201', 'it engineer': '7480201',
    'it ct': '7480201', 'it ctu': '7480201', 'itctu': '7480201',
    # Hệ thống thông tin
    'htt': '7480104', 'he thong thong tin': '7480104', 'information systems': '7480104',
    'hệ thống thông tin': '7480104', 'is': '7480104', 'is major': '7480104',
    # KHMT
    'khmt': '7480101', 'khoa hoc may tinh': '7480101', 'computer science': '7480101',
    'cs': '7480101', 'lap trinh': '7480101', 'programming': '7480101',
    'khoa học máy tính': '7480101', 'cs major': '7480101',
    # KTPM
    'ktpm': '7480103', 'ky thuat phan mem': '7480103', 'software engineering': '7480103',
    'se': '7480103', 'phan mem': '7480103', 'kỹ thuật phần mềm': '7480103',
    'software': '7480103', 'software dev': '7480103',
    # MMT
    'mmt': '7480102', 'mang may tinh': '7480102', 'network': '7480102',
    'mang': '7480102', 'computer network': '7480102', 'mạng máy tính': '7480102',
    'networking': '7480102', 'network engineer': '7480102',
    # TTNT
    'ttnt': '7480107', 'tri tue nhan tao': '7480107', 'artificial intelligence': '7480107',
    'ai': '7480107', 'machine learning': '7480107', 'ml': '7480107', 'ai major': '7480107',
    'trí tuệ nhân tạo': '7480107',
    # An toàn thông tin
    'attt': '7480202', 'an toan thong tin': '7480202', 'information security': '7480202',
    'an toàn thông tin': '7480202', 'security': '7480202', 'cyber security': '7480202',
    'infosec': '7480202',
    # Kinh tế
    'kinh te': '7310101', 'economics': '7310101', 'kinh tế': '7310101', 'eco': '7310101',
    # Kế toán
    'ke toan': '7340301', 'accounting': '7340301', 'kế toán': '7340301', 'kt': '7340301',
    # Quản trị kinh doanh
    'quan tri kinh doanh': '7340101', 'business': '7340101', 'business administration': '7340101',
    'qtkd': '7340101', 'quản trị kinh doanh': '7340101', 'ba': '7340101',
    # Marketing
    'marketing': '7340115', 'tiếp thị': '7340115', 'marketing major': '7340115',
}


class ColoredOutput:
    @staticmethod
    def print_header(text: str) -> None:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}\n{text}\n{'='*60}{Style.RESET_ALL}")

    @staticmethod
    def print_bot_response(text: str) -> None:
        print(f"\n{Fore.GREEN}🤖 {text}{Style.RESET_ALL}")

    @staticmethod
    def print_error(text: str) -> None:
        print(f"\n{Fore.RED}❌ {text}{Style.RESET_ALL}")

    @staticmethod
    def print_warning(text: str) -> None:
        print(f"\n{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

    @staticmethod
    def print_info(text: str) -> None:
        print(f"\n{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

    @staticmethod
    def print_success(text: str) -> None:
        print(f"\n{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


class ChatbotMemory:
    def __init__(self) -> None:
        self.current_session: List[Dict] = []
        self.user_preferences: Dict = {}
        self.conversation_context: Dict = {}
        self.last_nganh_context: Optional[Dict] = None

    def add_turn(self, question: str, answer: str, metadata: dict = None) -> None:
        turn = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "metadata": metadata or {}
        }
        self.current_session.append(turn)
        if len(self.current_session) > MAX_HISTORY_LENGTH:
            self.current_session = self.current_session[-MAX_HISTORY_LENGTH:]

    def get_context_for_llm(self) -> List[Dict]:
        return self.current_session[-5:] if self.current_session else []

    def save_session(self) -> None:
        try:
            sessions: List[Dict] = []
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
            if self.current_session:
                sessions.append({
                    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "turns": self.current_session
                })
            sessions = sessions[-10:]
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            ColoredOutput.print_warning(f"Không thể lưu lịch sử chat: {e}")

    def reset_session(self) -> None:
        self.current_session = []
        self.conversation_context = {}
        self.last_nganh_context = None


class SmartMatcher:
    @staticmethod
    def remove_accents(text: str) -> str:
        if not text:
            return ""
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

    @staticmethod
    def extract_year(text: str) -> Optional[str]:
        patterns = [r'năm\s*(20\d{2})', r'(20\d{2})', r'năm\s*(\d{2})']
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                year = match.group(1)
                if len(year) == 2:
                    year = "20" + year
                return year
        return None

    @staticmethod
    def extract_year_range(text: str) -> Optional[Tuple[str, str]]:
        text_l = text.lower()
        patterns = [
            r'từ\s*(20\d{2})\s*đến\s*(20\d{2})',
            r'giai\s*đoạn\s*(20\d{2})\s*(?:đến|-|–)\s*(20\d{2})',
            r'(20\d{2})\s*(?:-|–|đến)\s*(20\d{2})',
        ]
        for pattern in patterns:
            m = re.search(pattern, text_l)
            if m:
                start, end = m.group(1), m.group(2)
                if start > end:
                    start, end = end, start
                return start, end
        return None

    @staticmethod
    def extract_score_range(text: str) -> Tuple[Optional[float], Optional[float]]:
        patterns = [
            r'từ\s*([\d.]+)\s*đến\s*([\d.]+)',
            r'trên\s*([\d.]+)',
            r'dưới\s*([\d.]+)',
            r'>\s*([\d.]+)',
            r'<\s*([\d.]+)',
        ]
        text_l = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_l)
            if match:
                if pattern.startswith('từ'):
                    return float(match.group(1)), float(match.group(2))
                if 'trên' in pattern or '>' in pattern:
                    return float(match.group(1)), None
                if 'dưới' in pattern or '<' in pattern:
                    return None, float(match.group(1))
        return None, None

    @staticmethod
    def extract_admission_method(text: str) -> Optional[str]:
        text_lower = text.lower()
        method_keywords = {
            "điểm thi thpt": ["điểm thi thpt", "điểm thi tốt nghiệp", "điểm thi đại học"],
            "học bạ": ["học bạ", "xét học bạ", "điểm học bạ"],
            "kết hợp": ["kết hợp", "tổ hợp", "điểm kết hợp"],
            "xét tuyển thẳng": ["xét tuyển thẳng", "tuyển thẳng", "ưu tiên xét tuyển"],
            "phỏng vấn": ["phỏng vấn", "vấn đáp", "interview"],
        }
        for method, keywords in method_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return method
        return None

    @staticmethod
    def filter_by_admission_method(diem_chuan_list: List[Dict], method: str) -> List[Dict]:
        if not method:
            return diem_chuan_list
        filtered: List[Dict] = []
        for dc in diem_chuan_list:
            phuong_thuc = str(dc.get('phuong_thuc', '')).lower()
            if method == "điểm thi thpt":
                if any(kw in phuong_thuc for kw in ["điểm thi tốt nghiệp thpt", "xét điểm thi tốt nghiệp thpt", "điểm thi thpt"]):
                    filtered.append(dc)
            elif method == "học bạ":
                if any(kw in phuong_thuc for kw in ["học bạ thpt", "xét học bạ thpt", "học bạ"]):
                    filtered.append(dc)
            elif method == "kết hợp":
                if any(kw in phuong_thuc for kw in ["kết hợp", "tổ hợp"]):
                    filtered.append(dc)
            elif method == "xét tuyển thẳng":
                if any(kw in phuong_thuc for kw in ["tuyển thẳng", "ưu tiên"]):
                    filtered.append(dc)
        return filtered


class ImprovedChatbot:
    def __init__(self) -> None:
        self.model: Optional[SentenceTransformer] = None
        self.nganhs: List[Dict] = []
        self.vue_nganh_map: Dict[str, Dict] = {}
        self.embeddings: Optional[np.ndarray] = None
        self.index: Optional[faiss.Index] = None
        self.ids: List[int] = []
        self.memory = ChatbotMemory()
        self.is_loading = False
        self.last_question: Optional[str] = None

    # -------------------- Data Loading --------------------
    def load_data(self) -> bool:
        if not os.path.exists(DATA_FILE):
            ColoredOutput.print_error(f"File dữ liệu {DATA_FILE} không tồn tại!")
            return False
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.nganhs = data.get('nganhs', [])
            ColoredOutput.print_success(f"Đã load {len(self.nganhs)} ngành học từ {os.path.basename(DATA_FILE)}")
        except Exception as e:
            ColoredOutput.print_error(f"Lỗi khi load dữ liệu: {e}")
            return False
        # Merge từ Vue (nếu có)
        if os.path.exists(VUE_DATA_FILE):
            try:
                with open(VUE_DATA_FILE, 'r', encoding='utf-8') as f:
                    vue_data = json.load(f)
                self.vue_nganh_map = {}
                for item in vue_data:
                    ma_nganh = item.get('maNganh') or item.get('ma_nganh')
                    if ma_nganh:
                        self.vue_nganh_map[ma_nganh] = item
                for ng in self.nganhs:
                    ma_nganh = ng.get('ma_nganh')
                    vue_info = self.vue_nganh_map.get(ma_nganh)
                    if vue_info:
                        for key in ['gioiThieu', 'viTriViecLam', 'noiLamViec', 'thoiGianDaoTao', 'bangCap', 'khoa', 'phuongThucXetTuyen']:
                            if key in vue_info:
                                ng[key] = vue_info[key]
                ColoredOutput.print_success(f"Đã merge dữ liệu mô tả ngành từ {os.path.basename(VUE_DATA_FILE)}")
            except Exception as e:
                ColoredOutput.print_warning(f"Không thể load hoặc merge dữ liệu từ {os.path.basename(VUE_DATA_FILE)}: {e}")
        else:
            ColoredOutput.print_warning(f"Không tìm thấy file {os.path.basename(VUE_DATA_FILE)}, chỉ dùng dữ liệu từ {os.path.basename(DATA_FILE)}")
        return True

    def _loading_animation(self) -> None:
        chars = "|/-\\"
        i = 0
        while self.is_loading:
            print(f"\r{Fore.YELLOW}Đang tải model... {chars[i % len(chars)]}{Style.RESET_ALL}", end='')
            time.sleep(0.1)
            i += 1

    def load_model(self) -> bool:
        try:
            self.is_loading = True
            t = threading.Thread(target=self._loading_animation)
            t.start()
            self.model = SentenceTransformer(MODEL_NAME)
            self.is_loading = False
            t.join()
            print(f"\r{Fore.GREEN}✅ Model đã được tải thành công!{Style.RESET_ALL}")
            return True
        except Exception as e:
            self.is_loading = False
            ColoredOutput.print_error(f"Lỗi khi load model: {e}")
            return False

    # -------------------- Embeddings & Index --------------------
    def _compute_data_hash(self) -> str:
        sha = hashlib.sha256()
        for path in [DATA_FILE, VUE_DATA_FILE]:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        sha.update(chunk)
        return sha.hexdigest()

    def _load_cache_meta(self) -> Optional[Dict]:
        if not os.path.exists(CACHE_META_FILE):
            return None
        try:
            with open(CACHE_META_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_cache_meta(self, data_hash: str) -> None:
        try:
            with open(CACHE_META_FILE, 'w', encoding='utf-8') as f:
                json.dump({"data_hash": data_hash, "model": MODEL_NAME}, f)
        except Exception as e:
            ColoredOutput.print_warning(f"Không thể lưu cache meta: {e}")

    def build_enhanced_embeddings(self) -> Tuple[np.ndarray, faiss.Index, List[int]]:
        texts: List[str] = []
        ids: List[int] = []
        for idx, ng in enumerate(self.nganhs):
            components: List[str] = []
            if ng.get('nganh'):
                components.append(f"Tên ngành: {ng['nganh']}")
            if ng.get('ma_nganh'):
                components.append(f"Mã ngành: {ng['ma_nganh']}")
            if ng.get('mo_ta'):
                components.append(f"Mô tả: {ng['mo_ta']}")
            if ng.get('khoa'):
                components.append(f"Thuộc khoa: {ng['khoa']}")
            if ng.get('chi_tieu'):
                components.append(f"Chỉ tiêu tuyển sinh: {ng['chi_tieu']} sinh viên")
            alias_list: List[str] = []
            for alias, ma_nganh in ALIAS_MAP.items():
                if ng.get('ma_nganh') == ma_nganh:
                    alias_list.append(alias)
            if alias_list:
                components.append(f"Tên gọi khác: {', '.join(alias_list)}")
            if ng.get('diem_chuan'):
                try:
                    latest = max(
                        [d for d in ng['diem_chuan'] if d.get('nam') is not None and d.get('diem') is not None],
                        key=lambda d: int(str(d.get('nam'))[:4])
                    )
                    components.append(f"Điểm chuẩn gần nhất: {latest.get('diem', '')} năm {latest.get('nam', '')}")
                except Exception:
                    pass
            texts.append(". ".join(components))
            ids.append(idx)
        # Encode
        embeddings = self.model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return embeddings, index, ids

    def ensure_index(self) -> bool:
        data_hash = self._compute_data_hash()
        meta = self._load_cache_meta()
        cache_ok = (
            os.path.exists(EMBEDDING_FILE) and os.path.exists(INDEX_FILE) and os.path.exists(ID_FILE)
            and meta is not None and meta.get('data_hash') == data_hash and meta.get('model') == MODEL_NAME
        )
        try:
            if cache_ok:
                self.embeddings = np.load(EMBEDDING_FILE)
                self.index = faiss.read_index(INDEX_FILE)
                with open(ID_FILE, 'r', encoding='utf-8') as f:
                    self.ids = json.load(f)
                ColoredOutput.print_info("Đã load index từ cache")
                return True
        except Exception as e:
            ColoredOutput.print_warning(f"Lỗi khi load cache, tạo mới: {e}")
        ColoredOutput.print_info("Đang tạo embeddings và index...")
        self.embeddings, self.index, self.ids = self.build_enhanced_embeddings()
        try:
            np.save(EMBEDDING_FILE, self.embeddings)
            faiss.write_index(self.index, INDEX_FILE)
            with open(ID_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ids, f)
            self._save_cache_meta(data_hash)
            ColoredOutput.print_success("Đã lưu cache thành công")
        except Exception as e:
            ColoredOutput.print_warning(f"Không thể lưu cache: {e}")
        return True

    # -------------------- Retrieval / Matching --------------------
    def smart_keyword_match(self, question: str) -> Optional[Dict]:
        q_lower = question.lower()
        q_no_accent = SmartMatcher.remove_accents(q_lower)
        for alias, ma_nganh in ALIAS_MAP.items():
            if alias in q_no_accent:
                for ng in self.nganhs:
                    if ng.get('ma_nganh') == ma_nganh:
                        return ng
        for ng in self.nganhs:
            if ng.get('ma_nganh') and ng.get('ma_nganh') in question:
                return ng
        for ng in self.nganhs:
            if ng.get('nganh'):
                nganh_no_accent = SmartMatcher.remove_accents(ng['nganh'])
                if nganh_no_accent in q_no_accent:
                    return ng
        # Keywords in description
        keywords_found: List[Tuple[Dict, int]] = []
        words = [w for w in q_no_accent.split() if len(w) > 3]
        for ng in self.nganhs:
            mo_ta = ng.get('mo_ta')
            if mo_ta:
                mo_ta_no = SmartMatcher.remove_accents(mo_ta)
                count = sum(1 for w in words if w in mo_ta_no)
                if count > 0:
                    keywords_found.append((ng, count))
        if keywords_found:
            keywords_found.sort(key=lambda x: x[1], reverse=True)
            return keywords_found[0][0]
        return None

    def semantic_search(self, question: str, top_k: int = TOP_K) -> List[Tuple[Dict, float]]:
        q_emb = self.model.encode([question], normalize_embeddings=True)
        q_emb = np.array(q_emb).astype('float32')
        if q_emb.ndim == 1:
            q_emb = np.expand_dims(q_emb, 0)
        D, I = self.index.search(q_emb, top_k)
        results: List[Tuple[Dict, float]] = []
        for i, score in zip(I[0], D[0]):
            if score >= MIN_SIMILARITY_SCORE:
                results.append((self.nganhs[self.ids[i]], float(score)))
        return results

    def filter_by_criteria(self, nganhs: List[Dict], question: str) -> List[Dict]:
        year = SmartMatcher.extract_year(question)
        min_score, max_score = SmartMatcher.extract_score_range(question)
        admission_method = SmartMatcher.extract_admission_method(question)
        filtered: List[Dict] = []
        for ng in nganhs:
            ds = ng.get('diem_chuan') or []
            if year:
                ds = [dc for dc in ds if str(dc.get('nam')) == year]
                if not ds:
                    continue
            if admission_method:
                ds = SmartMatcher.filter_by_admission_method(ds, admission_method)
                if not ds:
                    continue
            if min_score is not None or max_score is not None:
                scores: List[float] = []
                for dc in ds:
                    try:
                        scores.append(float(dc.get('diem')))
                    except Exception:
                        pass
                if not scores:
                    continue
                if min_score is not None and all(s < min_score for s in scores):
                    continue
                if max_score is not None and all(s > max_score for s in scores):
                    continue
            filtered.append(ng)
        return filtered

    # -------------------- Answer generation --------------------
    def generate_smart_answer(self, question: str, ng: Dict, score: float = 1.0) -> str:
        q_lower = question.lower()
        year = SmartMatcher.extract_year(question)
        year_range = SmartMatcher.extract_year_range(question)
        method = SmartMatcher.extract_admission_method(question)
        if any(kw in q_lower for kw in ["phân tích", "đánh giá", "so sánh", "xu hướng", "biến động"]):
            if year_range:
                start_y, end_y = year_range
                return self._analyze_score_trend_range(ng, start_y, end_y)
            return self._analyze_score_trend(ng, year)
        if any(kw in q_lower for kw in ["điểm chuẩn", "điểm", "benchmark"]):
            return self._get_admission_scores(ng, year, method)
        if any(kw in q_lower for kw in ["điểm sàn", "tối thiểu", "minimum"]):
            return self._get_minimum_scores(ng, year)
        if any(kw in q_lower for kw in ["chỉ tiêu", "quota", "số lượng"]):
            return self._get_quota_info(ng)
        if any(kw in q_lower for kw in ["khoa", "faculty", "department"]):
            return self._get_faculty_info(ng)
        if any(kw in q_lower for kw in ["mô tả", "giới thiệu", "học gì", "ra trường làm gì"]):
            return self._get_program_description(ng)
        return self._get_comprehensive_info(ng)

    def _analyze_score_trend(self, ng: Dict, year: Optional[str] = None) -> str:
        if not ng.get('diem_chuan'):
            return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích xu hướng."
        if year:
            year_scores = {str(dc.get('nam')): float(dc.get('diem')) for dc in ng['diem_chuan'] if str(dc.get('nam')) == year and dc.get('diem')}
            if not year_scores:
                return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn năm {year}."
            result = f"📊 Điểm chuẩn {ng.get('nganh')} năm {year}\n"
            for y, s in year_scores.items():
                result += f" • Năm {y}: {s:.2f} điểm\n"
            return result
        year_scores: Dict[int, float] = {}
        for dc in ng['diem_chuan']:
            y = dc.get('nam')
            score = dc.get('diem')
            if y and score is not None:
                try:
                    s = float(score)
                except Exception:
                    continue
                if y not in year_scores or s > year_scores[y]:
                    year_scores[y] = s
        if len(year_scores) < 2:
            return f"📊 {ng.get('nganh')}: Cần ít nhất 2 năm dữ liệu để phân tích xu hướng."
        years = sorted(year_scores.keys())
        scores = [year_scores[y] for y in years]
        result = f"\n📈 Phân tích xu hướng điểm chuẩn ngành {ng.get('nganh')}\n"
        result += f"{'Năm':<8}{'Điểm':<12}{'Ghi chú'}\n"
        result += "-"*32 + "\n"
        for idx, y in enumerate(years):
            note = ""
            if idx > 0:
                d = scores[idx] - scores[idx-1]
                note = f"↑ +{d:.2f}" if d > 0 else (f"↓ {d:.2f}" if d < 0 else "=")
            result += f"{y:<8}{scores[idx]:<12.2f}{note}\n"
        avg_score = sum(scores) / len(scores)
        result += f"\n✨ Trung bình: {avg_score:.2f} | Cao nhất: {max(scores):.2f} | Thấp nhất: {min(scores):.2f} | Biên độ: {max(scores)-min(scores):.2f}\n"
        if scores[-1] > scores[0]:
            result += "- 📢 Xu hướng tăng, cần chuẩn bị tốt hơn."
        elif scores[-1] < scores[0]:
            result += "- 📢 Xu hướng giảm, cơ hội có thể cao hơn."
        else:
            result += "- 📢 Ổn định qua các năm."
        return result

    def _analyze_score_trend_range(self, ng: Dict, start_year: str, end_year: str) -> str:
        if not ng.get('diem_chuan'):
            return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích xu hướng."
        try:
            s_year, e_year = int(start_year), int(end_year)
            if s_year > e_year:
                s_year, e_year = e_year, s_year
        except Exception:
            return "📊 Khoảng năm không hợp lệ."
        year_scores: Dict[int, float] = {}
        for dc in ng['diem_chuan']:
            y = dc.get('nam')
            score = dc.get('diem')
            if isinstance(y, int) and s_year <= y <= e_year and score is not None:
                try:
                    s = float(score)
                except Exception:
                    continue
                if y not in year_scores or s > year_scores[y]:
                    year_scores[y] = s
        if not year_scores:
            return f"📊 {ng.get('nganh')}: Không có dữ liệu trong giai đoạn {s_year}-{e_year}."
        years = sorted(year_scores.keys())
        scores = [year_scores[y] for y in years]
        result = f"📈 Xu hướng điểm chuẩn {ng.get('nganh')} ({s_year}–{e_year})\n"
        for idx, y in enumerate(years):
            note = ""
            if idx > 0:
                d = scores[idx] - scores[idx-1]
                note = f" ↑ +{d:.2f}" if d > 0 else (f" ↓ {d:.2f}" if d < 0 else " =")
            result += f"- {y}: {scores[idx]:.2f}{note}\n"
        if len(scores) >= 2:
            delta = scores[-1] - scores[0]
            trend_text = "tăng" if delta > 0.25 else ("giảm" if delta < -0.25 else "ổn định")
            result += f"Tóm tắt: {trend_text} ({scores[0]:.2f} → {scores[-1]:.2f}, Δ {delta:.2f})."
        return result

    def _get_admission_scores(self, ng: Dict, year: Optional[str] = None, method: Optional[str] = None) -> str:
        if not ng.get('diem_chuan'):
            return f"📚 {ng.get('nganh')}: Chưa có dữ liệu điểm chuẩn."
        scores = ng['diem_chuan']
        if year:
            scores = [s for s in scores if str(s.get('nam')) == year]
            if not scores:
                return f"📚 {ng.get('nganh')}: Không có điểm chuẩn năm {year}."
        if method:
            filtered = SmartMatcher.filter_by_admission_method(scores, method)
            if filtered:
                s = filtered[0]
                return f"📚 {ng.get('nganh')} {f'năm {year} ' if year else ''}({s.get('phuong_thuc','')}): {s.get('diem','N/A')} điểm"
            return f"📚 {ng.get('nganh')}: Không có điểm chuẩn{f' năm {year}' if year else ''} cho phương thức {method}."
        result = f"📚 {ng.get('nganh')}"
        if year:
            result += f" năm {year}"
        result += ":\n"
        order = ["điểm thi", "thpt", "tốt nghiệp", "học bạ"]
        def weight(item: Dict) -> int:
            pt = str(item.get('phuong_thuc','')).lower()
            for idx, key in enumerate(order):
                if key in pt:
                    return idx
            return len(order)
        sorted_scores = sorted(scores, key=weight)
        for s in sorted_scores[:2]:
            result += f"• {s.get('phuong_thuc','')}: {s.get('diem','N/A')} điểm\n"
        if len(sorted_scores) > 2:
            result += f"... và {len(sorted_scores) - 2} phương thức khác"
        return result

    def _get_minimum_scores(self, ng: Dict, year: Optional[str] = None) -> str:
        tieu_chi = ng.get('tieu_chi_xet_tuyen') or []
        diem_san_data = []
        for tc in tieu_chi:
            if tc.get('diem_toi_thieu') is not None:
                diem_san_data.append({'nam': tc.get('nam'), 'diem_san': tc.get('diem_toi_thieu')})
        if not diem_san_data:
            return f"📝 {ng.get('nganh')}: Không có dữ liệu điểm sàn cụ thể."
        if year:
            diem_san_data = [d for d in diem_san_data if str(d.get('nam')) == year]
            if not diem_san_data:
                return f"📝 {ng.get('nganh')}: Không có điểm sàn năm {year}."
        result = f"📝 Điểm sàn {ng.get('nganh')}\n"
        for d in sorted(diem_san_data, key=lambda x: x.get('nam', 0), reverse=True):
            result += f" • Năm {d.get('nam', 'N/A')}: {d.get('diem_san', 'N/A')} điểm\n"
        return result

    def _get_quota_info(self, ng: Dict) -> str:
        chi_tieu = ng.get('chi_tieu')
        if not chi_tieu and ng.get('mo_ta'):
            match = re.search(r'[Cc]hỉ tiêu: ?(\d+)', ng['mo_ta'])
            if match:
                chi_tieu = match.group(1)
        if chi_tieu:
            nam_gan_nhat = None
            if ng.get('diem_chuan'):
                try:
                    nam_gan_nhat = max(ng['diem_chuan'], key=lambda d: int(str(d.get('nam'))[:4])).get('nam')
                except Exception:
                    nam_gan_nhat = None
            return f"🎯 {ng.get('nganh')}: {chi_tieu} sinh viên" + (f" (năm {nam_gan_nhat})" if nam_gan_nhat else "")
        return f"🎯 {ng.get('nganh')}: Chưa có thông tin chỉ tiêu"

    def _get_faculty_info(self, ng: Dict) -> str:
        result = f"🏫 Thông tin Khoa - {ng.get('nganh')}\n"
        khoa_info = ng.get('khoa')
        if khoa_info:
            if isinstance(khoa_info, dict):
                result += f" • Thuộc khoa: {khoa_info.get('tenKhoa', 'N/A')}\n"
            else:
                result += f" • Thuộc khoa: {khoa_info}\n"
        else:
            result += " • Chưa có thông tin khoa cụ thể\n"
        result += f" • Mã ngành: {ng.get('ma_nganh', 'N/A')}\n"
        if ng.get('mo_ta'):
            result += f" • Mô tả: {str(ng.get('mo_ta'))[:200]}...\n"
        return result

    def _get_program_description(self, ng: Dict) -> str:
        result = f"📖 Giới thiệu ngành {ng.get('nganh') or ng.get('tenNganh')}\n"
        mo_ta = ng.get('gioiThieu') or ng.get('mo_ta')
        if mo_ta:
            if len(mo_ta) > 350:
                cut_idx = mo_ta.rfind('.', 0, 350)
                mo_ta = mo_ta[:cut_idx+1] if cut_idx != -1 else mo_ta[:350] + '...'
            result += f"🎓 {mo_ta}\n"
        result += f"📋 Thông tin cơ bản:\n"
        result += f"   • Mã ngành: {ng.get('ma_nganh', ng.get('maNganh', 'N/A'))}\n"
        if ng.get('khoa'):
            if isinstance(ng['khoa'], dict):
                result += f"   • Khoa: {ng['khoa'].get('tenKhoa', ng['khoa'])}\n"
            else:
                result += f"   • Khoa: {ng['khoa']}\n"
        if ng.get('thoiGianDaoTao'):
            result += f"   • Thời gian đào tạo: {ng.get('thoiGianDaoTao')}\n"
        if ng.get('bangCap'):
            result += f"   • Bằng cấp: {ng.get('bangCap')}\n"
        return result

    def _get_comprehensive_info(self, ng: Dict) -> str:
        result = f"🎓 Thông tin tổng hợp - {ng.get('nganh')}\n\n"
        result += f"📋 Thông tin cơ bản:\n"
        result += f" • Tên ngành: {ng.get('nganh', 'N/A')}\n"
        result += f" • Mã ngành: {ng.get('ma_nganh', 'N/A')}\n"
        if ng.get('khoa'):
            if isinstance(ng['khoa'], dict):
                result += f" • Thuộc khoa: {ng['khoa'].get('tenKhoa', 'N/A')}\n"
            else:
                result += f" • Thuộc khoa: {ng['khoa']}\n"
        if ng.get('chi_tieu'):
            result += f" • Chỉ tiêu: {ng.get('chi_tieu')} sinh viên\n"
        if ng.get('diem_chuan'):
            try:
                latest = max(ng['diem_chuan'], key=lambda d: int(str(d.get('nam'))[:4]))
                result += f"\n🏆 Tuyển sinh:\n"
                result += f" • Điểm chuẩn gần nhất: {latest.get('diem', 'N/A')} điểm\n"
                result += f" • Năm: {latest.get('nam', 'N/A')}\n"
                result += f" • Phương thức: {latest.get('phuong_thuc', 'Chính quy')}\n"
            except Exception:
                pass
        if ng.get('mo_ta'):
            description = str(ng.get('mo_ta'))
            if len(description) > 150:
                description = description[:150] + "..."
            result += f"\n📝 Mô tả: {description}\n"
        return result

    # -------------------- LLM --------------------
    def check_llm_connection(self) -> bool:
        try:
            r = requests.get("http://localhost:11434/api/version", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def generate_llm_response(self, question: str, top_nganhs: List[Dict]) -> str:
        if not self.check_llm_connection():
            return "❌ Không thể kết nối đến Ollama server. Vui lòng chạy 'ollama serve' hoặc 'ollama run mistral' trước."
        context_parts: List[str] = []
        for ng in top_nganhs:
            part = f"Ngành: {ng.get('nganh','')}\nMã: {ng.get('ma_nganh','')}\nKhoa: {ng.get('khoa','')}\n"
            if ng.get('mo_ta'):
                part += f"Mô tả: {ng.get('mo_ta','')}\n"
            if ng.get('chi_tieu'):
                part += f"Chỉ tiêu: {ng.get('chi_tieu')} sinh viên\n"
            if ng.get('diem_chuan'):
                try:
                    latest = max(ng['diem_chuan'], key=lambda d: int(str(d.get('nam'))[:4]))
                    part += f"Điểm chuẩn: {latest.get('diem','')} ({latest.get('nam','')})\n"
                except Exception:
                    pass
            context_parts.append(part)
        context = "\n---\n".join(context_parts)
        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là tư vấn viên tuyển sinh đại học thân thiện. Hãy trả lời bằng tiếng Việt, ngắn gọn, chính xác, "
                    "chỉ dựa vào thông tin ngành bên dưới. Nếu không có thông tin, hãy nói 'Không có dữ liệu'.\n\n" 
                    + context
                ),
            }
        ]
        history = self.memory.get_context_for_llm()
        for turn in history[-3:]:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        messages.append({"role": "user", "content": question})
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "mistral",
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 500},
                },
                timeout=LLM_TIMEOUT,
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                return content or "🤖 Không có dữ liệu phù hợp để trả lời."
            return f"❌ Lỗi LLM: HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "⏰ Timeout: LLM phản hồi quá lâu, vui lòng thử lại."
        except Exception as e:
            return f"❌ Lỗi LLM: {e}"

    # -------------------- Intents & Flow --------------------
    def is_question_vague(self, question: str) -> bool:
        keywords = [
            "ngành", "điểm", "mã ngành", "tên ngành", "khoa", "chỉ tiêu",
            "năm", "mô tả", "tuyển sinh", "đại học", "cntt", "it", "khmt",
        ]
        q = SmartMatcher.remove_accents(question.lower())
        if len(question.strip()) < 5:
            return True
        if not any(k in q for k in keywords):
            return True
        if len(question.split()) <= 2:
            return True
        return False

    def suggest_questions(self) -> List[str]:
        return [
            "Điểm chuẩn CNTT 2023",
            "Chỉ tiêu ngành Khoa học máy tính",
            "So sánh điểm chuẩn CNTT và KTPM",
            "Phân tích xu hướng điểm ngành AI",
            "Ngành nào thuộc khoa CNTT?",
            "Mô tả ngành Mạng máy tính",
            "Điểm sàn các ngành IT 2023",
        ]

    def print_welcome(self) -> None:
        ColoredOutput.print_header("🎓 CHATBOT TƯ VẤN TUYỂN SINH THÔNG MINH 🤖")
        print(f"{Fore.CYAN}Chào mừng bạn! Tôi giúp tra cứu ngành học, điểm chuẩn, chỉ tiêu...{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}💡 Tính năng:")
        for f in [
            "🔍 Tìm kiếm thông minh (từ khóa + ngữ nghĩa)",
            "📊 Phân tích xu hướng điểm chuẩn",
            "🤖 Trả lời tự nhiên bằng AI",
            "💾 Nhớ ngữ cảnh hội thoại",
            "🎯 Lọc theo năm, phương thức, khoảng điểm",
            "⚡ Cache thông minh",
        ]:
            print(f"   {f}")
        print(f"\n{Fore.GREEN}📝 Lệnh: \n   • help\n   • suggest\n   • reset\n   • stats\n   • exit{Style.RESET_ALL}")

    def print_help(self) -> None:
        print(
            f"""
{Fore.CYAN}📚 HƯỚNG DẪN{Style.RESET_ALL}
- Dùng tên ngành, mã ngành hoặc alias (VD: CNTT, 7480201)
- Chỉ định năm (VD: điểm chuẩn CNTT 2023)
- Khoảng điểm (VD: ngành nào dưới 20 điểm)
- Phân tích xu hướng (VD: phân tích điểm AI 2021-2023)
"""
        )

    def print_stats(self) -> None:
        print(
            f"""
{Fore.CYAN}📈 THỐNG KÊ{Style.RESET_ALL}
• Tổng số ngành: {len(self.nganhs)}
• Số ngành có điểm chuẩn: {len([ng for ng in self.nganhs if ng.get('diem_chuan')])}
• Cache embeddings: {'✅' if os.path.exists(EMBEDDING_FILE) else '❌'}
• Cache FAISS index: {'✅' if os.path.exists(INDEX_FILE) else '❌'}
• Model: {MODEL_NAME}
• LLM: {'🟢 Connected' if self.check_llm_connection() else '🔴 Disconnected'}
"""
        )

    def extract_multiple_majors(self, question: str, top_k: int = 5) -> List[Dict]:
        found: List[Dict] = []
        used: set = set()
        q_noaccent = SmartMatcher.remove_accents(question.lower())
        for alias, ma in ALIAS_MAP.items():
            if alias in q_noaccent and ma not in used:
                for ng in self.nganhs:
                    if ng.get('ma_nganh') == ma:
                        found.append(ng)
                        used.add(ma)
                        if len(found) == 2:
                            return found
        if len(found) < 2:
            for ng, _score in self.semantic_search(question, top_k=top_k):
                ma = ng.get('ma_nganh')
                if ma and ma not in used:
                    found.append(ng)
                    used.add(ma)
                    if len(found) == 2:
                        break
        return found

    def is_reference_to_previous_major(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in ["ngành này", "ngành đó", "ngành trên", "ngành vừa hỏi", "ngành vừa rồi"])

    def is_career_question(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in ["vị trí việc làm", "nghề nghiệp", "job", "career", "ra trường làm gì", "làm gì", "cơ hội việc làm"])

    def is_workplace_question(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in ["nơi làm việc", "làm ở đâu", "workplace", "công ty", "doanh nghiệp", "làm việc ở đâu"])

    def is_quota_question(self, question: str) -> bool:
        q = question.lower()
        return any(kw in q for kw in ["chỉ tiêu", "quota", "số lượng tuyển", "tuyển sinh bao nhiêu", "bao nhiêu chỉ tiêu"])

    def _list_faculty_programs(self, target_khoa: str) -> str:
        matching: List[Dict] = []
        for ng in self.nganhs:
            khoa_info = ng.get('khoa')
            if not khoa_info:
                continue
            khoa_str = str(khoa_info.get('tenKhoa', '')) if isinstance(khoa_info, dict) else str(khoa_info)
            ks = khoa_str.lower()
            if target_khoa in ks or any(kw in ks for kw in target_khoa.split()):
                matching.append(ng)
        if matching:
            result = f"🏫 Ngành thuộc khoa {target_khoa.title()}:\n\n"
            for ng in matching[:6]:
                result += f"🎓 {ng.get('nganh','N/A')} ({ng.get('ma_nganh','N/A')})\n"
            if len(matching) > 6:
                result += f"\n... và {len(matching) - 6} ngành khác"
            return result
        return f"❌ Không tìm thấy ngành nào thuộc khoa {target_khoa.title()}"

    def process_question(self, question: str) -> str:
        self.last_question = question
        # Early vague detection
        if self.is_question_vague(question):
            sugg = self.suggest_questions()
            return "Mình cần thêm chi tiết (tên/mã ngành, năm...). Ví dụ:\n- " + "\n- ".join(sugg[:3])
        q_lower = question.lower()
        year = SmartMatcher.extract_year(question)
        min_score, max_score = SmartMatcher.extract_score_range(question)
        # Faculty listing intent
        if any(kw in q_lower for kw in ["thuộc khoa", "ngành nào thuộc khoa", "khoa nào có ngành"]):
            khoa_keywords = ["công nghệ thông tin", "cntt", "y khoa", "y tế", "kinh tế", "luật", "sư phạm", "nông nghiệp"]
            for keyword in khoa_keywords:
                if keyword in q_lower:
                    return self._list_faculty_programs(keyword)
        # Below X points
        if max_score is not None:
            matching: List[Dict] = []
            for ng in self.nganhs:
                ds = ng.get('diem_chuan') or []
                if year:
                    ds = [dc for dc in ds if str(dc.get('nam')) == year]
                if not ds:
                    continue
                for dc in ds:
                    try:
                        score_val = float(dc.get('diem', 0))
                    except Exception:
                        continue
                    if score_val < max_score:
                        matching.append({
                            'nganh': ng.get('nganh'),
                            'score': score_val,
                            'year': dc.get('nam'),
                            'method': dc.get('phuong_thuc', 'Không rõ')
                        })
                        break
            if matching:
                matching.sort(key=lambda x: x['score'])
                result = f"📊 Ngành có điểm chuẩn dưới {max_score} điểm" + (f" năm {year}" if year else "") + ":\n\n"
                for item in matching[:8]:
                    result += f"🎓 {item['nganh']}: {item['score']:.1f} điểm\n"
                if len(matching) > 8:
                    result += f"\n... và {len(matching) - 8} ngành khác"
                return result
            return f"❌ Không tìm thấy ngành nào có điểm chuẩn dưới {max_score} điểm"
        # Above X points
        if min_score is not None:
            admission_method = SmartMatcher.extract_admission_method(question)
            matching: List[Dict] = []
            for ng in self.nganhs:
                ds = ng.get('diem_chuan') or []
                if year:
                    ds = [dc for dc in ds if str(dc.get('nam')) == year]
                if not ds:
                    continue
                if admission_method:
                    ds = SmartMatcher.filter_by_admission_method(ds, admission_method)
                    if not ds:
                        continue
                for dc in ds:
                    try:
                        score_val = float(dc.get('diem', 0))
                    except Exception:
                        continue
                    if score_val >= min_score:
                        matching.append({
                            'nganh': ng.get('nganh'),
                            'score': score_val,
                            'year': dc.get('nam'),
                            'method': dc.get('phuong_thuc', 'Không rõ')
                        })
                        break
            if matching:
                matching.sort(key=lambda x: x['score'], reverse=True)
                result = f"📊 Ngành có điểm chuẩn trên {min_score} điểm" + (f" năm {year}" if year else "")
                if admission_method:
                    result += f" ({admission_method})"
                result += ":\n\n"
                for item in matching[:8]:
                    result += f"🎓 {item['nganh']}: {item['score']:.1f} điểm\n"
                if len(matching) > 8:
                    result += f"\n... và {len(matching) - 8} ngành khác"
                return result
            method_text = f" theo phương thức {admission_method}" if admission_method else ""
            return f"❌ Không tìm thấy ngành nào có điểm chuẩn trên {min_score} điểm{method_text}"
        # Follow-up intent to previous major
        if self.is_reference_to_previous_major(question) and self.memory.last_nganh_context:
            ng = self.memory.last_nganh_context
            if self.is_career_question(question) and ng.get('viTriViecLam'):
                result = f"💼 Vị trí việc làm tiêu biểu ngành {ng.get('nganh', ng.get('tenNganh'))}:\n"
                for vt in ng['viTriViecLam']:
                    result += f"   - {vt}\n"
                return result
            if self.is_workplace_question(question) and ng.get('noiLamViec'):
                result = f"🏢 Nơi làm việc phổ biến ngành {ng.get('nganh', ng.get('tenNganh'))}:\n"
                for nlv in ng['noiLamViec']:
                    result += f"   - {nlv}\n"
                return result
            if self.is_quota_question(question):
                return self._get_quota_info(ng)
            return self.generate_smart_answer(question, ng, 1.0)
        # Keyword match intent
        matched_nganh = self.smart_keyword_match(question)
        if matched_nganh:
            if self.is_career_question(question) and matched_nganh.get('viTriViecLam'):
                self.memory.last_nganh_context = matched_nganh
                result = f"💼 Vị trí việc làm tiêu biểu ngành {matched_nganh.get('nganh', matched_nganh.get('tenNganh'))}:\n"
                for vt in matched_nganh['viTriViecLam']:
                    result += f"   - {vt}\n"
                return result
            if self.is_workplace_question(question) and matched_nganh.get('noiLamViec'):
                self.memory.last_nganh_context = matched_nganh
                result = f"🏢 Nơi làm việc phổ biến ngành {matched_nganh.get('nganh', matched_nganh.get('tenNganh'))}:\n"
                for nlv in matched_nganh['noiLamViec']:
                    result += f"   - {nlv}\n"
                return result
            if self.is_quota_question(question):
                self.memory.last_nganh_context = matched_nganh
                return self._get_quota_info(matched_nganh)
            ColoredOutput.print_info(f"Tìm thấy ngành: {matched_nganh.get('nganh')} (keyword match)")
            self.memory.last_nganh_context = matched_nganh
            return self.generate_smart_answer(question, matched_nganh, 1.0)
        # Semantic search
        results = self.semantic_search(question, TOP_K)
        if self.is_reference_to_previous_major(question) and self.memory.last_nganh_context:
            ColoredOutput.print_info("Nhận diện câu hỏi tham chiếu ngành trước đó.")
            return self.generate_smart_answer(question, self.memory.last_nganh_context, 1.0)
        if not results or (results and results[0][1] < 0.7 and self.memory.last_nganh_context):
            ColoredOutput.print_info("Score thấp hoặc không tìm thấy ngành, dùng context ngành trước đó.")
            return self.generate_smart_answer(question, self.memory.last_nganh_context, 1.0)
        candidate_nganhs = [ng for ng, _s in results]
        filtered_nganhs = self.filter_by_criteria(candidate_nganhs, question) or candidate_nganhs
        # confident hit
        if results and results[0][1] > 0.75:
            best_nganh, score = results[0]
            if self.is_career_question(question) and best_nganh.get('viTriViecLam'):
                self.memory.last_nganh_context = best_nganh
                result = f"💼 Vị trí việc làm tiêu biểu ngành {best_nganh.get('nganh', best_nganh.get('tenNganh'))}:\n"
                for vt in best_nganh['viTriViecLam']:
                    result += f"   - {vt}\n"
                return result
            if self.is_workplace_question(question) and best_nganh.get('noiLamViec'):
                self.memory.last_nganh_context = best_nganh
                result = f"🏢 Nơi làm việc phổ biến ngành {best_nganh.get('nganh', best_nganh.get('tenNganh'))}:\n"
                for nlv in best_nganh['noiLamViec']:
                    result += f"   - {nlv}\n"
                return result
            if self.is_quota_question(question):
                self.memory.last_nganh_context = best_nganh
                return self._get_quota_info(best_nganh)
            ColoredOutput.print_info(f"Tìm thấy ngành: {best_nganh.get('nganh')} (score: {score:.3f})")
            self.memory.last_nganh_context = best_nganh
            return self.generate_smart_answer(question, best_nganh, score)
        # Fallback LLM
        ColoredOutput.print_info("Sử dụng AI để trả lời...")
        llm_response = self.generate_llm_response(question, filtered_nganhs[:3])
        if not llm_response or "⏰ Timeout" in llm_response or "❌" in llm_response:
            return (
                "🤖 Xin lỗi, tôi chưa thể trả lời rõ câu hỏi này. Hãy nêu cụ thể tên ngành hoặc năm học, "
                "hoặc thử lại sau nếu máy chủ AI bị gián đoạn."
            )
        if len(filtered_nganhs) == 1:
            self.memory.last_nganh_context = filtered_nganhs[0]
        return llm_response

    # -------------------- CLI --------------------
    def run(self) -> None:
        self.print_welcome()
        if not self.load_data():
            return
        if not self.load_model():
            return
        if not self.ensure_index():
            return
        ColoredOutput.print_success("Hệ thống đã sẵn sàng! Hãy đặt câu hỏi đầu tiên 🚀")
        while True:
            try:
                question = input(f"\n{Fore.CYAN}❓ Câu hỏi: {Style.RESET_ALL}").strip()
                if not question:
                    ColoredOutput.print_warning("Vui lòng nhập câu hỏi!")
                    continue
                q_lower = question.lower()
                if q_lower == 'exit':
                    ColoredOutput.print_info("Đang lưu lịch sử...")
                    self.memory.save_session()
                    ColoredOutput.print_success("Cám ơn bạn đã sử dụng! Tạm biệt! 👋")
                    break
                if q_lower == 'reset':
                    self.memory.reset_session()
                    ColoredOutput.print_success("Đã xóa lịch sử hội thoại!")
                    continue
                if q_lower == 'help':
                    self.print_help()
                    continue
                if q_lower == 'stats':
                    self.print_stats()
                    continue
                if q_lower == 'suggest':
                    suggestions = self.suggest_questions()
                    ColoredOutput.print_info("💡 Câu hỏi gợi ý:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion}")
                    continue
                start_time = time.time()
                answer = self.process_question(question)
                response_time = time.time() - start_time
                ColoredOutput.print_bot_response(answer)
                if response_time > 1:
                    print(f"{Fore.LIGHTBLACK_EX}⏱️  Thời gian phản hồi: {response_time:.2f}s{Style.RESET_ALL}")
                self.memory.add_turn(question, answer, {"response_time": response_time})
            except KeyboardInterrupt:
                ColoredOutput.print_info("\n\nĐang thoát...")
                self.memory.save_session()
                ColoredOutput.print_success("Tạm biệt! 👋")
                break
            except Exception as e:
                ColoredOutput.print_error(f"Lỗi không mong muốn: {e}")
                ColoredOutput.print_info("Vui lòng thử lại với câu hỏi khác.")


def main() -> None:
    try:
        chatbot = ImprovedChatbot()
        chatbot.run()
    except Exception as e:
        ColoredOutput.print_error(f"Lỗi khởi tạo chatbot: {e}")
        print("Vui lòng kiểm tra:\n1. File data_chatbot.json có tồn tại không\n2. Các thư viện đã được cài đặt chưa\n3. Model embedding có thể tải được không")


if __name__ == "__main__":
    main()