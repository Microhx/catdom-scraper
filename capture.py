import os
import subprocess
import json

def get_video_data(url):
    # 增加 --cookies 参数
    cmd = f'yt-dlp --cookies cookies.txt --extractor-args "youtube:player_client=android" --get-duration --get-id -f b {url}'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip().split('\n')
    duration_str = output[-2] # 倒数第二行通常是时长
    v_id = output[-1]
    
    parts = duration_str.split(':')
    seconds = int(parts[-1]) + int(parts[-2]) * 60 if len(parts) >= 2 else int(parts[0])
    return v_id, seconds

def take_screenshot(url, timestamp, output_name):
    try:
        # 增加 --cookies 参数获取流地址
        get_url_cmd = f'yt-dlp --cookies cookies.txt --extractor-args "youtube:player_client=android" -g -f b {url}'
        stream_url = subprocess.check_output(get_url_cmd, shell=True).decode('utf-8').strip()
        
        # ffmpeg 截图（-ss 放在 -i 前面速度极快）
        cmd = f'ffmpeg -ss {timestamp} -i "{stream_url}" -vframes 1 -q:v 2 {output_name} -y'
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"Failed to capture {output_name}: {e}")

def main():
    if not os.path.exists('screenshots'): os.makedirs('screenshots')
    with open('videos.txt', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            v_id, total_sec = get_video_data(url)
            print(f"Processing Level: {v_id} (Duration: {total_sec}s)")
            
            # 精准截图逻辑：
            # 1. 初始图 (3秒)
            take_screenshot(url, 3, f"screenshots/{v_id}_1.jpg")
            # 2. 中期图 (时长的一半)
            take_screenshot(url, total_sec // 2, f"screenshots/{v_id}_2.jpg")
            # 3. 冲刺图 (时长的 80%)
            take_screenshot(url, int(total_sec * 0.8), f"screenshots/{v_id}_3.jpg")
            # 4. 结算图 (时长减去 2 秒，非常精准)
            take_screenshot(url, total_sec - 2, f"screenshots/{v_id}_4.jpg")
        except Exception as e:
            print(f"Failed {url}: {e}")

if __name__ == "__main__":
    main()
