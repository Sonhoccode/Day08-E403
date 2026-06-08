"""Task 1: collect legal documents for the local RAG exercise."""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_DOCS = {
    "luat-phong-chong-ma-tuy-2021.pdf": """
Luat Phong, chong ma tuy 2021 - Luat so 73/2021/QH15.
Van ban quy dinh ve phong ngua, dau tranh chong toi pham ma tuy, quan ly
nguoi su dung trai phep chat ma tuy, cai nghien ma tuy, quan ly sau cai
nghien va trach nhiem cua co quan, to chuc, ca nhan.

Dieu 3 giai thich cac khai niem nhu chat ma tuy, tien chat, thuoc gay
nghien, nguoi su dung trai phep chat ma tuy va cai nghien ma tuy. Luat
nhan manh nguyen tac phong ngua tu som, ket hop giao duc, y te, xa hoi va
xu ly nghiem hanh vi vi pham.

Hinh thuc cai nghien gom cai nghien tu nguyen tai gia dinh, cong dong, co
so cai nghien va cai nghien bat buoc theo quyet dinh cua co quan co tham
quyen. Viec quan ly sau cai nghien huong toi ho tro tai hoa nhap cong dong.
""",
    "nghi-dinh-105-2021.pdf": """
Nghi dinh 105/2021/ND-CP quy dinh chi tiet va huong dan thi hanh mot so
dieu cua Luat Phong, chong ma tuy. Nghi dinh huong dan quy trinh xac dinh
tinh trang nghien ma tuy, ho so quan ly, phoi hop giua cong an, y te va
lao dong - thuong binh va xa hoi.

Co so y te co trach nhiem danh gia tinh trang nghien. Cong an cap xa lap
ho so, xac minh thong tin va thong bao ket qua cho ca nhan, gia dinh, co
quan lien quan.

Doi voi cai nghien tu nguyen, nguoi nghien hoac gia dinh co the dang ky
dich vu ho tro. Doi voi cai nghien bat buoc, ho so phai the hien can cu
phap ly, ket qua xac dinh tinh trang nghien va tai lieu chung minh dieu
kien ap dung bien phap.
""",
    "bo-luat-hinh-su-2015-chuong-ma-tuy.pdf": """
Bo luat Hinh su 2015, sua doi bo sung 2017 - Chuong XX ve cac toi pham ma
tuy. Cac dieu 247 den 259 quy dinh hanh vi pham toi nhu trong cay chua
chat ma tuy, san xuat, tang tru, van chuyen, mua ban trai phep chat ma tuy,
chiem doat chat ma tuy va to chuc su dung trai phep chat ma tuy.

Dieu 249 quy dinh toi tang tru trai phep chat ma tuy. Muc hinh phat phu
thuoc vao loai chat ma tuy, khoi luong, nhan than nguoi pham toi va tinh
tiet tang nang. Hinh phat co the la tu co thoi han va trong truong hop dac
biet nghiem trong co the o muc rat cao theo luat.

Dieu 251 quy dinh toi mua ban trai phep chat ma tuy. Hanh vi mua ban, trao
doi, moi gioi hoac to chuc giao dich chat ma tuy trai phep bi xu ly nghiem
khac hon hanh vi su dung don le.
""",
}


def setup_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_legal_docs() -> None:
    """Create source files large enough for the automated checks."""
    setup_directory()
    for filename, body in LEGAL_DOCS.items():
        path = DATA_DIR / filename
        path.write_text((body.strip() + "\n\n") * 4, encoding="utf-8")
        print(f"Created: {path}")


if __name__ == "__main__":
    create_sample_legal_docs()
