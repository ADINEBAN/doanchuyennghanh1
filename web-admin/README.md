# Driver Monitor Web Admin

Web admin dùng để quản lý hệ thống giám sát tài xế: hãng xe, xe, tài khoản, phiên giám sát, cảnh báo và thống kê realtime từ desktop app.

## Công nghệ

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- Supabase Auth, Database, Row Level Security và Realtime

## Chức năng chính

- Đăng nhập cho `SUPER_ADMIN` và `COMPANY_ADMIN`.
- Chặn tài khoản `DRIVER` đăng nhập web admin.
- `SUPER_ADMIN` quản lý hãng xe, xe, tài khoản quản lý hãng và tài xế.
- `COMPANY_ADMIN` quản lý tài xế và xe trong phạm vi hãng của mình.
- Theo dõi trạng thái realtime của tài xế từ bảng `driver_live_status`.
- Xem phiên giám sát, cảnh báo và thống kê vận hành.

## Cấu trúc thư mục

```text
src/
  app/                    Route của Next.js App Router
    api/admin/create-user API tạo user bằng Supabase service role
    dashboard/            Trang tổng quan realtime
    companies/            Quản lý hãng xe
    vehicles/             Quản lý xe
    drivers/              Quản lý tài khoản và chi tiết tài xế
    sessions/             Danh sách phiên giám sát
    alerts/               Lịch sử cảnh báo
    statistics/           Thống kê
    settings/             Thiết lập hệ thống
  components/
    layout/               Shell, auth gate
    ui/                   Component dùng chung như table, badge, stat card
  contexts/               AuthContext
  lib/                    Supabase client, format, live-status helpers
  types/                  TypeScript type cho database
```

## Biến môi trường

Tạo file `.env.local` trong thư mục `web-admin`:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

`SUPABASE_SERVICE_ROLE_KEY` chỉ dùng ở API server để tạo tài khoản mới. Không đưa key này vào client hoặc public repo.

## Cài đặt và chạy

```bash
npm install
npm run dev
```

Mở `http://localhost:3000`.

Kiểm tra lint:

```bash
npm run lint
```

Trên Windows PowerShell nếu bị chặn `npm.ps1`, dùng:

```bash
npm.cmd run lint
```

## Database và realtime

Chạy migration realtime:

```text
../db/migrations/20260512_driver_live_status.sql
```

Migration này tạo bảng `driver_live_status`, bật RLS và thêm bảng vào publication `supabase_realtime`.

Các bảng chính web admin đang sử dụng:

- `profiles`
- `companies`
- `vehicles`
- `monitoring_sessions`
- `alerts`
- `user_settings`
- `driver_live_status`

## Phân quyền

- `SUPER_ADMIN`: xem và quản lý toàn hệ thống.
- `COMPANY_ADMIN`: chỉ xem và quản lý dữ liệu thuộc `company_id` của mình.
- `DRIVER`: dùng desktop app, không dùng web admin.

API tạo user nằm ở `src/app/api/admin/create-user/route.ts` và kiểm tra quyền bằng token đăng nhập hiện tại trước khi dùng service role.

## Checklist demo

- Đăng nhập bằng tài khoản `SUPER_ADMIN`.
- Tạo hãng xe.
- Tạo tài khoản `COMPANY_ADMIN` hoặc `DRIVER`.
- Gán xe cho tài xế.
- Mở desktop app để cập nhật `driver_live_status`.
- Kiểm tra Dashboard, Drivers, Sessions và Alerts có cập nhật realtime.

