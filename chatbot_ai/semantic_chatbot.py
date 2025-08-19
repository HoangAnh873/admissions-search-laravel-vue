import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import unicodedata
import re
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import colorama
from colorama import Fore, Style, Back
import threading
import matplotlib.pyplot as plt
import io
import base64


# Khởi tạo colorama cho Windows
colorama.init()

# Cấu hình file
DATA_FILE = "data_chatbot.json"
VUE_DATA_FILE = "data_nganh_vue.json"
EMBEDDING_FILE = "nganh_embeddings.npy"
INDEX_FILE = "nganh_faiss.index"
ID_FILE = "nganh_ids.json"
CHAT_HISTORY_FILE = "chat_sessions.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# Cải tiến bản đồ alias với nhiều từ khóa hơn
ALIAS_MAP = {
    # CNTT
    'cntt': '7480201', 'it': '7480201', 'cong nghe thong tin': '7480201',
    'information technology': '7480201', 'tin hoc': '7480201', 'c.n.t.t': '7480201',
    'công nghệ thông tin': '7480201', 'it major': '7480201', 'it engineer': '7480201',
    'it ct': '7480201', 'it ctu': '7480201', 'itctu': '7480201',
    # Hệ thống thông tin
    'httt': '7480104', 'he thong thong tin': '7480104', 'information systems': '7480104',
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
    # Thêm các ngành khác nếu cần
}

# Cấu hình RAG và LLM
TOP_K = 5
MIN_SIMILARITY_SCORE = 0.4
LLM_TIMEOUT = 60
MAX_HISTORY_LENGTH = 15

