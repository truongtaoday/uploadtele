# Google Photos Video Downloader & Telegram Uploader

Tự động tải video từ Google Photos và upload lên Telegram Bot bằng GitHub Actions.

## 🚀 Tính năng

- ✅ Tự động tải video từ Google Photos
- ✅ Upload video lên Telegram qua Bot
- ✅ Chạy tự động theo lịch trình với GitHub Actions
- ✅ Xử lý lỗi và logging chi tiết
- ✅ Headless browser (không cần giao diện)

## 📋 Yêu cầu

1. **Telegram Bot Token**: Tạo bot từ [@BotFather](https://t.me/botfather)
2. **Telegram API credentials**: Lấy từ [my.telegram.org](https://my.telegram.org)
3. **GitHub repository** với quyền Actions

## 🔧 Cài đặt

### Bước 1: Fork repository này

Click vào nút **Fork** ở góc phải trên để tạo bản sao trong tài khoản GitHub của bạn.

### Bước 2: Thiết lập Secrets

Trong repository của bạn, vào **Settings** → **Secrets and variables** → **Actions**, thêm các secrets sau:

| Secret Name | Mô tả | Ví dụ |
|-------------|-------|-------|
| `TELEGRAM_API_ID` | API ID từ my.telegram.org | `12345678` |
| `TELEGRAM_API_HASH` | API Hash từ my.telegram.org | `abcdef123456789` |
| `TELEGRAM_BOT_TOKEN` | Token từ @BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `TELEGRAM_CHAT_ID` | User ID của bạn | `987654321` |

### Bước 3: Cập nhật danh sách video

Chỉnh sửa file `Dragon.txt` với định dạng:
```
Tên video 1
https://photos.google.com/share/link1
Tên video 2
https://photos.google.com/share/link2
```

### Bước 4: Kích hoạt GitHub Actions

1. Vào tab **Actions**
2. Click **I understand my workflows, go ahead and enable them**
3. Workflow sẽ tự động chạy

## ⚙️ Cấu hình

### Lịch chạy tự động

Trong file `.github/workflows/download-upload.yml`, bạn có thể thay đổi lịch chạy:

```yaml
schedule:
  - cron: '0 2 * * *'  # Chạy lúc 2:00 UTC mỗi ngày
```

### Timeout và retry

Trong `main.py`, bạn có thể điều chỉnh:

```python
self.download_timeout = 900  # 15 phút timeout cho mỗi video
```

## 🏃‍♂️ Chạy thủ công

### Trên GitHub Actions

1. Vào tab **Actions**
2. Chọn workflow **"Download Videos and Upload to Telegram"**
3. Click **"Run workflow"**

### Chạy local

```bash
# Clone repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Cài đặt dependencies
pip install -r requirements.txt

# Thiết lập environment variables
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Chạy script
python main.py
```

## 📁 Cấu trúc project

```
.
├── .github/
│   └── workflows/
│       └── download-upload.yml    # GitHub Actions workflow
├── main.py                        # Script chính
├── requirements.txt               # Python dependencies
├── Dragon.txt                     # Danh sách video cần tải
└── README.md                      # Hướng dẫn này
```

## 🐛 Troubleshooting

### Lỗi Selenium

- **Lỗi ChromeDriver**: Workflow tự động cài đặt Chrome và ChromeDriver tương thích
- **Timeout**: Tăng `download_timeout` nếu video lớn
- **XPATH không tìm thấy**: Google Photos có thể thay đổi giao diện, cần cập nhật XPATH

### Lỗi Telegram

- **Bot token sai**: Kiểm tra token từ @BotFather
- **Chat ID sai**: Nhắn tin `/start` cho @userinfobot để lấy chat ID
- **API credentials**: Đảm bảo API ID và Hash đúng từ my.telegram.org

### Lỗi GitHub Actions

- **Secrets không được thiết lập**: Kiểm tra trong Settings → Secrets
- **Workflow bị vô hiệu hóa**: Kích hoạt trong tab Actions
- **Quota vượt hạn**: GitHub Actions có giới hạn 2000 phút/tháng cho tài khoản miễn phí

## 📝 Logs và Debug

Khi có lỗi, check:

1. **GitHub Actions logs**: Tab Actions → chọn run → xem chi tiết
2. **Error screenshots**: Tự động upload làm artifacts khi có lỗi
3. **Console logs**: Script ghi log chi tiết mọi bước

## ⚠️ Giới hạn dung lượng file

### GitHub Actions limitations:
- ✅ **Dung lượng tối đa**: 2GB per file (được kiểm tra tự động)
- ✅ **Thời gian timeout**: 30 phút cho mỗi video (tăng từ 15 phút)
- ✅ **Telegram Bot API**: 2GB limit cho upload

### Xử lý file lớn:
- 🔍 **Tự động phát hiện** file >2GB trước khi tải
- 📁 **File quá lớn** sẽ được di chuyển vào thư mục `large_files/` 
- 📊 **Thống kê chi tiết** về dung lượng file sau khi hoàn thành
- ⚠️ **Cảnh báo** file >500MB sẽ mất nhiều thời gian

### Giải pháp cho file lớn:
1. **Nén video** bằng tool như FFmpeg trước khi upload
2. **Chia nhỏ video** thành nhiều phần
3. **Sử dụng Telegram Client** thay vì Bot (hỗ trợ file lên đến 4GB)
4. **Upload manual** qua Google Drive hoặc cloud storage khác

## 🔄 Tự động hóa nâng cao

### Webhook từ Google Photos

Bạn có thể thiết lập webhook để tự động trigger workflow khi có video mới.

### Notification

Thêm notification khi hoàn thành:

```python
await app.send_message(chat_id, "✅ Đã tải và upload xong tất cả video!")
```

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo Issue hoặc Pull Request.

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.
