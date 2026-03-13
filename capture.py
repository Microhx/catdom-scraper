import os
import subprocess

def get_video_data(url):
    # 使用 --print 替代老的 --get-duration，更稳定
    # 删除了 -f b，让系统自动选择
    cmd = [
        'yt-dlp', 
        '--cookies', 'cookies.txt',
        '--extractor-args', 'youtube:player_client=android',
        '--print', '%(duration)s', 
        '--print', '%(id)s',
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = result.stdout.strip().split('\n')
    
    duration_str = lines[0]
    v_id = lines[1]
    
    # 转换时长为秒 (处理 05, 01:20, 01:02:03 等各种情况)
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 1: total_sec = parts[0]
    elif len(parts) == 2: total_sec = parts[0] * 60 + parts[1]
    else: total_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
    
    return v_id, total_sec

def take_screenshot(url, timestamp, output_name):
    try:
        # 获取流地址，不限制格式，只要视频
        get_url_cmd = ['yt-dlp', '--cookies', 'cookies.txt', '-g', url]
        stream_url = subprocess.check_output(get_url_cmd, text=True).strip()
        
        # 截取第一条视频流
        first_url = stream_url.split('\n')[0]
        
        # ffmpeg 截图
        cmd = [
            'ffmpeg', '-ss', str(timestamp), 
            '-i', first_url, 
            '-vframes', '1', '-q:v', '2', 
            output_name, '-y'
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"Successfully saved: {output_name}")
    except Exception as e:
        print(f"Screenshot failed for {output_name}: {e}")

def main():
    if not os.path.exists('screenshots'): os.makedirs('screenshots')
    
    with open('videos.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # 核心改进：自动分割编号和网址
            # 如果一行是 "1 https://..."，会提取网址部分
            parts = line.split()
            level_num = parts[0] if len(parts) > 1 else "unknown"
            url = parts[-1] 
            
            try:
                v_id, total_sec = get_video_data(url)
                print(f"Processing Level {level_num} (ID: {v_id}, Duration: {total_sec}s)")
                
                # 设定截图时间点
                take_screenshot(url, 2, f"screenshots/level_{level_num}_1.jpg")
                take_screenshot(url, total_sec // 2, f"screenshots/level_{level_num}_2.jpg")
                take_screenshot(url, int(total_sec * 0.8), f"screenshots/level_{level_num}_3.jpg")
                take_screenshot(url, max(0, total_sec - 2), f"screenshots/level_{level_num}_4.jpg")
            except Exception as e:
                print(f"Failed to process line '{line}': {e}")

if __name__ == "__main__":
    main()
