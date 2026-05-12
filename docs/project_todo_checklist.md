# Project Todo Checklist

Tai lieu nay dung de theo doi cac viec can lam de hoan thanh do an.

Quy uoc:

- `[x]` Da xong
- `[~]` Dang lam / da lam mot phan
- `[ ]` Chua lam

## 0. Scope da chot

- `[x]` Chot kien truc: `Desktop app` chi danh cho `DRIVER`
- `[x]` Chot kien truc: `SUPER_ADMIN` va `COMPANY_ADMIN` thuoc `web admin`
- `[x]` Chot repo hien tai uu tien hoan thien `desktop monitoring app`
- `[ ]` Neu can, tai lieu hoa scope `web admin` thanh module he thong rieng

## 1. Nen tang du an

- `[x]` Doc de cuong va chot huong trien khai
- `[x]` Chot kien truc tong the cua du an
- `[x]` Chon cau truc repo `single repo + modular monolith + hybrid feature-based`
- `[x]` Tao tai lieu kien truc o `docs/project_architecture.md`
- `[x]` Tao schema Supabase o `db/supabase_schema.sql`
- `[x]` Tao `README.md`, `.env.example`, `requirements.txt`
- `[x]` Tach `requirements-train.txt` cho moi truong AI rieng

## 2. Khung desktop app

- `[x]` Tao entrypoint `app/main.py`
- `[x]` Tao khung UI `login`
- `[x]` Tao khung UI `register`
- `[x]` Tao khung UI `dashboard`
- `[x]` Tao khung UI `history`
- `[x]` Tao khung UI `statistics`
- `[x]` Tao khung UI `settings`
- `[x]` Tao local fallback mode khi chua co Supabase
- `[x]` Chinh code tuong thich Python 3.9

## 3. Monitoring realtime

- `[x]` Ket noi webcam vao dashboard
- `[x]` Start/Stop monitoring session
- `[x]` Tich hop MediaPipe Face Mesh vao pipeline
- `[x]` Tinh EAR
- `[x]` Tinh MAR
- `[x]` Rule-based detection bang EAR/MAR
- `[x]` Hien thi `status`, `risk`, `EAR`, `MAR` realtime
- `[x]` Ve landmark len preview
- `[x]` Ve contour mat/mieng len preview
- `[x]` Ve overlay thong so len preview
- `[x]` Phat am thanh canh bao
- `[x]` Chong spam alert theo frame
- `[~]` On dinh MediaPipe runtime tren may demo
- `[ ]` Tinh chinh threshold theo webcam that

## 4. Luu lich su va thong ke

- `[x]` Luu alert local theo user
- `[x]` Luu alert local theo session
- `[x]` Hien thi man hinh history
- `[x]` Hien thi man hinh statistics
- `[x]` Tong hop theo ngay
- `[x]` Tong hop theo loai canh bao
- `[x]` Tong hop theo muc risk
- `[x]` Luu thong ke alert theo session khi stop monitoring
- `[ ]` Doc history tu Supabase that
- `[ ]` Doc statistics tu Supabase that
- `[ ]` Them loc theo ngay
- `[ ]` Them loc theo session

## 5. Supabase that

- `[ ]` Tao project Supabase
- `[ ]` Chay `db/supabase_schema.sql`
- `[ ]` Dien `SUPABASE_URL` vao `.env`
- `[ ]` Dien `SUPABASE_ANON_KEY` vao `.env`
- `[ ]` Test dang ky tai khoan that
- `[ ]` Test dang nhap tai khoan that
- `[ ]` Luu `user_settings` len Supabase
- `[ ]` Luu `monitoring_sessions` len Supabase
- `[ ]` Luu `alerts` len Supabase
- `[ ]` Dong bo history/statistics tu DB

## 5.1 Mo rong schema theo he thong nhieu role

- `[~]` Mo rong `profiles` thanh bang user nghiep vu day du hon
- `[ ]` Them `companies`
- `[ ]` Them `vehicles`
- `[ ]` Them lien ket `company_id` cho user phu hop
- `[ ]` Them lien ket gan xe cho `DRIVER`
- `[ ]` Them `company_id` va `vehicle_id` vao `monitoring_sessions`
- `[ ]` Them `company_id` va `vehicle_id` vao `alerts`
- `[ ]` Chot RLS theo 3 role: `SUPER_ADMIN`, `COMPANY_ADMIN`, `DRIVER`

## 6. AI model

- `[ ]` Chon dataset phu hop
- `[ ]` Thu thap / tai dataset
- `[ ]` Gan nhan du lieu
- `[ ]` Viet preprocess dataset day du
- `[ ]` Tach train/validation/test
- `[ ]` Train model CNN hoac MobileNetV2
- `[ ]` Danh gia accuracy, loss, confusion matrix
- `[ ]` Chon model tot nhat
- `[ ]` Export model `.keras`

## 7. Tich hop AI vao app

- `[ ]` Load model trong runtime app
- `[ ]` Tien xu ly frame cho model
- `[ ]` Predict theo chu ky frame
- `[ ]` Hien thi nhan AI va confidence
- `[ ]` Ket hop AI voi EAR/MAR
- `[ ]` Ra quyet dinh canh bao cuoi cung bang rule + AI

## 8. Hoan thien trai nghiem nguoi dung

- `[ ]` Hien thi ro `Local mode` / `Supabase mode`
- `[ ]` Hien thi loi camera ro rang hon
- `[ ]` Hien thi loi model ro rang hon
- `[x]` Co `camera_index` trong settings
- `[x]` Co bat/tat am thanh canh bao trong settings
- `[ ]` Cho chon model AI trong settings theo file that

## 9. Kiem thu tong the

- `[ ]` Test login/register end-to-end
- `[ ]` Test monitoring start/stop end-to-end
- `[ ]` Test nham mat lau
- `[ ]` Test ngap
- `[ ]` Test khong co mat trong khung
- `[ ]` Test luu history
- `[ ]` Test statistics
- `[ ]` Test settings
- `[ ]` Test voi Supabase that
- `[ ]` Test voi model AI that

## 10. Dong goi va demo

- `[ ]` Cau hinh PyInstaller
- `[ ]` Build file `.exe`
- `[ ]` Test `.exe` tren may demo
- `[ ]` Kiem tra webcam, am thanh, assets trong ban dong goi
- `[ ]` Chuan bi kich ban demo 3-5 phut

## 11. Bao cao va slide

- `[ ]` Viet mo ta kien truc he thong
- `[ ]` Viet phan thiet ke co so du lieu
- `[ ]` Viet phan quy trinh huan luyen model
- `[ ]` Chup anh man hinh cac chuc nang chinh
- `[ ]` Lam slide thuyet trinh
- `[ ]` Chuan bi cau hoi va tra loi

## 12. Uu tien tiep theo

Thu tu uu tien de lam tiep:

1. `[ ]` On dinh moi truong runtime va chay webcam + MediaPipe that tren may ban
2. `[ ]` Tinh chinh threshold EAR/MAR
3. `[ ]` Noi Supabase that
4. `[ ]` Hoan thien history/statistics tu Supabase
5. `[ ]` Chot schema he thong nhieu role theo scope moi
6. `[ ]` Train model AI
7. `[ ]` Tich hop AI vao runtime
8. `[ ]` Dong goi `.exe`
9. `[ ]` Hoan thien bao cao va slide
