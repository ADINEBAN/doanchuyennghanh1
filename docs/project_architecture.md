# Kien truc du an Desktop App Canh Bao Buon Ngu

## 1. Muc tieu buoc 1

Buoc nay chot 3 phan nen tang de nhom co the bat tay vao code ngay:

- Cau truc thu muc du an.
- Kien truc module va luong du lieu.
- Thiet ke co so du lieu Supabase PostgreSQL.

Huong thiet ke uu tien:

- De demo duoc som.
- Tach ro UI, xu ly webcam, detector, AI model va database.
- Co the phat trien theo MVP truoc, mo rong sau.

## 1.1 Kien truc da chot

Kien truc nghiep vu da duoc chot nhu sau:

- `Desktop app` chi danh cho `DRIVER`
- `SUPER_ADMIN` va `COMPANY_ADMIN` thuoc `web admin`
- Repo hien tai tap trung vao `desktop monitoring app`
- Phan `web admin` duoc xem la module/ung dung quan tri tach rieng

Dieu nay co nghia:

- App desktop khong co muc tieu lam day du giao dien quan tri he thong
- Trong repo nay, uu tien cao nhat van la:
  - dang nhap tai xe
  - mo webcam
  - giam sat realtime
  - luu session va alerts
  - history va statistics cho tai xe

Phan mo rong he thong tong the:

- `SUPER_ADMIN`: quan ly hang xe, tai khoan quan ly, model AI, nguong mac dinh
- `COMPANY_ADMIN`: quan ly xe, tai xe, gan xe, xem lich su va thong ke theo hang

se duoc thiet ke theo huong `web admin`, khong nhung vao desktop runtime cua DRIVER.

## 2. Stack de xuat

- Ngon ngu: Python 3.11+
- Desktop UI: PyQt6
- Xu ly webcam va anh: OpenCV
- Landmark khuon mat: MediaPipe Face Mesh
- AI model: TensorFlow / Keras
- Database online: Supabase PostgreSQL
- Bieu do: Matplotlib
- Dong goi: PyInstaller

## 3. Cau truc thu muc de xuat

Repo nay nen theo kieu:

- Single repo
- Modular monolith
- Hybrid feature-based structure
- Tach `runtime app` khoi `training workspace`
- Desktop runtime cho `DRIVER`
- Web admin la module he thong tach rieng trong pham vi tong the

```text
drowsiness_desktop_app/
|-- app/
|   |-- main.py
|   |-- features/
|   |   |-- auth/
|   |   |   |-- service.py
|   |   |   `-- ui.py
|   |   |-- monitoring/
|   |   |   |-- alert_service.py
|   |   |   |-- engine.py
|   |   |   |-- frame.py
|   |   |   |-- landmark.py
|   |   |   |-- metrics.py
|   |   |   |-- session_service.py
|   |   |   |-- ui.py
|   |   |   `-- webcam.py
|   |   |-- history/
|   |   |   `-- ui.py
|   |   |-- statistics/
|   |   |   `-- ui.py
|   |   `-- settings/
|   |       |-- service.py
|   |       `-- ui.py
|   |-- shared/
|   |   |-- config/
|   |   |   |-- settings.py
|   |   |   `-- constants.py
|   |   |-- core/
|   |   |   |-- app_state.py
|   |   |   |-- signals.py
|   |   |   `-- exceptions.py
|   |   |-- database/
|   |   |   `-- supabase_service.py
|   |   |-- widgets/
|   |   |   |-- camera_view.py
|   |   |   |-- alert_banner.py
|   |   |   `-- stats_chart.py
|   |   |-- styles/
|   |   |   `-- theme.qss
|   |   `-- utils/
|   |       |-- logger.py
|   |       |-- datetime_helper.py
|   |       `-- audio_player.py
|   `-- ai/
|       |-- predictor.py
|       |-- labels.py
|       `-- model_loader.py
|-- assets/
|   |-- sounds/
|   |   `-- alert.wav
|   |-- icons/
|   `-- images/
|-- db/
|   `-- supabase_schema.sql
|-- docs/
|   `-- project_architecture.md
|-- ml/
|   |-- datasets/
|   |-- notebooks/
|   |-- training/
|   |   |-- train_model.py
|   |   |-- evaluate_model.py
|   |   `-- preprocess_dataset.py
|   `-- exported_models/
|       `-- drowsiness_model.keras
|-- tests/
|   |-- test_ear_mar.py
|   |-- test_alert_rules.py
|   `-- test_services.py
|-- .env.example
|-- requirements.txt
`-- README.md
```