class ColoredOutput:
    """Class để quản lý màu sắc output"""
    
    @staticmethod
    def print_header(text: str):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{text}")
        print(f"{'='*60}{Style.RESET_ALL}")
    
    @staticmethod
    def print_bot_response(text: str):
        print(f"\n{Fore.GREEN}🤖 {text}{Style.RESET_ALL}")
    
    @staticmethod
    def print_error(text: str):
        print(f"\n{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    @staticmethod
    def print_warning(text: str):
        print(f"\n{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")
    
    @staticmethod
    def print_info(text: str):
        print(f"\n{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")
    
    @staticmethod
    def print_success(text: str):
        print(f"\n{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

class ChatbotMemory:
    """Class quản lý bộ nhớ và lịch sử chat"""
    
    def __init__(self):
        self.current_session = []
        self.user_preferences = {}
        self.conversation_context = {}
        self.last_nganh_context = None  # Lưu ngành vừa hỏi gần nhất
        
    def add_turn(self, question: str, answer: str, metadata: dict = None):
        """Thêm lượt hội thoại vào session hiện tại"""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "metadata": metadata or {}
        }
        self.current_session.append(turn)
        
        # Giới hạn độ dài lịch sử
        if len(self.current_session) > MAX_HISTORY_LENGTH:
            self.current_session = self.current_session[-MAX_HISTORY_LENGTH:]
    
    def get_context_for_llm(self) -> List[Dict]:
        """Lấy context cho LLM từ lịch sử gần đây"""
        return self.current_session[-5:] if self.current_session else []
    
    def save_session(self):
        """Lưu session hiện tại vào file"""
        try:
            # Đọc sessions cũ
            sessions = []
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
            
            # Thêm session mới
            if self.current_session:
                sessions.append({
                    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "turns": self.current_session
                })
            
            # Chỉ giữ lại 10 sessions gần nhất
            sessions = sessions[-10:]
            
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            ColoredOutput.print_warning(f"Không thể lưu lịch sử chat: {e}")
    
    def reset_session(self):
        """Reset session hiện tại"""
        self.current_session = []
        self.conversation_context = {}
        self.last_nganh_context = None

class SmartMatcher:
    """Class xử lý matching thông minh"""

    @staticmethod
    def extract_code(text: str) -> Optional[str]:
        """Trích mã ngành dạng 6 hoặc 7 chữ số từ câu hỏi (ví dụ: 7480103)."""
        if not text:
            return None
        # match 6 hoặc 7 chữ số liên tiếp
        m = re.search(r'\b\d{6,7}\b', text)
        return m.group(0) if m else None
    
    @staticmethod
    def remove_accents(text: str) -> str:
        """Loại bỏ dấu tiếng Việt"""
        if not text:
            return ""
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()
    
    @staticmethod
    def extract_year(text: str) -> Optional[str]:
        """Trích xuất năm từ text"""
        patterns = [
            r'năm\s*(20\d{2})',
            r'(20\d{2})',
            r'năm\s*(\d{2})',
        ]
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
        """Trích xuất khoảng năm (start_year, end_year) từ câu hỏi.
        Hỗ trợ các mẫu: "từ 2021 đến 2023", "2021-2023", "giai đoạn 2021 đến 2023".
        """
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
                # Bảo đảm start <= end
                if start > end:
                    start, end = end, start
                return start, end
        return None
    
    @staticmethod
    def extract_score_range(text: str) -> Tuple[Optional[float], Optional[float]]:
        """Trích xuất khoảng điểm từ text"""
        # Pattern: "từ X đến Y điểm", "trên X điểm", "dưới X điểm"
        patterns = [
            r'từ\s*([\d.]+)\s*đến\s*([\d.]+)',
            r'trên\s*([\d.]+)',
            r'dưới\s*([\d.]+)',
            r'dưới\s*điểm\s*([\d.]+)',  # Thêm pattern "dưới điểm X"
            r'>\s*([\d.]+)',
            r'<\s*([\d.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if "từ" in pattern:
                    return float(match.group(1)), float(match.group(2))
                elif "trên" in pattern or ">" in pattern:
                    return float(match.group(1)), None
                elif "dưới" in pattern or "<" in pattern:
                    return None, float(match.group(1))
        

        return None, None
    
    @staticmethod
    def extract_admission_method(text: str) -> Optional[str]:
        """Trích xuất phương thức xét tuyển từ text"""
        text_lower = text.lower()
        
        # Các từ khóa phương thức xét tuyển
        method_keywords = {
            "điểm thi thpt": ["điểm thi thpt", "điểm thi tốt nghiệp", "điểm thi đại học"],
            "học bạ": ["học bạ", "xét học bạ", "điểm học bạ"],
            "kết hợp": ["kết hợp", "tổ hợp", "điểm kết hợp"],
            "xét tuyển thẳng": ["xét tuyển thẳng", "tuyển thẳng", "ưu tiên xét tuyển"],
            "phỏng vấn": ["phỏng vấn", "vấn đáp", "interview"]
        }
        
        for method, keywords in method_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return method
        
        return None
    
    @staticmethod
    def filter_by_admission_method(diem_chuan_list: List[Dict], method: str) -> List[Dict]:
        """Lọc danh sách điểm chuẩn theo phương thức xét tuyển"""
        if not method:
            return diem_chuan_list
        
        filtered = []
        for dc in diem_chuan_list:
            phuong_thuc = dc.get('phuong_thuc', '').lower()
            if method == "điểm thi thpt":
                # Tìm các phương thức liên quan đến điểm thi THPT
                if any(kw in phuong_thuc for kw in ["điểm thi tốt nghiệp thpt", "xét điểm thi tốt nghiệp thpt"]):
                    filtered.append(dc)
            elif method == "học bạ":
                # Tìm các phương thức liên quan đến học bạ
                if any(kw in phuong_thuc for kw in ["học bạ thpt", "xét học bạ thpt"]):
                    filtered.append(dc)
            elif method == "kết hợp":
                # Tìm các phương thức kết hợp
                if any(kw in phuong_thuc for kw in ["kết hợp", "tổ hợp"]):
                    filtered.append(dc)
            elif method == "xét tuyển thẳng":
                # Tìm các phương thức xét tuyển thẳng
                if any(kw in phuong_thuc for kw in ["tuyển thẳng", "ưu tiên"]):
                    filtered.append(dc)
        
        return filtered

class ImprovedChatbot:
    """Class chính của chatbot được cải tiến"""
    
    def __init__(self):
        self.model = None
        self.nganhs = []
        self.vue_nganh_map = {}  # Map ma_nganh -> vue data
        self.embeddings = None
        self.index = None
        self.ids = []
        self.memory = ChatbotMemory()
        self.is_loading = False
        
    def load_data(self):
        """Load dữ liệu ngành học từ cả hai file"""
        if not os.path.exists(DATA_FILE):
            ColoredOutput.print_error(f"File dữ liệu {DATA_FILE} không tồn tại!")
            return False
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.nganhs = data.get('nganhs', [])
            ColoredOutput.print_success(f"Đã load {len(self.nganhs)} ngành học từ {DATA_FILE}")
        except Exception as e:
            ColoredOutput.print_error(f"Lỗi khi load dữ liệu: {e}")
            return False
        # Load thêm dữ liệu từ file vue
        if os.path.exists(VUE_DATA_FILE):
            try:
                with open(VUE_DATA_FILE, 'r', encoding='utf-8') as f:
                    vue_data = json.load(f)
                # Tạo map ma_nganh -> vue_data
                self.vue_nganh_map = {}
                for item in vue_data:
                    ma_nganh = item.get('maNganh') or item.get('ma_nganh')
                    if ma_nganh:
                        self.vue_nganh_map[ma_nganh] = item
                # Merge thông tin vào self.nganhs
                for ng in self.nganhs:
                    ma_nganh = ng.get('ma_nganh')
                    vue_info = self.vue_nganh_map.get(ma_nganh)
                    if vue_info:
                        # Merge các trường mô tả, vị trí việc làm, nơi làm việc, ...
                        for key in ['gioiThieu', 'viTriViecLam', 'noiLamViec', 'thoiGianDaoTao', 'bangCap', 'khoa', 'phuongThucXetTuyen']:
                            if key in vue_info:
                                ng[key] = vue_info[key]
                ColoredOutput.print_success(f"Đã merge dữ liệu mô tả ngành từ {VUE_DATA_FILE}")
            except Exception as e:
                ColoredOutput.print_warning(f"Không thể load hoặc merge dữ liệu từ {VUE_DATA_FILE}: {e}")
        else:
            ColoredOutput.print_warning(f"Không tìm thấy file {VUE_DATA_FILE}, chỉ dùng dữ liệu từ {DATA_FILE}")
        return True
    
    def load_model(self):
        """Load model embedding với loading animation"""
        def loading_animation():
            chars = "|/-\\"
            i = 0
            while self.is_loading:
                print(f"\r{Fore.YELLOW}Đang tải model... {chars[i % len(chars)]}{Style.RESET_ALL}", end='')
                time.sleep(0.1)
                i += 1
        
        try:
            self.is_loading = True
            # Bắt đầu animation trong thread riêng
            loading_thread = threading.Thread(target=loading_animation)
            loading_thread.start()
            
            self.model = SentenceTransformer(MODEL_NAME)
            
            self.is_loading = False
            loading_thread.join()
            print(f"\r{Fore.GREEN}✅ Model đã được tải thành công!{Style.RESET_ALL}")
            return True
        except Exception as e:
            self.is_loading = False
            ColoredOutput.print_error(f"Lỗi khi load model: {e}")
            return False
    
    def build_enhanced_embeddings(self):
        """Xây dựng embeddings với thông tin phong phú hơn"""
        texts = []
        ids = []
        
        for idx, ng in enumerate(self.nganhs):
            # Xây dựng text phong phú với nhiều thông tin
            components = []
            
            # Tên ngành
            if ng.get('nganh'):
                components.append(f"Tên ngành: {ng['nganh']}")
            
            # Mã ngành
            if ng.get('ma_nganh'):
                components.append(f"Mã ngành: {ng['ma_nganh']}")
            
            # Mô tả
            if ng.get('mo_ta'):
                components.append(f"Mô tả: {ng['mo_ta']}")
            
            # Khoa
            if ng.get('khoa'):
                components.append(f"Thuộc khoa: {ng['khoa']}")
            
            # Chỉ tiêu
            if ng.get('chi_tieu'):
                components.append(f"Chỉ tiêu tuyển sinh: {ng['chi_tieu']} sinh viên")
            
            # Thêm alias
            alias_list = []
            for alias, ma_nganh in ALIAS_MAP.items():
                if ng.get('ma_nganh') == ma_nganh:
                    alias_list.append(alias)
            
            if alias_list:
                components.append(f"Tên gọi khác: {', '.join(alias_list)}")
            
            # Thông tin điểm chuẩn gần nhất
            if ng.get('diem_chuan'):
                # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                sorted_diem_chuan = sorted(ng['diem_chuan'], key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                latest_score = sorted_diem_chuan[0]
                components.append(f"Điểm chuẩn gần nhất: {latest_score.get('diem', '')} năm {latest_score.get('nam', '')}")
            
            text = ". ".join(components)
            texts.append(text)
            ids.append(idx)
        
        # Tạo embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)
        
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Tạo FAISS index
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        return embeddings, index, ids
    
    def ensure_index(self):
        """Đảm bảo index tồn tại hoặc tạo mới"""
        if (os.path.exists(EMBEDDING_FILE) and 
            os.path.exists(INDEX_FILE) and 
            os.path.exists(ID_FILE)):
            try:
                self.embeddings = np.load(EMBEDDING_FILE)
                self.index = faiss.read_index(INDEX_FILE)
                with open(ID_FILE, 'r', encoding='utf-8') as f:
                    self.ids = json.load(f)
                ColoredOutput.print_info("Đã load index từ cache")
                return True
            except Exception as e:
                ColoredOutput.print_warning(f"Lỗi khi load cache, tạo mới: {e}")
        
        # Tạo mới
        ColoredOutput.print_info("Đang tạo embeddings và index...")
        self.embeddings, self.index, self.ids = self.build_enhanced_embeddings()
        
        # Lưu cache
        try:
            np.save(EMBEDDING_FILE, self.embeddings)
            faiss.write_index(self.index, INDEX_FILE)
            with open(ID_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ids, f)
            ColoredOutput.print_success("Đã lưu cache thành công")
        except Exception as e:
            ColoredOutput.print_warning(f"Không thể lưu cache: {e}")
        
        return True
    
    def smart_keyword_match(self, question: str) -> Optional[Dict]:
        """Matching thông minh với keywords"""
        q_lower = question.lower()
        q_no_accent = SmartMatcher.remove_accents(q_lower)
        
        # Tìm theo alias (ưu tiên cao nhất)
        for alias, ma_nganh in ALIAS_MAP.items():
            if alias in q_no_accent:
                for ng in self.nganhs:
                    if ng.get('ma_nganh') == ma_nganh:
                        return ng
        
        # Tìm theo mã ngành
        for ng in self.nganhs:
            if ng.get('ma_nganh') and ng.get('ma_nganh') in question:
                return ng
        
        # Tìm theo tên ngành (loại bỏ dấu)
        for ng in self.nganhs:
            if ng.get('nganh'):
                nganh_no_accent = SmartMatcher.remove_accents(ng['nganh'])
                if nganh_no_accent in q_no_accent:
                    return ng
        
        # Tìm theo từ khóa trong mô tả
        keywords_found = []
        for ng in self.nganhs:
            if ng.get('mo_ta'):
                mo_ta_no_accent = SmartMatcher.remove_accents(ng['mo_ta'])
                # Đếm số từ khóa trùng khớp
                count = sum(1 for word in q_no_accent.split() 
                           if len(word) > 3 and word in mo_ta_no_accent)
                if count > 0:
                    keywords_found.append((ng, count))
        
        # Trả về ngành có nhiều từ khóa trùng khớp nhất
        if keywords_found:
            keywords_found.sort(key=lambda x: x[1], reverse=True)
            return keywords_found[0][0]
        
        return None
    
    def semantic_search(self, question: str, top_k: int = TOP_K) -> List[Tuple[Dict, float]]:
        """Tìm kiếm semantic với FAISS"""
        q_emb = self.model.encode([question], normalize_embeddings=True)
        q_emb = np.array(q_emb).astype('float32')
        
        if q_emb.ndim == 1:
            q_emb = np.expand_dims(q_emb, 0)
        
        D, I = self.index.search(q_emb, top_k)
        
        results = []
        for i, score in zip(I[0], D[0]):
            if score >= MIN_SIMILARITY_SCORE:
                ng = self.nganhs[self.ids[i]]
                results.append((ng, float(score)))
        
        return results
    
    def filter_by_criteria(self, nganhs: List[Dict], question: str) -> List[Dict]:
        year = SmartMatcher.extract_year(question)
        min_score, max_score = SmartMatcher.extract_score_range(question)
        admission_method = SmartMatcher.extract_admission_method(question)
        
        filtered = []
        for ng in nganhs:
            if year and ng.get('diem_chuan'):
                has_year_data = any(str(dc.get('nam')) == year for dc in ng['diem_chuan'])
                if not has_year_data:
                    continue
            if (min_score is not None or max_score is not None) and ng.get('diem_chuan'):
                if year:
                    diem_chuan_nam = [dc for dc in ng['diem_chuan'] if str(dc.get('nam')) == year]
                else:
                    # Nếu không có year, lấy năm mới nhất có dữ liệu
                    sorted_diem_chuan = sorted(ng['diem_chuan'], key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                    latest_year = sorted_diem_chuan[0].get('nam')
                    diem_chuan_nam = [dc for dc in ng['diem_chuan'] if str(dc.get('nam')) == str(latest_year)]
                
                if not diem_chuan_nam:
                    continue
                
                # Lọc theo phương thức xét tuyển nếu có
                if admission_method:
                    diem_chuan_nam = SmartMatcher.filter_by_admission_method(diem_chuan_nam, admission_method)
                    if not diem_chuan_nam:
                        continue
                
                try:
                    score_val = min(float(dc.get('diem')) for dc in diem_chuan_nam if dc.get('diem'))
                except ValueError:
                    continue
                if min_score is not None and score_val < min_score:
                    continue
                if max_score is not None and score_val > max_score:
                    continue
            filtered.append(ng)
        return filtered
    
    def generate_smart_answer(self, question: str, ng: Dict, score: float = 1.0) -> str:
        """Tạo câu trả lời thông minh"""
        q_lower = question.lower()
        year = SmartMatcher.extract_year(question)
        year_range = SmartMatcher.extract_year_range(question)
        method = SmartMatcher.extract_admission_method(question)
        
        # Phân tích xu hướng điểm chuẩn
        if any(kw in q_lower for kw in ["phân tích", "đánh giá", "so sánh", "xu hướng", "biến động"]):
            if year_range:
                start_y, end_y = year_range
                return self._analyze_score_trend_range(ng, start_y, end_y)
            return self._analyze_score_trend(ng, year)
        
        # Thông tin điểm chuẩn
        if any(kw in q_lower for kw in ["điểm chuẩn", "điểm", "benchmark"]):
            return self._get_admission_scores(ng, year, method)
        
        # Thông tin điểm sàn
        if any(kw in q_lower for kw in ["điểm sàn", "tối thiểu", "minimum"]):
            return self._get_minimum_scores(ng, year)
        
        # Thông tin chỉ tiêu
        if any(kw in q_lower for kw in ["chỉ tiêu", "quota", "số lượng"]):
            return self._get_quota_info(ng)
        
        # Thông tin khoa
        if any(kw in q_lower for kw in ["khoa", "faculty", "department"]):
            return self._get_faculty_info(ng)
        
        # Mô tả ngành
        if any(kw in q_lower for kw in ["mô tả", "giới thiệu", "học gì", "ra trường làm gì"]):
            return self._get_program_description(ng)
        
        # So sánh với ngành khác
        # if any(kw in q_lower for kw in ["so sánh", "khác nhau", "compare"]):
        #     return self._compare_programs(ng, question)
        
        # Thông tin tổng hợp (mặc định)
        return self._get_comprehensive_info(ng)
    
    def _analyze_score_trend(self, ng: Dict, year: str = None) -> str:
        """Phân tích xu hướng điểm chuẩn.
        - Nếu year là chuỗi: chỉ phân tích năm đó
        - Nếu year là None: phân tích nhiều năm
        """
        if not ng.get('diem_chuan'):
            return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích xu hướng."
        # Nếu có year, chỉ phân tích năm đó
        if year:
            year_scores = {str(dc.get('nam')): float(dc.get('diem')) for dc in ng['diem_chuan'] if str(dc.get('nam')) == year and dc.get('diem')}
            if not year_scores:
                return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn năm {year}."
            result = f"📊 **Điểm chuẩn {ng.get('nganh')} năm {year}**\n\n"
            for y, score in year_scores.items():
                result += f"   • Năm {y}: {score:.2f} điểm\n"
            return result
        # Nếu không có year, phân tích xu hướng nhiều năm
        year_scores = {}
        # Sắp xếp theo năm để đảm bảo thứ tự chính xác
        sorted_diem_chuan = sorted(ng['diem_chuan'], key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0)
        for dc in sorted_diem_chuan:
            y = dc.get('nam')
            score = dc.get('diem')
            if y and score:
                try:
                    score_val = float(score)
                    if y not in year_scores or score_val > year_scores[y]:
                        year_scores[y] = score_val
                except ValueError:
                    continue
        if len(year_scores) < 2:
            return f"📊 {ng.get('nganh')}: Cần ít nhất 2 năm dữ liệu để phân tích xu hướng."
        years = sorted(year_scores.keys())
        scores = [year_scores[y] for y in years]
        # Tính xu hướng
        trends = []
        for i in range(1, len(scores)):
            diff = scores[i] - scores[i-1]
            if diff > 0.5:
                trends.append("tăng mạnh")
            elif diff > 0:
                trends.append("tăng nhẹ")
            elif diff < -0.5:
                trends.append("giảm mạnh")
            elif diff < 0:
                trends.append("giảm nhẹ")
            else:
                trends.append("ổn định")
        # Bảng điểm rõ ràng
        result = f"\n📈 **Phân tích xu hướng điểm chuẩn ngành {ng.get('nganh')}**\n"
        result += f"{'Năm':<8}{'Điểm chuẩn':<12}{'Ghi chú'}\n"
        result += "-"*32 + "\n"
        for idx, y in enumerate(years):
            note = ""
            if idx > 0:
                d = scores[idx] - scores[idx-1]
                if d > 0:
                    note = f"↑ +{d:.2f}"
                elif d < 0:
                    note = f"↓ {d:.2f}"
                else:
                    note = "="
            result += f"{y:<8}{scores[idx]:<12.2f}{note}\n"
        # Nhận xét tổng kết
        result += "\n✨ **Tóm tắt xu hướng:**\n"
        if all("tăng" in t for t in trends):
            result += "- Điểm chuẩn liên tục tăng qua các năm.\n"
        elif all("giảm" in t for t in trends):
            result += "- Điểm chuẩn liên tục giảm qua các năm.\n"
        elif all("ổn định" in t for t in trends):
            result += "- Điểm chuẩn khá ổn định qua các năm.\n"
        else:
            result += "- Điểm chuẩn có biến động qua các năm.\n"
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        result += f"- Trung bình: {avg_score:.2f} | Cao nhất: {max_score:.2f} | Thấp nhất: {min_score:.2f} | Biên độ: {max_score-min_score:.2f} điểm.\n"
        # Lời khuyên ngắn gọn
        if scores[-1] > scores[0]:
            result += "- 📢 Lời khuyên: Điểm chuẩn có xu hướng tăng, thí sinh nên chuẩn bị kỹ càng hơn cho các năm tới!"
        elif scores[-1] < scores[0]:
            result += "- 📢 Lời khuyên: Điểm chuẩn có xu hướng giảm, cơ hội trúng tuyển có thể cao hơn."
        else:
            result += "- 📢 Lời khuyên: Điểm chuẩn ổn định, hãy tập trung vào năng lực bản thân để đạt mục tiêu."
        return result

    def _analyze_score_trend_range(self, ng: Dict, start_year: str, end_year: str) -> str:
        """Phân tích xu hướng điểm chuẩn trong khoảng [start_year, end_year]."""
        if not ng.get('diem_chuan'):
            return f"📊 {ng.get('nganh')}: Không có dữ liệu điểm chuẩn để phân tích xu hướng."
        try:
            s_year = int(start_year)
            e_year = int(end_year)
        except Exception:
            return f"📊 Khoảng năm không hợp lệ."
        if s_year > e_year:
            s_year, e_year = e_year, s_year
        # Lọc điểm theo khoảng
        year_scores: Dict[int, float] = {}
        for dc in ng['diem_chuan']:
            y = dc.get('nam')
            score = dc.get('diem')
            if isinstance(y, int) and s_year <= y <= e_year and score is not None:
                try:
                    score_val = float(score)
                    # Lấy điểm cao nhất của mỗi năm nếu trùng năm với nhiều phương thức
                    if y not in year_scores or score_val > year_scores[y]:
                        year_scores[y] = score_val
                except ValueError:
                    continue
        if len(year_scores) < 1:
            return f"📊 {ng.get('nganh')}: Không có dữ liệu trong giai đoạn {s_year}-{e_year}."
        years = sorted(year_scores.keys())
        scores = [year_scores[y] for y in years]
        # Tạo bảng ngắn gọn
        result = f"📈 **Xu hướng điểm chuẩn {ng.get('nganh')} ({s_year}–{e_year})**\n"
        for idx, y in enumerate(years):
            note = ""
            if idx > 0:
                d = scores[idx] - scores[idx-1]
                if d > 0:
                    note = f" ↑ +{d:.2f}"
                elif d < 0:
                    note = f" ↓ {d:.2f}"
                else:
                    note = " ="
            result += f"- {y}: {scores[idx]:.2f}{note}\n"
        # Tóm tắt
        if len(scores) >= 2:
            delta = scores[-1] - scores[0]
            trend_text = "tăng" if delta > 0.25 else ("giảm" if delta < -0.25 else "ổn định")
            result += f"Tóm tắt: {trend_text} ({scores[0]:.2f} → {scores[-1]:.2f}, Δ {delta:.2f})."
        return result
    

    def _get_admission_scores(self, ng: Dict, year: str = None, method: Optional[str] = None) -> str:
        """Lấy điểm chuẩn theo năm/phương thức.
        Quy tắc:
        - Nếu có cả year và method: chỉ trả về đúng phương thức trong năm đó
        - Nếu chỉ có year: trả về tất cả phương thức của năm đó (tối đa 2-3 dòng ngắn gọn)
        - Nếu không có year: tự động lấy năm mới nhất có dữ liệu
        """
        if not ng.get('diem_chuan'):
            return f"📚 {ng.get('nganh')}: Chưa có dữ liệu điểm chuẩn."
        
        # Lọc theo năm nếu có
        scores = ng['diem_chuan']
        if year:
            scores = [s for s in scores if str(s.get('nam')) == year]
            if not scores:
                return f"📚 {ng.get('nganh')}: Không có điểm chuẩn năm {year}."
        else:
            # Nếu không có year, tự động lấy năm mới nhất có dữ liệu
            if scores:
                # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                scores = sorted(scores, key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                latest_year = scores[0].get('nam')
                # Lọc chỉ lấy dữ liệu của năm mới nhất
                scores = [s for s in scores if str(s.get('nam')) == str(latest_year)]
                year = str(latest_year)  # Cập nhật year để hiển thị
        
        # Lọc theo phương thức nếu có
        if method:
            filtered = SmartMatcher.filter_by_admission_method(scores, method)
            if filtered:
                # Ưu tiên 1 kết quả khớp
                s = filtered[0]
                return f"📚 **{ng.get('nganh')}** năm {year} ({s.get('phuong_thuc','')}): {s.get('diem','N/A')} điểm"
            else:
                return f"📚 {ng.get('nganh')}: Không có điểm chuẩn năm {year} cho phương thức {method}."
        
        # Không chỉ định phương thức → trả về ngắn gọn theo năm với 2 phương thức tiêu biểu
        result = f"📚 **{ng.get('nganh')} năm {year}:**\n"
        # Sắp xếp để ưu tiên THPT rồi học bạ
        order = ["điểm thi", "thpt", "tốt nghiệp", "học bạ"]
        def weight(item: Dict) -> int:
            pt = item.get('phuong_thuc','').lower()
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
    
    def _get_minimum_scores(self, ng: Dict, year: str = None) -> str:
        """Lấy thông tin điểm sàn"""
        if not ng.get('tieu_chi_xet_tuyen'):
            return f"📝 {ng.get('nganh')}: Không có thông tin điểm sàn."
        
        diem_san_data = []
        for tc in ng['tieu_chi_xet_tuyen']:
            if tc.get('diem_toi_thieu'):
                diem_san_data.append({
                    'nam': tc.get('nam'),
                    'diem_san': tc.get('diem_toi_thieu')
                })
        
        if not diem_san_data:
            return f"📝 {ng.get('nganh')}: Không có dữ liệu điểm sàn cụ thể."
        
        # Lọc theo năm
        if year:
            diem_san_data = [d for d in diem_san_data if str(d.get('nam')) == year]
            if not diem_san_data:
                return f"📝 {ng.get('nganh')}: Không có điểm sàn năm {year}."
        
        result = f"📝 **Điểm sàn {ng.get('nganh')}**\n\n"
        # Sắp xếp theo năm giảm dần để hiển thị năm mới nhất trước
        for d in sorted(diem_san_data, key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True):
            result += f"   • Năm {d.get('nam', 'N/A')}: {d.get('diem_san', 'N/A')} điểm\n"
        
        return result
    
    def extract_subject_combination(question: str) -> Optional[str]:
        # Ví dụ: tìm các tổ hợp phổ biến trong câu hỏi
        combinations = ['A00', 'A01', 'B00', 'C00', 'D01', 'D07', 'D90', 'A09']
        question_upper = question.upper()
        for comb in combinations:
            if comb in question_upper:
                return comb
        return None

    def suggest_major_by_score(self, score: float, year: Optional[str] = None, method: Optional[str] = None, subject_comb: Optional[str] = None) -> str:
        matching = []
        for ng in self.nganhs:
            if not ng.get('diem_chuan'):
                continue
            diem_list = ng['diem_chuan']
            if year:
                diem_list = [d for d in diem_list if str(d.get('nam')) == str(year)]
                if not diem_list:
                    continue
            else:
                # Nếu không có year, lấy năm mới nhất có dữ liệu
                if diem_list:
                    # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                    sorted_diem_list = sorted(diem_list, key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                    latest_year = sorted_diem_list[0].get('nam')
                    diem_list = [d for d in diem_list if str(d.get('nam')) == str(latest_year)]
            if method:
                diem_list = SmartMatcher.filter_by_admission_method(diem_list, method)
                if not diem_list:
                    continue
            # Lọc thêm theo tổ hợp môn nếu có
            if subject_comb:
                # Giả sử trong từng điểm chuẩn có trường 'to_hop'
                diem_list = [d for d in diem_list if subject_comb in d.get('to_hop', '')]
                if not diem_list:
                    continue
            try:
                min_diem = min(float(d.get('diem')) for d in diem_list if d.get('diem'))
                if min_diem <= score:
                    matching.append((ng.get('nganh'), min_diem))
            except:
                continue
        if not matching:
            return f"❌ Không tìm thấy ngành nào có điểm chuẩn ≤ {score}"
        matching.sort(key=lambda x: x[1])
        result = f"🎯 Ngành có điểm chuẩn ≤ {score}"
        if subject_comb:
            result += f" theo tổ hợp {subject_comb}"
        result += ":\n"
        for name, s in matching[:10]:
            result += f"• {name}: {s}\n"
        return result


    def _get_quota_info(self, ng: Dict) -> str:
        """Lấy thông tin chỉ tiêu - ngắn gọn, kèm năm nếu có"""
        chi_tieu = ng.get('chi_tieu')
        # Nếu chưa có, thử tìm trong mô tả
        if not chi_tieu and ng.get('mo_ta'):
            match = re.search(r'[Cc]hỉ tiêu:?\s*(\d+)', ng['mo_ta'])
            if match:
                chi_tieu = match.group(1)

        if chi_tieu:
            # Lấy năm gần nhất nếu có điểm chuẩn
            nam_gan_nhat = None
            if ng.get('diem_chuan'):
                # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                sorted_diem_chuan = sorted(ng['diem_chuan'], key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                nam_gan_nhat = sorted_diem_chuan[0].get('nam')

            if nam_gan_nhat:
                return f"🎯 **{ng.get('nganh')}**: {chi_tieu} sinh viên (năm {nam_gan_nhat})"
            else:
                return f"🎯 **{ng.get('nganh')}**: {chi_tieu} sinh viên"
        else:
            return f"🎯 **{ng.get('nganh')}**: Chưa có thông tin chỉ tiêu"


    
    def _get_faculty_info(self, ng: Dict) -> str:
        """Lấy thông tin khoa"""
        result = f"🏫 **Thông tin Khoa - {ng.get('nganh')}**\n\n"
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
            result += f" • Mô tả: {ng.get('mo_ta')[:200]}...\n"

        return result

    
    def _get_program_description(self, ng: Dict) -> str:
        """Lấy mô tả chi tiết ngành học, ưu tiên dữ liệu từ vue nếu có, nhưng trả lời ngắn gọn hơn"""
        result = f"📖 **Giới thiệu ngành {ng.get('nganh') or ng.get('tenNganh')}**\n\n"
        # Ưu tiên trường gioiThieu từ vue
        mo_ta = ng.get('gioiThieu') or ng.get('mo_ta')
        if mo_ta:
            # Rút gọn mô tả: lấy tối đa 350 ký tự, cắt ở dấu chấm gần nhất nếu có
            if len(mo_ta) > 350:
                cut_idx = mo_ta.rfind('.', 0, 350)
                if cut_idx != -1:
                    mo_ta = mo_ta[:cut_idx+1]
                else:
                    mo_ta = mo_ta[:350] + '...'
            result += f"🎓 {mo_ta}\n\n"
        # Thông tin cơ bản (ngắn gọn)
        result += f"📋 **Thông tin cơ bản:**\n"
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
    
    def _compare_programs(self, ng: Dict, question: str) -> str:
        """So sánh ngành với ngành khác (tính năng cơ bản)"""
        result = f"⚖️ **So sánh {ng.get('nganh')}**\n\n"
        result += "🤖 Để so sánh chi tiết, bạn hãy hỏi cụ thể về ngành muốn so sánh.\n\n"
        
        # Hiển thị thông tin ngành hiện tại để so sánh
        result += f"📊 **Thông tin {ng.get('nganh')}:**\n"
        if ng.get('diem_chuan'):
            latest = ng['diem_chuan'][-1]
            result += f"   • Điểm chuẩn: {latest.get('diem')} ({latest.get('nam')})\n"
        if ng.get('chi_tieu'):
            result += f"   • Chỉ tiêu: {ng.get('chi_tieu')} sinh viên\n"
        if ng.get('khoa'):
            result += f"   • Thuộc khoa: {ng.get('khoa')}\n"
        
        return result
    
    def _get_comprehensive_info(self, ng: Dict) -> str:
        """Lấy thông tin tổng hợp"""
        result = f"🎓 **Thông tin tổng hợp - {ng.get('nganh')}**\n\n"
        result += f"📋 **Thông tin cơ bản:**\n"
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
            # Sắp xếp theo năm giảm dần để lấy năm mới nhất
            sorted_diem_chuan = sorted(ng['diem_chuan'], key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
            latest = sorted_diem_chuan[0]
            result += f"\n🏆 **Tuyển sinh:**\n"
            result += f" • Điểm chuẩn gần nhất: {latest.get('diem', 'N/A')} điểm\n"
            result += f" • Năm: {latest.get('nam', 'N/A')}\n"
            result += f" • Phương thức: {latest.get('phuong_thuc', 'Chính quy')}\n"

        if ng.get('mo_ta'):
            description = ng.get('mo_ta')
            if len(description) > 150:
                description = description[:150] + "..."
            result += f"\n📝 **Mô tả:** {description}\n"

        return result

    
    def check_llm_connection(self) -> bool:
        """Kiểm tra kết nối LLM"""
        try:
            response = requests.get("http://localhost:11434/", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def generate_llm_response(self, question: str, top_nganhs: List[Dict]) -> str:
        """Tạo câu trả lời bằng LLM"""
        if not self.check_llm_connection():
            return "❌ Không thể kết nối đến Ollama server. Vui lòng chạy lệnh 'ollama serve' trước."
        
        # Chuẩn bị context
        context_parts = []
        for ng in top_nganhs:
            context_part = f"Ngành: {ng.get('nganh', '')}\n"
            context_part += f"Mã: {ng.get('ma_nganh', '')}\n"
            context_part += f"Khoa: {ng.get('khoa', '')}\n"
            if ng.get('mo_ta'):
                context_part += f"Mô tả: {ng.get('mo_ta', '')}\n"
            if ng.get('chi_tieu'):
                context_part += f"Chỉ tiêu: {ng.get('chi_tieu')} sinh viên\n"
            if ng.get('diem_chuan'):
                latest = ng['diem_chuan'][-1]
                context_part += f"Điểm chuẩn: {latest.get('diem', '')} ({latest.get('nam', '')})\n"
            context_parts.append(context_part)
        
        context = "\n---\n".join(context_parts)
        
        # Chuẩn bị messages
        messages = [
            {
                "role": "system",
                "content": f"""Bạn là tư vấn viên tuyển sinh đại học chuyên nghiệp và thân thiện. 
Hãy trả lời câu hỏi của thí sinh dựa trên thông tin ngành học dưới đây.

NGUYÊN TẮC TRẢ LỜI:
- Trả lời bằng tiếng Việt, ngắn gọn, chính xác
- Sử dụng emoji phù hợp để tạo sự thân thiện
- Nếu không có thông tin, hãy nói "Không có dữ liệu"
- Khuyến khích và hỗ trợ thí sinh
- Đưa ra lời khuyên thiết thực

THÔNG TIN CÁC NGÀNH:
{context}"""
            }
        ]
        
        # Thêm lịch sử hội thoại
        history = self.memory.get_context_for_llm()
        for turn in history[-3:]:  # Chỉ lấy 3 lượt gần nhất
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        
        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": question})
        
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "mistral",
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=LLM_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                return content if content else "🤖 Không có dữ liệu phù hợp để trả lời câu hỏi này."
            else:
                return f"❌ Lỗi LLM: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "⏰ Timeout: LLM phản hồi quá lâu, vui lòng thử lại."
        except Exception as e:
            return f"❌ Lỗi LLM: {e}"
    
    def is_question_vague(self, question: str) -> bool:
        """Kiểm tra câu hỏi có mơ hồ không"""
        keywords = [
            "ngành", "điểm", "mã ngành", "tên ngành", "khoa", "chỉ tiêu", 
            "năm", "mô tả", "tuyển sinh", "đại học", "cntt", "it", "khmt"
        ]
        
        q_lower = SmartMatcher.remove_accents(question.lower())
        
        # Câu hỏi quá ngắn
        if len(question.strip()) < 5:
            return True
        
        # Không chứa từ khóa liên quan
        if not any(keyword in q_lower for keyword in keywords):
            return True
        
        # Câu hỏi chỉ có 1-2 từ
        if len(question.split()) <= 2:
            return True
        
        return False
    
    def suggest_questions(self) -> List[str]:
        """Gợi ý câu hỏi mẫu"""
        suggestions = [
            "Điểm chuẩn CNTT 2023",
            "Chỉ tiêu ngành Khoa học máy tính",
            "So sánh điểm chuẩn CNTT và KTPM",
            "Phân tích xu hướng điểm ngành AI",
            "Ngành nào thuộc khoa CNTT?",
            "Mô tả ngành Mạng máy tính",
            "Điểm sàn các ngành IT 2023"
        ]
        return suggestions
    
    def print_welcome(self):
        """In lời chào và hướng dẫn"""
        ColoredOutput.print_header("🎓 CHATBOT TƯ VẤN TUYỂN SINH THÔNG MINH 🤖")
        print(f"{Fore.CYAN}Chào mừng bạn đến với hệ thống tư vấn tuyển sinh!")
        print(f"Tôi có thể giúp bạn tìm hiểu về các ngành học, điểm chuẩn, chỉ tiêu...{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}💡 TÍNH NĂNG NỔI BẬT:")
        features = [
            "🔍 Tìm kiếm thông minh (từ khóa + ngữ nghĩa)",
            "📊 Phân tích xu hướng điểm chuẩn qua các năm",
            "🤖 Trả lời tự nhiên bằng AI",
            "💾 Nhớ ngữ cảnh hội thoại",
            "🎯 Lọc theo năm, điểm số cụ thể",
            "⚡ Trả lời nhanh với cache thông minh"
        ]
        
        for feature in features:
            print(f"   {feature}")
        
        print(f"\n{Fore.GREEN}📝 CÁC LỆNH ĐẶC BIỆT:")
        commands = [
            "'help' - Xem hướng dẫn chi tiết",
            "'suggest' - Xem câu hỏi gợi ý", 
            "'reset' - Xóa lịch sử hội thoại",
            "'stats' - Xem thống kê hệ thống",
            "'exit' - Thoát chương trình"
        ]
        
        for cmd in commands:
            print(f"   • {cmd}")
        
        print(f"{Style.RESET_ALL}")
    
    def print_help(self):
        """In hướng dẫn chi tiết"""
        help_text = f"""
{Fore.CYAN}📚 HƯỚNG DẪN SỬ DỤNG CHI TIẾT{Style.RESET_ALL}

{Fore.YELLOW}🔍 CÁCH HỎI HIỆU QUẢ:{Style.RESET_ALL}
   • Sử dụng tên ngành, mã ngành hoặc từ viết tắt (VD: "CNTT", "7480201")
   • Chỉ định năm cụ thể (VD: "điểm chuẩn CNTT 2023")
   • Hỏi về khoảng điểm (VD: "ngành nào dưới 20 điểm")
   • Yêu cầu phân tích (VD: "phân tích xu hướng điểm AI")

{Fore.GREEN}📊 CÁC LOẠI THÔNG TIN CÓ THỂ HỎI:{Style.RESET_ALL}
   • Điểm chuẩn theo năm hoặc phương thức
   • Chỉ tiêu tuyển sinh
   • Thông tin khoa, mô tả ngành
   • Điểm sàn, điểm tối thiểu
   • So sánh giữa các ngành
   • Xu hướng biến động điểm qua các năm

{Fore.BLUE}🎯 VÍ DỤ CÂU HỎI HAY:{Style.RESET_ALL}
   • "Điểm chuẩn CNTT UIT 2023"
   • "Chỉ tiêu ngành Trí tuệ nhân tạo"
   • "So sánh CNTT và KTPM"
   • "Ngành nào có điểm dưới 18?"
   • "Phân tích xu hướng điểm KHMT"
   • "Mô tả ngành Mạng máy tính"

{Fore.MAGENTA}🤖 TÍNH NĂNG AI:{Style.RESET_ALL}
   • Chatbot nhớ ngữ cảnh cuộc trò chuyện
   • Trả lời tự nhiên, thân thiện
   • Phân tích và đưa ra lời khuyên
   • Tự động gợi ý câu hỏi liên quan
        """
        print(help_text)
    
    def print_stats(self):
        """In thống kê hệ thống"""
        stats = f"""
{Fore.CYAN}📈 THỐNG KÊ HỆ THỐNG{Style.RESET_ALL}

{Fore.GREEN}📚 Dữ liệu:{Style.RESET_ALL}
   • Tổng số ngành: {len(self.nganhs)}
   • Số ngành có điểm chuẩn: {len([ng for ng in self.nganhs if ng.get('diem_chuan')])}
   • Số ngành có mô tả: {len([ng for ng in self.nganhs if ng.get('mo_ta')])}

{Fore.BLUE}💾 Bộ nhớ:{Style.RESET_ALL}
   • Lượt hội thoại trong session: {len(self.memory.current_session)}
   • Cache embeddings: {'✅' if os.path.exists(EMBEDDING_FILE) else '❌'}
   • Cache FAISS index: {'✅' if os.path.exists(INDEX_FILE) else '❌'}

{Fore.YELLOW}🔧 Kỹ thuật:{Style.RESET_ALL}
   • Model embedding: {MODEL_NAME}
   • Số chiều vector: {self.embeddings.shape[1] if self.embeddings is not None else 'N/A'}
   • FAISS index type: IndexFlatIP
   • LLM connection: {'🟢 Connected' if self.check_llm_connection() else '🔴 Disconnected'}
        """
        print(stats)

    def extract_multiple_majors(self, question: str, top_k: int = 5) -> List[Dict]:
        found = []
        already_added_ma = set()
        q_noaccent = SmartMatcher.remove_accents(question.lower())
        # Ưu tiên alias xuất hiện trong câu hỏi, chỉ lấy tối đa 2 ngành
        for alias, ma_nganh in ALIAS_MAP.items():
            if alias in q_noaccent and ma_nganh not in already_added_ma:
                for ng in self.nganhs:
                    if ng.get("ma_nganh") == ma_nganh:
                        found.append(ng)
                        already_added_ma.add(ma_nganh)
                        if len(found) == 2:
                            return found
        # Nếu chưa đủ 2 ngành, bổ sung ngành gần đúng nhất qua semantic search (không trùng mã ngành)
        if len(found) < 2:
            search_results = self.semantic_search(question, top_k=top_k)
            for ng, score in search_results:
                ma_nganh = ng.get('ma_nganh')
                if ma_nganh and ma_nganh not in already_added_ma:
                    found.append(ng)
                    already_added_ma.add(ma_nganh)
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

    def process_question(self, question: str) -> str:
        self.last_question = question

        # --- XỬ LÝ ƯU TIÊN: mã ngành exact match ---
        code = SmartMatcher.extract_code(question)
        if code:
            for ng in self.nganhs:
                ma = str(ng.get('ma_nganh') or ng.get('maNganh') or "").strip()
                if ma == code:
                    self.memory.last_nganh_context = ng
                    ColoredOutput.print_info(f"Tìm thấy mã ngành: {code} -> {ng.get('nganh')}")
                    return self.generate_smart_answer(question, ng, 1.0)
            return f"❌ Không tìm thấy ngành có mã {code} trong dữ liệu."

        # --- Gợi ý ngành theo điểm ---
        m = re.search(r'được\s*(\d+(?:\.\d+)?)\s*điểm', question)
        if m:
            score = float(m.group(1))
            year = SmartMatcher.extract_year(question)
            method = SmartMatcher.extract_admission_method(question)
            return self.suggest_major_by_score(score, year, method)

        # 0. Xử lý câu hỏi về ngành có điểm chuẩn dưới X
        year = SmartMatcher.extract_year(question)
        min_score, max_score = SmartMatcher.extract_score_range(question)
        
        # Debug: in ra thông tin để kiểm tra
        ColoredOutput.print_info(f"Debug - Year: {year}, Min score: {min_score}, Max score: {max_score}")
        
        # 0.1. Xử lý câu hỏi về ngành thuộc khoa X
        q_lower = question.lower()
        
        # Xử lý câu hỏi "Ngành X thuộc khoa nào?"
        if "thuộc khoa nào" in q_lower or "khoa nào" in q_lower:
            # Tìm mã ngành trong câu hỏi
            code = SmartMatcher.extract_code(question)
            if code:
                for ng in self.nganhs:
                    ma = str(ng.get('ma_nganh') or ng.get('maNganh') or "").strip()
                    if ma == code:
                        nganh_name = ng.get('nganh', 'N/A')
                        khoa_info = ng.get('khoa')
                        if khoa_info:
                            if isinstance(khoa_info, dict):
                                khoa_name = khoa_info.get('tenKhoa', khoa_info)
                            else:
                                khoa_name = khoa_info
                            return f"🏫 **Ngành {nganh_name} ({code}) thuộc khoa: {khoa_name}**"
                        else:
                            return f"🏫 **Ngành {nganh_name} ({code})**: Chưa có thông tin về khoa"
                return f"❌ Không tìm thấy ngành có mã {code}"
        
        if any(kw in q_lower for kw in ["thuộc khoa", "ngành nào thuộc khoa", "khoa nào có ngành"]):
            # Tìm tên khoa trong câu hỏi
            khoa_keywords = ["công nghệ thông tin", "cntt", "y khoa", "y tế", "kinh tế", "luật", "sư phạm", "nông nghiệp"]
            target_khoa = None
            for keyword in khoa_keywords:
                if keyword in q_lower:
                    target_khoa = keyword
                    break
            
            if target_khoa:
                # Tìm tất cả ngành thuộc khoa đó
                matching_nganhs = []
                for ng in self.nganhs:
                    khoa_info = ng.get('khoa')
                    if khoa_info:
                        # Kiểm tra xem ngành có thuộc khoa target không
                        khoa_str = str(khoa_info).lower()
                        if isinstance(khoa_info, dict):
                            khoa_str = str(khoa_info.get('tenKhoa', '')).lower()
                        
                        if target_khoa in khoa_str or any(kw in khoa_str for kw in target_khoa.split()):
                            matching_nganhs.append(ng)
                
                if matching_nganhs:
                    result = f"🏫 **Ngành thuộc khoa {target_khoa.title()}:**\n\n"
                    # Liệt kê tất cả ngành thay vì giới hạn
                    for ng in matching_nganhs:
                        nganh_name = ng.get('nganh', 'N/A')
                        ma_nganh = ng.get('ma_nganh', 'N/A')
                        result += f"🎓 **{nganh_name}** ({ma_nganh})\n"
                    return result
                else:
                    return f"❌ Không tìm thấy ngành nào thuộc khoa {target_khoa.title()}"
        
        # 0.2. Xử lý câu hỏi về ngành có điểm chuẩn dưới X
        if max_score is not None:  # Có điều kiện "dưới X điểm"
            # Debug: in ra thông tin để kiểm tra
            ColoredOutput.print_info(f"Tìm ngành có điểm chuẩn dưới {max_score} điểm, năm: {year}")
            
            # Trích xuất phương thức xét tuyển từ câu hỏi
            admission_method = SmartMatcher.extract_admission_method(question)
            ColoredOutput.print_info(f"Phương thức xét tuyển: {admission_method}")
            
            matching_nganhs = []
            for ng in self.nganhs:
                if not ng.get('diem_chuan'):
                    continue
                # Lọc theo năm nếu có
                diem_chuan_nam = ng['diem_chuan']
                if year:
                    diem_chuan_nam = [dc for dc in diem_chuan_nam if str(dc.get('nam')) == year]
                else:
                    # Nếu không có year, lấy năm mới nhất có dữ liệu
                    if diem_chuan_nam:
                        # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                        sorted_diem_chuan = sorted(diem_chuan_nam, key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                        latest_year = sorted_diem_chuan[0].get('nam')
                        diem_chuan_nam = [dc for dc in diem_chuan_nam if str(dc.get('nam')) == str(latest_year)]
                
                if not diem_chuan_nam:
                    continue
                
                # Lọc theo phương thức xét tuyển nếu có
                if admission_method:
                    diem_chuan_nam = SmartMatcher.filter_by_admission_method(diem_chuan_nam, admission_method)
                    if not diem_chuan_nam:
                        continue
                
                # Kiểm tra xem có điểm nào dưới max_score không
                for dc in diem_chuan_nam:
                    try:
                        score_val = float(dc.get('diem', 0))
                        if score_val < max_score:
                            matching_nganhs.append({
                                'nganh': ng.get('nganh'),
                                'score': score_val,
                                'year': dc.get('nam'),
                                'method': dc.get('phuong_thuc', 'Không rõ')
                            })
                    except (ValueError, TypeError):
                        continue
            
            if matching_nganhs:
                # Sắp xếp theo điểm từ thấp đến cao
                matching_nganhs.sort(key=lambda x: x['score'])
                
                # Xác định năm để hiển thị
                display_year = year
                if not display_year and matching_nganhs:
                    # Lấy năm từ kết quả đầu tiên
                    display_year = matching_nganhs[0]['year']
                
                # Tạo tiêu đề với phương thức xét tuyển nếu có
                if admission_method:
                    result = f"📊 **Ngành có điểm chuẩn dưới {max_score} điểm năm {display_year} ({admission_method}):**\n\n"
                else:
                    result = f"📊 **Ngành có điểm chuẩn dưới {max_score} điểm năm {display_year}:**\n\n"
                
                # Liệt kê tất cả ngành thay vì giới hạn
                for ng in matching_nganhs:
                    method_display = f" ({ng['method']})" if ng['method'] and ng['method'] != 'Không rõ' else ""
                    result += f"🎓 **{ng['nganh']}**: {ng['score']:.2f} điểm{method_display}\n"
                
                return result
            else:
                # Xác định năm để hiển thị
                display_year = year if year else "mới nhất"
                method_text = f" theo phương thức {admission_method}" if admission_method else ""
                return f"❌ Không tìm thấy ngành nào có điểm chuẩn dưới {max_score} điểm năm {display_year}{method_text}"
        
        # 0.3. Xử lý câu hỏi về ngành có điểm chuẩn trên X
        if min_score is not None:  # Có điều kiện "trên X điểm"
            admission_method = SmartMatcher.extract_admission_method(question)         

            
            matching_nganhs = []
            for ng in self.nganhs:
                if not ng.get('diem_chuan'):
                    continue
                # Lọc theo năm nếu có
                diem_chuan_nam = ng['diem_chuan']
                if year:
                    diem_chuan_nam = [dc for dc in diem_chuan_nam if str(dc.get('nam')) == year]
                else:
                    # Nếu không có year, lấy năm mới nhất có dữ liệu
                    if diem_chuan_nam:
                        # Sắp xếp theo năm giảm dần để lấy năm mới nhất
                        sorted_diem_chuan = sorted(diem_chuan_nam, key=lambda x: int(x.get('nam', 0)) if x.get('nam') else 0, reverse=True)
                        latest_year = sorted_diem_chuan[0].get('nam')
                        diem_chuan_nam = [dc for dc in diem_chuan_nam if str(dc.get('nam')) == str(latest_year)]
                
                if not diem_chuan_nam:
                    continue
                
                # Lọc theo phương thức xét tuyển nếu có
                if admission_method:
                    diem_chuan_nam = SmartMatcher.filter_by_admission_method(diem_chuan_nam, admission_method)
                    if not diem_chuan_nam:
                        continue
                
                # Kiểm tra xem có điểm nào trên min_score không
                for dc in diem_chuan_nam:
                    try:
                        score_val = float(dc.get('diem', 0))
                        if score_val >= min_score:
                            matching_nganhs.append({
                                'nganh': ng.get('nganh'),
                                'score': score_val,
                                'year': dc.get('nam'),
                                'method': dc.get('phuong_thuc', 'Không rõ')
                            })
                    except (ValueError, TypeError):
                        continue
            
            if matching_nganhs:
                # Sắp xếp theo điểm từ cao đến thấp
                matching_nganhs.sort(key=lambda x: x['score'], reverse=True)
                
                # Xác định năm để hiển thị
                display_year = year
                if not display_year and matching_nganhs:
                    # Lấy năm từ kết quả đầu tiên
                    display_year = matching_nganhs[0]['year']
                
                result = f"📊 **Ngành có điểm chuẩn trên {min_score} điểm năm {display_year}"
                if admission_method:
                    result += f" ({admission_method})"
                result += ":**\n\n"
                
                # Liệt kê tất cả ngành thay vì giới hạn
                for ng in matching_nganhs:
                    method_display = f" ({ng['method']})" if ng['method'] and ng['method'] != 'Không rõ' else ""
                    result += f"🎓 **{ng['nganh']}**: {ng['score']:.2f} điểm{method_display}\n"
                
                return result
            else:
                # Xác định năm để hiển thị
                display_year = year if year else "mới nhất"
                method_text = f" theo phương thức {admission_method}" if admission_method else ""
                return f"❌ Không tìm thấy ngành nào có điểm chuẩn trên {min_score} điểm năm {display_year}{method_text}"
        
        # 1. Ưu tiên intent đặc biệt nếu có context ngành
        if self.is_reference_to_previous_major(question) and self.memory.last_nganh_context:
            ng = self.memory.last_nganh_context
            if self.is_career_question(question):
                vi_tri = ng.get('viTriViecLam')
                if vi_tri:
                    result = f"💼 **Vị trí việc làm tiêu biểu ngành {ng.get('nganh', ng.get('tenNganh'))}:**\n"
                    for vt in vi_tri:
                        result += f"   - {vt}\n"
                    return result
            if self.is_workplace_question(question):
                noi_lam_viec = ng.get('noiLamViec')
                if noi_lam_viec:
                    result = f"🏢 **Nơi làm việc phổ biến ngành {ng.get('nganh', ng.get('tenNganh'))}:**\n"
                    for nlv in noi_lam_viec:
                        result += f"   - {nlv}\n"
                    return result
            if self.is_quota_question(question):
                return self._get_quota_info(ng)
            return self.generate_smart_answer(question, ng, 1.0)
        # 2. Ưu tiên intent đặc biệt nếu keyword match ngành
        matched_nganh = self.smart_keyword_match(question)
        if matched_nganh:
            if self.is_career_question(question):
                vi_tri = matched_nganh.get('viTriViecLam')
                if vi_tri:
                    self.memory.last_nganh_context = matched_nganh
                    result = f"💼 **Vị trí việc làm tiêu biểu ngành {matched_nganh.get('nganh', matched_nganh.get('tenNganh'))}:**\n"
                    for vt in vi_tri:
                        result += f"   - {vt}\n"
                    return result
            if self.is_workplace_question(question):
                noi_lam_viec = matched_nganh.get('noiLamViec')
                if noi_lam_viec:
                    self.memory.last_nganh_context = matched_nganh
                    result = f"🏢 **Nơi làm việc phổ biến ngành {matched_nganh.get('nganh', matched_nganh.get('tenNganh'))}:**\n"
                    for nlv in noi_lam_viec:
                        result += f"   - {nlv}\n"
                    return result
            if self.is_quota_question(question):
                self.memory.last_nganh_context = matched_nganh
                return self._get_quota_info(matched_nganh)
            ColoredOutput.print_info(f"Tìm thấy ngành: {matched_nganh.get('nganh')} (keyword match)")
            self.memory.last_nganh_context = matched_nganh
            return self.generate_smart_answer(question, matched_nganh, 1.0)
        # 3. Semantic search
        results = self.semantic_search(question, TOP_K)
        # Ưu tiên context nếu câu hỏi là tham chiếu ngành trước đó
        if self.is_reference_to_previous_major(question) and self.memory.last_nganh_context:
            ColoredOutput.print_info("Nhận diện câu hỏi tham chiếu ngành trước đó.")
            return self.generate_smart_answer(question, self.memory.last_nganh_context, 1.0)
        # Nếu không tìm thấy ngành, hoặc score thấp, dùng context ngành trước đó
        if not results or (results and results[0][1] < 0.7 and self.memory.last_nganh_context):
            ColoredOutput.print_info("Score thấp hoặc không tìm thấy ngành, dùng context ngành trước đó.")
            return self.generate_smart_answer(question, self.memory.last_nganh_context, 1.0)
        # ⛳ Lọc kết quả theo điều kiện về năm, khoảng điểm...
        candidate_nganhs = [ng for ng, score in results]
        filtered_nganhs = self.filter_by_criteria(candidate_nganhs, question)
        if not filtered_nganhs:
            filtered_nganhs = candidate_nganhs
        # ✅ Nếu tìm ra ngành gần chính xác
        if len(results) >= 1 and results[0][1] > 0.8:
            best_nganh, score = results[0]
            if self.is_career_question(question):
                vi_tri = best_nganh.get('viTriViecLam')
                if vi_tri:
                    self.memory.last_nganh_context = best_nganh
                    result = f"💼 **Vị trí việc làm tiêu biểu ngành {best_nganh.get('nganh', best_nganh.get('tenNganh'))}:**\n"
                    for vt in vi_tri:
                        result += f"   - {vt}\n"
                    return result
            if self.is_workplace_question(question):
                noi_lam_viec = best_nganh.get('noiLamViec')
                if noi_lam_viec:
                    self.memory.last_nganh_context = best_nganh
                    result = f"🏢 **Nơi làm việc phổ biến ngành {best_nganh.get('nganh', best_nganh.get('tenNganh'))}:**\n"
                    for nlv in noi_lam_viec:
                        result += f"   - {nlv}\n"
                    return result
            if self.is_quota_question(question):
                self.memory.last_nganh_context = best_nganh
                return self._get_quota_info(best_nganh)
            ColoredOutput.print_info(f"Tìm thấy ngành: {best_nganh.get('nganh')} (score: {score:.2f})")
            self.memory.last_nganh_context = best_nganh
            return self.generate_smart_answer(question, best_nganh, score)
        # 🧠 Fallback: dùng LLM trả lời nếu vẫn chưa rõ
        ColoredOutput.print_info("Sử dụng AI để trả lời...")
        llm_response = self.generate_llm_response(question, filtered_nganhs[:3])
        if not llm_response or "⏰ Timeout" in llm_response or "❌" in llm_response:
            return (
                "🤖 Xin lỗi, tôi chưa thể trả lời rõ câu hỏi này. Bạn có thể hỏi cụ thể hơn tên ngành hoặc năm học, "
                "hoặc thử lại sau nếu máy chủ AI bị gián đoạn."
            )
        if len(filtered_nganhs) == 1:
            self.memory.last_nganh_context = filtered_nganhs[0]
        return llm_response
    
    def run(self):
        """Chạy chatbot chính"""
        # Khởi tạo
        self.print_welcome()
        
        if not self.load_data():
            return
        
        if not self.load_model():
            return
        
        if not self.ensure_index():
            return
        
        ColoredOutput.print_success("Hệ thống đã sẵn sàng! Hãy đặt câu hỏi đầu tiên 🚀")
        
        # Vòng lặp chính
        while True:
            try:
                # Nhận input
                question = input(f"\n{Fore.CYAN}❓ Câu hỏi: {Style.RESET_ALL}").strip()
                
                if not question:
                    ColoredOutput.print_warning("Vui lòng nhập câu hỏi!")
                    continue
                
                q_lower = question.lower()
                
                # Xử lý lệnh đặc biệt
                if q_lower == 'exit':
                    ColoredOutput.print_info("Đang lưu lịch sử...")
                    self.memory.save_session()
                    ColoredOutput.print_success("Cám ơn bạn đã sử dụng! Tạm biệt! 👋")
                    break
                
                elif q_lower == 'reset':
                    self.memory.reset_session()
                    ColoredOutput.print_success("Đã xóa lịch sử hội thoại!")
                    continue
                
                elif q_lower == 'help':
                    self.print_help()
                    continue
                
                elif q_lower == 'stats':
                    self.print_stats()
                    continue
                
                elif q_lower == 'suggest':
                    suggestions = self.suggest_questions()
                    ColoredOutput.print_info("💡 Câu hỏi gợi ý:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion}")
                    continue
                
                # Xử lý câu hỏi thường
                start_time = time.time()
                answer = self.process_question(question)
                response_time = time.time() - start_time
                
                # Hiển thị câu trả lời
                ColoredOutput.print_bot_response(answer)
                
                # Hiển thị thời gian phản hồi (nếu > 1s)
                if response_time > 1:
                    print(f"{Fore.LIGHTBLACK_EX}⏱️  Thời gian phản hồi: {response_time:.2f}s{Style.RESET_ALL}")
                
                # Lưu vào memory
                self.memory.add_turn(question, answer, {"response_time": response_time})
                
            except KeyboardInterrupt:
                ColoredOutput.print_info("\n\nĐang thoát...")
                self.memory.save_session()
                ColoredOutput.print_success("Tạm biệt! 👋")
                break
                
            except Exception as e:
                ColoredOutput.print_error(f"Lỗi không mong muốn: {e}")
                ColoredOutput.print_info("Vui lòng thử lại với câu hỏi khác.")

def main():
    """Hàm main"""
    try:
        chatbot = ImprovedChatbot()
        chatbot.run()
    except Exception as e:
        ColoredOutput.print_error(f"Lỗi khởi tạo chatbot: {e}")
        print("Vui lòng kiểm tra:")
        print("1. File data_chatbot.json có tồn tại không")
        print("2. Các thư viện đã được cài đặt chưa")
        print("3. Model embedding có thể tải được không")

if __name__ == "__main__":
    main()


