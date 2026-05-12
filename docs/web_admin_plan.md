# Ke Hoach Phat Trien Web Admin

Tai lieu nay mo ta ke hoach lam web admin cho he thong canh bao buon ngu tai xe.

## 1. Muc tieu

Web admin dung cho 2 vai tro:

- `SUPER_ADMIN`
- `COMPANY_ADMIN`

Web admin khong danh cho `DRIVER`. Tai xe su dung desktop app Python de dang nhap, mo webcam, giam sat va luu session/alert len Supabase.

## 2. Stack De Xuat

Su dung:

- Next.js
- TypeScript
- Tailwind CSS
- Supabase Auth
- Supabase PostgreSQL
- Supabase Realtime

Thu muc de xuat:

```text
web-admin/
|-- app/
|   |-- login/
|   |-- dashboard/
|   |-- companies/
|   |-- vehicles/
|   |-- drivers/
|   |-- sessions/
|   |-- alerts/
|   |-- statistics/
|   |-- settings/
|   `-- api/
|       `-- admin/
|-- components/
|-- lib/
|-- types/
|-- middleware.ts
|-- .env.local
`-- package.json
```

## 3. Kien Truc Ket Noi

Kien truc tong the:

```text
Desktop App Python
-> Supabase Auth + Database + Realtime

