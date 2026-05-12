# Supabase Setup Guide

Tai lieu nay dung de noi database Supabase that vao he thong giam sat buon ngu.

## 1. Tao project Supabase

1. Dang nhap `https://supabase.com`
2. Tao project moi
3. Ghi lai:
   - `Project URL`
   - `anon public key`
   - `service_role key` (dung cho Web Admin tao tai khoan user)

## 2. Chay schema database

1. Mo `SQL Editor` trong Supabase Dashboard
2. Copy toan bo noi dung file `db/supabase_schema.sql`
3. Chay toan bo script

Sau khi chay xong, database se co cac bang:

| Bang | Mo ta |
|------|-------|
| `companies` | Hang xe dich vu |
| `profiles` | Thong tin user (3 role: SUPER_ADMIN, COMPANY_ADMIN, DRIVER) |
| `vehicles` | Xe thuoc hang |
| `user_settings` | Cai dat nguong canh bao cho tung user |
| `monitoring_sessions` | Phien giam sat |
| `alerts` | Canh bao buon ngu |
| `ai_models` | Model AI dang quan ly |
| `system_settings` | Cau hinh he thong (nguong mac dinh) |

Ngoai ra con co:

- Trigger tu dong tao `profile` + `user_settings` khi user moi dang ky
- Trigger tu dong cap nhat `updated_at` khi update
- RLS policies cho 3 role
- Views thong ke: `system_overview`, `daily_alert_stats`
- Seed data: nguong canh bao mac dinh

## 3. Tao SUPER_ADMIN dau tien

Sau khi chay schema:

### Buoc 1: Tao user trong Supabase Auth

1. Mo `Authentication` > `Users`
2. Bam `Add User` > `Create User`
3. Nhap email va password cho SUPER_ADMIN
4. Bat `Auto Confirm User`

### Buoc 2: Cap nhat role trong profiles

Chay SQL trong SQL Editor:

```sql
UPDATE profiles
SET role = 'SUPER_ADMIN'
WHERE email = 'your-super-admin@email.com';
```

Vay la da co tai khoan SUPER_ADMIN dau tien.

## 4. Dien file `.env`

### Cho Desktop App (DRIVER)

```env
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key
APP_ENV=development
DEFAULT_CAMERA_INDEX=0
MODEL_PATH=ml/exported_models/drowsiness_model.keras
EAR_THRESHOLD=0.23
EAR_CONSEC_FRAMES=20
MAR_THRESHOLD=0.65
YAWN_CONSEC_FRAMES=15
AI_PREDICTION_INTERVAL=5
DROWSY_ALERT_SECONDS=2
ALERT_SOUND_PATH=assets/sounds/alert.wav
```

### Cho Web Admin (SUPER_ADMIN / COMPANY_ADMIN)

File `.env` cua Web Admin can them `SERVICE_ROLE_KEY`:

```env
VITE_SUPABASE_URL=your_project_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

> **Chu y**: `SERVICE_ROLE_KEY` chi duoc su dung tren server hoac Edge Function.
> KHONG duoc de key nay trong desktop app hoac code frontend public.

## 5. Luong tao tai khoan theo role

### SUPER_ADMIN tao COMPANY_ADMIN

1. SUPER_ADMIN dang nhap Web Admin
2. Tao company moi
3. Tao user moi qua Supabase Admin API (su dung `SERVICE_ROLE_KEY`)
4. He thong tu dong:
   - Tao user trong `auth.users`
   - Trigger tao `profiles` voi role mac dinh la DRIVER
   - Web Admin cap nhat `profiles.role = 'COMPANY_ADMIN'` va `profiles.company_id`

### COMPANY_ADMIN tao DRIVER

1. COMPANY_ADMIN dang nhap Web Admin
2. Tao tai khoan DRIVER qua Supabase Admin API
3. He thong tu dong:
   - Tao user trong `auth.users`
   - Trigger tao `profiles` voi role DRIVER
   - Web Admin cap nhat `profiles.company_id` = company cua COMPANY_ADMIN
4. COMPANY_ADMIN gan xe cho DRIVER

### DRIVER dang nhap Desktop App

1. DRIVER dung email va password duoc cap
2. Desktop app kiem tra `profiles.role == 'DRIVER'`
3. Lay thong tin company va vehicle duoc gan
4. Bat dau giam sat

## 6. Kiem tra ket noi

Chay:

```powershell
python scripts/verify_supabase_connection.py
```

## 7. Cau truc RLS tong quan

| Bang | SUPER_ADMIN | COMPANY_ADMIN | DRIVER |
|------|-------------|---------------|--------|
| `companies` | Full CRUD | Read/Update cong ty minh | Read cong ty minh |
| `profiles` | Full CRUD | Read cung cong ty, Update DRIVER cung cong ty | Read/Update chinh minh |
| `vehicles` | Full CRUD | Full CRUD xe cong ty minh | Read xe duoc gan |
| `user_settings` | Read all | Read/Write chinh minh | Read/Write chinh minh |
| `monitoring_sessions` | Read all | Read cung cong ty | Read/Write chinh minh |
| `alerts` | Read all | Read cung cong ty | Read/Write chinh minh |
| `ai_models` | Full CRUD | Read (active) | Read (active) |
| `system_settings` | Full CRUD | Read | Read |

## 8. Tat email confirmation (cho demo)

Neu muon demo nhanh ma khong can xac nhan email:

1. Mo Supabase Dashboard > `Authentication` > `Providers`
2. Chon `Email`
3. Tat `Confirm email`

Luu y: Chi nen tat cho moi truong development/demo.
