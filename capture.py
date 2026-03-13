import os
import subprocess

def get_video_data(url):
    print(f"DEBUG: Extracting data for URL: {url}")
    cmd = [
        'yt-dlp', 
        '--cookies', 'cookies.txt',
        '--extractor-args', 'youtube:player_client=android',
        '--print', '%(duration)s', 
        '--print', '%(id)s',
        url
    ]
    # 使用 check=True，如果失败会直接抛出异常
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = result.stdout.strip().split('\n')
    
    duration_str = lines[0]
    v_id = lines[1]
    
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 1: total_sec = parts[0]
    elif len(parts) == 2: total_sec = parts[0] * 60 + parts[1]
    else: total_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
    
    return v_id, total_sec

def take_screenshot(url, timestamp, output_name):
    try:
        # 只获取视频流地址
        get_url_cmd = ['yt-dlp', '--cookies', 'cookies.txt', '-g', '-f', 'bestvideo', url]
        stream_url = subprocess.check_output(get_url_cmd, text=True).strip().split('\n')[0]
        
        # ffmpeg 截图
        cmd = [
            'ffmpeg', '-ss', str(timestamp), 
            '-i', stream_url, 
            '-vframes', '1', '-q:v', '2', 
            output_name, '-y'
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"   - Saved: {output_name}")
    except Exception as e:
        print(f"   - Screenshot Error: {e}")

def main():
    if not os.path.exists('screenshots'): os.makedirs('screenshots')
    
    if not os.path.exists('videos.txt'):
        print("Error: videos.txt not found!")
        return

    with open('videos.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            parts = line.split()
            url = ""
            level_num = "unknown"
            
            # 智能识别 URL 和编号
            for p in parts:
                if p.startswith("http"):
                    url = p
                else:
                    level_num = p
            
            if not url:
                print(f"Skipping line: {line} (No URL found)")
                continue

            try:
                print(f"--- Processing Level {level_num} ---")
                v_id, total_sec = get_video_data(url)
                
                # 截图逻辑
                take_screenshot(url, 2, f"screenshots/level_{level_num}_1.jpg")
                take_screenshot(url, total_sec // 2, f"screenshots/level_{level_num}_2.jpg")
                take_screenshot(url, int(total_sec * 0.8), f"screenshots/level_{level_num}_3.jpg")
                take_screenshot(url, max(0, total_sec - 2), f"screenshots/level_{level_num}_4.jpg")
            except Exception as e:
                print(f"Critical error on line '{line}': {e}")

if __name__ == "__main__":
    main()