Web Admin Next.js
-> Supabase client voi anon key de doc/ghi du lieu theo RLS
-> Next.js API routes/server actions voi service role cho tac vu admin nhay cam
```

Bien moi truong web:

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

Luu y:

- `NEXT_PUBLIC_*` co the dung o client/browser.
- `SUPABASE_SERVICE_ROLE_KEY` chi duoc dung server-side trong API route hoac server action.
- Khong bao gio dua `SUPABASE_SERVICE_ROLE_KEY` vao component client.

## 4. Co Can Backend Rieng Khong?

Khong can backend rieng kieu Express/FastAPI cho MVP.

Supabase dong vai tro backend cho:

- Authentication
- Database
- Realtime
- Row Level Security

Next.js dong vai tro server-side cho cac chuc nang can service role:

- Tao tai khoan `COMPANY_ADMIN`
- Tao tai khoan `DRIVER`
- Reset password
- Khoa/mo khoa user auth
- Xoa user auth neu can
- Tac vu admin nhay cam khac

## 5. Phan Quyen

### SUPER_ADMIN

Co quyen:

- Dang nhap web admin.
- Quan ly hang xe.
- Tao tai khoan `COMPANY_ADMIN`.
- Xem toan bo users.
- Xem toan bo vehicles.
- Xem toan bo sessions.
- Xem toan bo alerts.
- Xem thong ke toan he thong.
- Quan ly AI models.
- Cau hinh nguong mac dinh.

### COMPANY_ADMIN

Co quyen:

- Dang nhap web admin.
- Xem/cap nhat thong tin hang xe cua minh.
- Quan ly xe thuoc hang minh.
- Tao tai khoan `DRIVER`.
- Quan ly tai xe/nguoi thue xe cua hang minh.
- Gan xe cho tai xe.
- Xem sessions cua tai xe thuoc hang minh.
- Xem alerts cua tai xe thuoc hang minh.
- Xem thong ke theo tai xe, xe, ngay.
- Xuat bao cao neu co.

### DRIVER

Khong duoc vao web admin.

Neu `DRIVER` dang nhap web:

- Redirect ve trang login.
- Hien thong bao tai khoan nay chi dung cho desktop app.

## 6. Cac Man Hinh Can Lam

### 6.1 Login

Route:

```text
/login
```

Chuc nang:

- Email/password login.
- Lay profile tu bang `profiles`.
- Chan role `DRIVER`.
- Cho phep `SUPER_ADMIN` va `COMPANY_ADMIN` vao dashboard.

### 6.2 Dashboard

Route:

```text
/dashboard
```

SUPER_ADMIN xem:

- Tong hang xe.
- Tong tai xe.
- Tong xe.
- Tong session.
- Tong alert.
- Alert hom nay.
- Session dang chay.

COMPANY_ADMIN xem:

- Tong xe cua hang.
- Tong tai xe cua hang.
- Session dang chay cua hang.
- Alert hom nay cua hang.
- Alert gan day.

### 6.3 Companies

Route:

```text
/companies
```

Chi danh cho `SUPER_ADMIN`.

Chuc nang:

- Danh sach hang xe.
- Them hang xe.
- Sua hang xe.
- Khoa/mo khoa hang xe.
- Xem so xe/tai xe/session cua hang.

Bang:

```text
companies
```

### 6.4 Vehicles

Route:

```text
/vehicles
```

SUPER_ADMIN:

- Xem toan bo xe.

COMPANY_ADMIN:

- Chi xem xe cua `company_id` minh.

Chuc nang:

- Them xe.
- Sua xe.
- Xoa/an xe.
- Doi trang thai xe.
- Gan xe cho tai xe.

Bang:

```text
vehicles
profiles
```

### 6.5 Drivers

Route:

```text
/drivers
```

Chuc nang:

- Danh sach tai xe.
- Tao tai khoan `DRIVER`.
- Sua thong tin tai xe.
- Khoa/mo khoa tai xe.
- Gan xe cho tai xe.

Luu y:

- Tao user auth phai dung API route/server action voi `SUPABASE_SERVICE_ROLE_KEY`.
- Sau khi tao auth user, can insert/update bang `profiles`.

### 6.6 Sessions

Route:

```text
/sessions
```

Hien thi:

- Tai xe.
- Xe.
- Hang xe.
- Thoi gian bat dau.
- Thoi gian ket thuc.
- Trang thai.
- Tong canh bao.
- So lan nham mat.
- So lan ngap.
- So lan buon ngu.
- So lan mat tap trung.

Bang:

```text
monitoring_sessions
profiles
vehicles
companies
```

Realtime:

- Subscribe bang `monitoring_sessions`.
- Khi desktop app start/stop session, web cap nhat ngay.

### 6.7 Alerts

Route:

```text
/alerts
```

Hien thi:

- Thoi gian.
- Tai xe.
- Xe.
- Loai canh bao.
- Muc rui ro.
- EAR.
- MAR.
- Goc mat.
- AI label neu co.

Bang:

```text
alerts
```

Realtime:

- Subscribe bang `alerts`.
- Khi desktop app tao alert, web hien canh bao moi gan nhu ngay lap tuc.

### 6.8 Statistics

Route:

```text
/statistics
```

Bieu do can co:

- Canh bao theo ngay.
- Canh bao theo loai.
- Canh bao theo muc rui ro.
- Top tai xe nhieu canh bao.
- Top xe nhieu canh bao.

SUPER_ADMIN xem toan he thong.

COMPANY_ADMIN chi xem du lieu hang cua minh.

### 6.9 Settings

Route:

```text
/settings
```

SUPER_ADMIN:

- Quan ly nguong mac dinh.
- Quan ly AI model.

Bang:

```text
system_settings
ai_models
```

## 7. Realtime Trang Thai Tai Xe

MVP co the biet tai xe dang hoat dong bang:

```text
monitoring_sessions.status = running
```

Va biet canh bao realtime qua:

```text
alerts
```

Neu muon web hien chi tiet hon:

- Tai xe dang `normal`
- Dang `closed_eyes`
- Dang `yawning`
- EAR/MAR hien tai
- Camera active
- Last seen

Thi nen them bang:

```text
driver_live_status
```

Cot de xuat:

```text
driver_id
session_id
company_id
vehicle_id
status
risk_level
ear_value
mar_value
head_yaw
head_pitch
is_camera_active
last_seen_at
updated_at
```

Desktop app update bang nay moi 2-5 giay.

Web admin subscribe realtime bang nay de hien trang thai song.

Phan nay co the lam sau MVP.

## 8. Thu Tu Trien Khai MVP

Nen lam theo thu tu:

1. Khoi tao `web-admin`.
2. Cai Next.js + TypeScript + Tailwind.
3. Tao Supabase client.
4. Tao login page.
5. Tao auth guard va role guard.
6. Tao admin layout: sidebar, header, logout.
7. Tao dashboard co so.
8. Tao vehicles page.
9. Tao drivers page.
10. Tao sessions page.
11. Tao alerts page realtime.
12. Tao statistics page.
13. Tao companies page cho `SUPER_ADMIN`.
14. Tao API route tao user bang service role.
15. Polish UI va bo sung filter/export.

MVP dau tien can dat:

```text
Login web admin
-> vao dashboard
-> xem tai xe/xe
-> xem session dang chay realtime
-> xem alert realtime tu desktop app
```

## 9. API Routes Can Co

De tranh dua service role key ra frontend, cac tac vu admin nhay cam can di qua API route:

```text
POST /api/admin/create-user
PATCH /api/admin/update-user-status
POST /api/admin/reset-password
```

Trong do `create-user` can:

1. Kiem tra user hien tai co role hop le.
2. Neu `SUPER_ADMIN`, duoc tao `COMPANY_ADMIN`.
3. Neu `COMPANY_ADMIN`, duoc tao `DRIVER` trong company cua minh.
4. Goi Supabase Admin API de tao auth user.
5. Insert/update `profiles`.
6. Tao `user_settings` mac dinh.

## 10. Ghi Chu Bao Mat

- Bat buoc giu RLS tren Supabase.
- Khong tin vao UI de bao mat phan quyen.
- Moi query client phai di qua RLS.
- Moi tac vu service role phai kiem tra role trong API route.
- Khong dua `SUPABASE_SERVICE_ROLE_KEY` vao client component.
- Khong commit `.env.local`.

