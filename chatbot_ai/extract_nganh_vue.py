import os
import re
import json

def js_object_to_json(js_object):
    # Loại bỏ comment JS
    js_object = re.sub(r'//.*', '', js_object)
    js_object = re.sub(r'/\*.*?\*/', '', js_object, flags=re.DOTALL)
    # Thêm dấu ngoặc kép cho key (cả key lồng trong object con)
    js_object = re.sub(r'([,{]\s*)(\w+)\s*:', r'\1"\2":', js_object)
    # Đổi dấu nháy đơn thành nháy kép
    js_object = js_object.replace("'", '"')
    # Xử lý dấu phẩy thừa cuối cùng trong object hoặc array (lặp nhiều lần cho chắc)
    for _ in range(5):
        js_object = re.sub(r',\s*([}}\]])', r'\1', js_object)
    return js_object

def extract_nganh_info_from_vue(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tìm đoạn nganhInfo: { ... }
    match = re.search(r'nganhInfo\s*:\s*({.*?})\s*,\s*loading:', content, re.DOTALL)
    if not match:
        return None

    js_object = match.group(1)
    json_str = js_object_to_json(js_object)

    try:
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Lỗi parse JSON ở file {file_path}: {e}")
        return None

def main():
    nganh_dir = os.path.join(os.path.dirname(__file__), '..', 'vuejsversion1', 'src', 'views', 'public', 'nganh')
    nganh_dir = os.path.abspath(nganh_dir)
    all_data = []

    for fname in os.listdir(nganh_dir):
        if fname.endswith('.vue'):
            fpath = os.path.join(nganh_dir, fname)
            nganh_data = extract_nganh_info_from_vue(fpath)
            if nganh_data:
                nganh_data['file'] = fname  # Ghi lại tên file để tra cứu
                all_data.append(nganh_data)

    # Lưu ra file JSON cho chatbot
    out_path = os.path.join(os.path.dirname(__file__), 'data_nganh_vue.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Đã xuất {len(all_data)} ngành ra file {out_path}")

if __name__ == "__main__":
    main()