## 4. Trach nhiem tung module

### 4.1 `app/main.py`

Diem vao chinh cua ung dung:

- Khoi tao QApplication.
- Nap cau hinh.
- Khoi tao session dang nhap.
- Dieu huong tu man hinh login sang dashboard.

### 4.2 `app/shared/config`

Quan ly:

- URL, key Supabase.
- Nguong EAR, MAR.
- So frame lien tiep de kich hoat canh bao.
- Duong dan model AI.

Tat ca gia tri nen doc tu `.env` va co gia tri mac dinh an toan.

### 4.3 `app/shared/core`

Dung de chua:

- `app_state.py`: user hien tai, session hien tai, model dang duoc chon.
- `signals.py`: event tu webcam sang UI, tu detector sang alert.
- `exceptions.py`: loi xac thuc, loi camera, loi database.

### 4.4 `app/features`

Code duoc gom theo tinh nang de de tim, de sua va de chia viec:

- `auth/`: login, register, auth service.
- `monitoring/`: dashboard, webcam, frame processing, landmark, EAR/MAR, session va alert.
- `history/`: man hinh lich su.
- `statistics/`: man hinh thong ke.
- `settings/`: UI va service cho cai dat nguoi dung.

Pham vi cua cac feature nay la cho `DRIVER desktop app`, khong bao gom giao dien quan tri hang xe.

### 4.5 `app/shared`

Day la tang dung chung cho nhieu feature:

- `config/`: doc `.env`, constants.
- `core/`: state, exception, signal.
- `database/`: ket noi Supabase.
- `widgets/`: widget tai su dung.
- `styles/`: theme chung.
- `utils/`: logger, datetime, audio.

Quy tac:

- Feature nao dung chung thi moi dua vao `shared/`.
- UI khong goi Supabase truc tiep.
- Moi thao tac voi DB phai di qua service cua feature hoac `shared/database`.

### 4.6 `app/features/monitoring`

Day la phan quan trong nhat cho demo:

- `webcam.py`: mo webcam, doc frame, giai phong tai nguyen.
- `frame.py`: resize, convert BGR sang RGB, crop.
- `landmark.py`: goi MediaPipe de lay landmark mat va mieng.
- `metrics.py`: tinh EAR, MAR.
- `engine.py`: hop nhat EAR, MAR va output cua model AI de dua ra trang thai cuoi.

`engine.py` nen tra ve:

- `status`: `normal`, `tired`, `drowsy`, `closed_eyes`, `yawning`
- `risk_level`: `low`, `medium`, `high`
- `metrics`: EAR, MAR, xac suat AI, so frame vi pham
- `should_alert`: true/false
- `alert_type`: loai canh bao neu co

### 4.7 `app/ai`

Tang du doan model:

- `model_loader.py`: nap model tu file `.keras` hoac `.onnx`.
- `predictor.py`: nhan input anh va tra ve class.
- `labels.py`: map index sang nhan.

Khuyen nghi:

- Bat dau voi 2-3 lop de dat do chinh xac on dinh.
- Neu dataset yeu, dung AI lam tham khao, uu tien EAR/MAR cho luat canh bao.

### 4.8 `ml/training`

Day la workspace rieng cho huan luyen:

- `preprocess_dataset.py`: doi ten, resize, tach train/val/test.
- `train_model.py`: train model.
- `evaluate_model.py`: confusion matrix, accuracy, classification report.

Khong de logic train trong `app/`.

## 5. Luong xu ly tong the

### 5.1 Luong dang nhap

1. User mo app.
2. Nhap email va mat khau.
3. `auth_service` gui yeu cau len Supabase Auth.
4. Neu hop le, app lay `profile` va `settings`.
5. Chuyen sang `dashboard_window`.

Trong phien ban hien tai, user chinh cua desktop app la `DRIVER`.

### 5.2 Luong giam sat realtime

1. User bam `Start Monitoring`.
2. `session_service` tao ban ghi `monitoring_session`.
3. `webcam_manager` mo camera va doc frame lien tuc.
4. `frame_preprocessor` xu ly frame co ban.
5. `face_landmark_detector` tim landmark khuon mat.
6. `ear_mar_calculator` tinh EAR va MAR.
7. `predictor` du doan trang thai bang AI theo chu ky, vi du moi 5 frame.
8. `drowsiness_engine` hop nhat thong tin va ra quyet dinh.
9. Neu vuot nguong:
   - Phat am thanh.
   - Hien banner canh bao.
   - `alert_service` luu alert vao DB.
