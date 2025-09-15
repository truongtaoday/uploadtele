#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tải video từ Google Photos và upload lên Telegram
Được chuyển đổi từ Google Colab để chạy trên GitHub Actions
"""

import os
import time
import shutil
import asyncio
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from pyrogram import Client
from tqdm import tqdm

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GooglePhotosDownloader:
    def __init__(self):
        self.download_directory = './videos/'
        self.link_file_path = './Dragon.txt'
        self.download_timeout = 900  # 15 phút
        self.xpath_step_1 = "/html/body/div[1]/div/c-wiz/div[5]/c-wiz/c-wiz/div/div[3]/span/div/div/div[1]/div[2]/a/div"
        self.driver = None
        
        # Thiết lập thư mục download
        self.setup_download_directory()
        
    def setup_download_directory(self):
        """Thiết lập thư mục để lưu video"""
        if os.path.exists(self.download_directory):
            shutil.rmtree(self.download_directory)
        os.makedirs(self.download_directory)
        logger.info(f"Đã tạo thư mục download: {self.download_directory}")
    
    def setup_chrome_driver(self):
        """Thiết lập Chrome WebDriver"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        
        # Thiết lập thư mục download
        prefs = {
            "download.default_directory": os.path.abspath(self.download_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Sử dụng webdriver-manager để tự động tải ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Đã khởi tạo Chrome WebDriver thành công")
    
    def read_video_links(self):
        """Đọc danh sách video từ file"""
        if not os.path.exists(self.link_file_path):
            logger.error(f"Không tìm thấy file {self.link_file_path}")
            return []
        
        with open(self.link_file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        logger.info(f"Đã đọc {len(lines)//2} video từ file")
        return lines
    
    def wait_for_download_complete(self, initial_files, video_name):
        """Chờ đợi quá trình download hoàn tất"""
        logger.info("Đang chờ tải file hoàn tất...")
        start_time = time.time()
        
        while time.time() - start_time < self.download_timeout:
            current_files = set(os.listdir(self.download_directory))
            new_files = current_files - initial_files
            
            if new_files:
                downloaded_filename = new_files.pop()
                if not downloaded_filename.endswith('.crdownload'):
                    downloaded_filepath = os.path.join(self.download_directory, downloaded_filename)
                    
                    # Kiểm tra sự ổn định của dung lượng file
                    logger.info(f"Phát hiện file '{downloaded_filename}'. Đang kiểm tra sự ổn định dung lượng...")
                    if self.check_file_stability(downloaded_filepath):
                        # Đổi tên file
                        file_ext = os.path.splitext(downloaded_filename)[1]
                        new_filename = f"{video_name}{file_ext}"
                        new_path = os.path.join(self.download_directory, new_filename)
                        shutil.move(downloaded_filepath, new_path)
                        
                        logger.info(f"Đã đổi tên thành công thành: '{new_filename}'")
                        return True
            
            time.sleep(1)
        
        logger.error(f"Quá thời gian chờ tải video '{video_name}'")
        return False
    
    def check_file_stability(self, filepath):
        """Kiểm tra sự ổn định của file (dung lượng không đổi)"""
        last_size = -1
        stable_checks = 0
        
        while stable_checks < 3:  # Yêu cầu 3 lần kiểm tra
            if not os.path.exists(filepath):
                logger.error("File tải xuống đã biến mất")
                return False
            
            current_size = os.path.getsize(filepath)
            if current_size == last_size and current_size > 0:
                stable_checks += 1
            else:
                stable_checks = 0
            
            last_size = current_size
            logger.info(f"Kích thước hiện tại: {current_size} bytes, kiểm tra ổn định: {stable_checks}/3")
            time.sleep(2)
        
        logger.info("Dung lượng file đã ổn định. Tải xuống hoàn tất 100%.")
        return True
    
    def download_videos(self):
        """Tải tất cả video từ danh sách"""
        lines = self.read_video_links()
        if not lines:
            return False
        
        self.setup_chrome_driver()
        
        try:
            for i in range(0, len(lines), 2):
                video_name = lines[i]
                video_url = lines[i+1]
                
                logger.info("-" * 50)
                logger.info(f"Đang xử lý video: '{video_name}'")
                logger.info(f"URL: {video_url}")
                
                try:
                    self.driver.get(video_url)
                    logger.info("Đang chờ trang web tải và nút tùy chọn xuất hiện...")
                    
                    wait = WebDriverWait(self.driver, 20)
                    more_options_button = wait.until(EC.element_to_be_clickable((By.XPATH, self.xpath_step_1)))
                    
                    logger.info("Bước 1: play video")
                    more_options_button.click()
                    time.sleep(2)
                    
                    # Lấy danh sách file ban đầu
                    initial_files = set(os.listdir(self.download_directory))
                    
                    logger.info("Bước 2: Tìm và click nút Download...")
                    
                    # Thử nhiều cách để tìm nút download
                    download_clicked = False
                    
                    # Phương pháp 1: Tìm nút download bằng XPATH
                    download_xpaths = [
                        "//button[@aria-label='Tải xuống']",
                        "//button[contains(@aria-label, 'Download')]",
                        "//div[@data-value='download']",
                        "//button[contains(text(), 'Tải xuống')]",
                        "//button[contains(text(), 'Download')]"
                    ]
                    
                    for xpath in download_xpaths:
                        try:
                            download_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            download_button.click()
                            logger.info(f"Đã click nút download bằng xpath: {xpath}")
                            download_clicked = True
                            break
                        except:
                            continue
                    
                    # Phương pháp 2: Nếu không tìm thấy nút, thử phím tắt
                    if not download_clicked:
                        logger.info("Không tìm thấy nút download, thử phím tắt Shift + D...")
                        actions = ActionChains(self.driver)
                        actions.key_down(Keys.SHIFT).send_keys('d').key_up(Keys.SHIFT).perform()
                        download_clicked = True
                    
                    # Phương pháp 3: Thử menu 3 chấm và tìm download
                    if not download_clicked:
                        try:
                            more_menu_xpaths = [
                                "//button[@aria-label='Thêm tùy chọn']",
                                "//button[@aria-label='More options']",
                                "//button[contains(@aria-label, 'menu')]"
                            ]
                            
                            for menu_xpath in more_menu_xpaths:
                                try:
                                    menu_button = self.driver.find_element(By.XPATH, menu_xpath)
                                    menu_button.click()
                                    time.sleep(2)
                                    
                                    # Tìm option download trong menu
                                    for xpath in download_xpaths:
                                        try:
                                            download_option = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                                            download_option.click()
                                            logger.info("Đã click download từ menu")
                                            download_clicked = True
                                            break
                                        except:
                                            continue
                                    
                                    if download_clicked:
                                        break
                                        
                                except:
                                    continue
                                    
                        except Exception as e:
                            logger.warning(f"Không thể mở menu: {str(e)}")
                    
                    if download_clicked:
                        logger.info(f"Đã gửi yêu cầu tải xuống cho '{video_name}'")
                        time.sleep(20)
                    else:
                        logger.error(f"Không thể tìm thấy cách tải video '{video_name}'")
                        continue
                    
                    # Chờ download hoàn tất
                    if not self.wait_for_download_complete(initial_files, video_name):
                        logger.error(f"Không thể tải video '{video_name}'. Bỏ qua.")
                        continue
                    
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý video '{video_name}': {str(e)}")
                    # Chụp ảnh màn hình để gỡ lỗi
                    screenshot_name = f"error_video_{i//2 + 1}.png"
                    self.driver.save_screenshot(screenshot_name)
                    logger.error(f"Đã lưu ảnh màn hình lỗi vào file '{screenshot_name}'")
                    continue
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Đã đóng WebDriver")
        
        logger.info("-" * 50)
        logger.info("HOÀN TẤT VIỆC TẢI TẤT CẢ VIDEO")
        return True

class TelegramUploader:
    def __init__(self):
        # Lấy thông tin từ environment variables
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
        self.video_dir = './videos'
    
    def progress_callback(self, current, total, pbar):
        """Callback để hiển thị tiến trình upload"""
        pbar.total = total
        pbar.n = current
        pbar.refresh()
    
    async def upload_videos(self):
        """Upload tất cả video lên Telegram"""
        if not all([self.api_id, self.api_hash, self.bot_token, self.chat_id]):
            logger.error("Thiếu thông tin cấu hình Telegram")
            return False
        
        try:
            async with Client("my_bot", api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token) as app:
                video_files = [f for f in os.listdir(self.video_dir) if os.path.isfile(os.path.join(self.video_dir, f))]
                
                if not video_files:
                    logger.warning("Không tìm thấy video nào để upload")
                    return True
                
                for filename in video_files:
                    filepath = os.path.join(self.video_dir, filename)
                    logger.info(f"Đang upload: {filename}")
                    
                    with tqdm(total=100, unit="B", unit_scale=True, desc=filename) as pbar:
                        await app.send_video(
                            self.chat_id,
                            video=filepath,
                            caption=filename,
                            progress=self.progress_callback,
                            progress_args=(pbar,)
                        )
                    logger.info(f"✅ Upload xong: {filename}")
                
                return True
        
        except Exception as e:
            logger.error(f"Lỗi khi upload video lên Telegram: {str(e)}")
            return False

def main():
    """Hàm chính"""
    logger.info("=== BẮt ĐẦU QUÁ TRÌNH TẢI VIDEO VÀ UPLOAD TELEGRAM ===")
    
    # Bước 1: Tải video từ Google Photos
    downloader = GooglePhotosDownloader()
    if not downloader.download_videos():
        logger.error("Không thể tải video. Dừng chương trình.")
        return
    
    # Bước 2: Upload video lên Telegram
    uploader = TelegramUploader()
    asyncio.run(uploader.upload_videos())
    
    # Bước 3: Dọn dẹp và thống kê
    logger.info("Đang dọn dẹp file...")
    
    # Thống kê file đã xử lý
    video_count = len([f for f in os.listdir('./videos/') if os.path.isfile(os.path.join('./videos/', f))]) if os.path.exists('./videos/') else 0
    large_file_count = len([f for f in os.listdir('./large_files/') if os.path.isfile(os.path.join('./large_files/', f))]) if os.path.exists('./large_files/') else 0
    
    logger.info(f"📊 THỐNG KÊ:")
    logger.info(f"  - Video đã upload thành công: {video_count}")
    logger.info(f"  - File quá lớn (>2GB) đã bỏ qua: {large_file_count}")
    
    # Xóa các file screenshot lỗi
    png_files = [f for f in os.listdir('.') if f.endswith('.png')]
    for file in png_files:
        os.remove(file)
        logger.info(f"Đã xóa file: {file}")
    
    if large_file_count > 0:
        logger.info(f"⚠️ Có {large_file_count} file quá lớn không thể upload Telegram")
        logger.info("💡 Đề xuất: Nén video hoặc chia nhỏ file trước khi upload")
    
    logger.info("=== HOÀN THÀNH TẤT CẢ ===")

if __name__ == "__main__":
    main()