10. Khi dung giam sat:
   - `session_service` dong phien.
   - Luu tong thoi gian, tong so canh bao.

### 5.3 Luong lich su va thong ke

1. User mo man hinh lich su.
2. `alert_service` lay du lieu theo user, theo ngay, theo session.
3. UI hien thi bang du lieu.
4. Man hinh thong ke goi query tong hop theo ngay/tuan va ve bieu do.

## 6. Dinh nghia trang thai nghiep vu

Nen chot nho, ro va de demo:

- `normal`: khong co dau hieu bat thuong.
- `tired`: co dau hieu met moi nhe, nhung chua canh bao manh.
- `closed_eyes`: EAR duoi nguong trong nhieu frame lien tiep.
- `yawning`: MAR vuot nguong trong mot khoang thoi gian.
- `drowsy`: ket hop nhieu dau hieu nguy hiem, canh bao muc cao.

Loai alert de luu DB:

- `closed_eyes`
- `yawning`
- `drowsy`
- `distraction`

## 7. Nguong canh bao de xuat cho MVP

Chi la gia tri khoi dau, se tinh chinh sau khi test:

- `EAR_THRESHOLD = 0.23`
- `EAR_CONSEC_FRAMES = 20`
- `MAR_THRESHOLD = 0.65`
- `YAWN_CONSEC_FRAMES = 15`
- `AI_PREDICTION_INTERVAL = 5`
- `DROWSY_ALERT_SECONDS = 2`

Nen luu cac gia tri nay trong `user_settings` de co the thay doi tu UI.

## 8. Bien moi truong can co

File `.env.example` nen co:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
APP_ENV=development
DEFAULT_CAMERA_INDEX=0
MODEL_PATH=ml/exported_models/drowsiness_model.keras
EAR_THRESHOLD=0.23
EAR_CONSEC_FRAMES=20
MAR_THRESHOLD=0.65
YAWN_CONSEC_FRAMES=15
ALERT_SOUND_PATH=assets/sounds/alert.wav
```

## 9. Phan cong goi y cho 2 nguoi

### Nguoi 1

- Dung khung PyQt6.
- Lam login, register, dashboard, history, statistics.
- Hien webcam frame len giao dien.
- Ve bieu do thong ke.
- Dong goi bang PyInstaller.

### Nguoi 2

- Tao Supabase schema.
- Viet `auth_service`, `session_service`, `alert_service`.
- Lam MediaPipe landmark, EAR/MAR.
- Train model AI va viet `predictor`.
- Tich hop logic canh bao.

### Lam chung

- Noi UI voi services.
- Kiem thu demo end-to-end.
- Chup hinh, viet bao cao, lam slide.

## 10. Thu tu trien khai de tranh vo tran

### Giai doan 1: Khung app

- Tao cau truc thu muc.
- Tao login/register.
- Ket noi Supabase auth.

### Giai doan 2: Webcam + CV

- Mo webcam, hien thi frame.
- Lay landmark.
- Tinh EAR/MAR.
- Hien thi trang thai realtime len UI.

### Giai doan 3: Canh bao + luu lich su

- Bat/tat monitoring session.
- Phat am thanh.
- Luu alert vao DB.
- Xem lich su theo user.

### Giai doan 4: AI model

- Chuan bi dataset.
- Train model.
- Tich hop predictor.
- Hop nhat AI voi rule-based EAR/MAR.

### Giai doan 5: Thong ke + dong goi

- Tong hop so lieu.
- Ve chart.
- Tao file `.exe`.

## 11. Nguyen tac thiet ke can giu

- UI khong chua xu ly nghiep vu phuc tap.
- Detector khong ghi DB truc tiep.
- Khong de logic train model tron vao app runtime.
- Realtime loop phai nhe, tranh goi DB o moi frame.
- Chi luu alert khi thuc su xay ra su kien, khong luu moi frame.

## 12. Ket luan

Voi kien truc nay, nhom co the code song song ma it dam chan nhau:

- UI va database la 2 huong tach biet.
- Realtime engine duoc dong goi rieng, de thay doi nguong va model.
- Schema DB nho gon, phu hop dung cho demo va bao cao do an.
- Desktop app duoc giu nhe va tap trung dung vao vai tro DRIVER.
- Nghiep vu quan tri he thong duoc dua ve huong web admin de hop ly hon.

Buoc tiep theo la hoan thien desktop runtime cho DRIVER, sau do moi mo rong sang phan web admin neu can.
