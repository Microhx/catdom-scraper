import os
import subprocess
import sys

def get_video_data(url):
    print(f"\n[1/3] Fetching metadata for: {url}")
    # 强制获取时长和ID
    cmd = [
        'yt-dlp', 
        '--cookies', 'cookies.txt',
        '--extractor-args', 'youtube:player_client=ios', # 换成 ios 客户端试试
        '--print', '%(duration)s', 
        '--print', '%(id)s',
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp metadata error: {result.stderr}")
        return None, None
    
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
        # 获取流地址，这次我们不限制 bestvideo，让它自动选
        print(f"   [2/3] Getting stream URL for {output_name}...")
        get_url_cmd = ['yt-dlp', '--cookies', 'cookies.txt', '-g', url]
        res = subprocess.run(get_url_cmd, capture_output=True, text=True)
        
        if res.returncode != 0:
            print(f"   Error getting stream URL: {res.stderr}")
            return
            
        stream_url = res.stdout.strip().split('\n')[0]
        
        # ffmpeg 截图
        print(f"   [3/3] Running ffmpeg at {timestamp}s...")
        # 增加 -timeout 和 -reconnect 参数，防止网络波动导致截图失败
        cmd = [
            'ffmpeg', 
            '-ss', str(timestamp), 
            '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5',
            '-i', stream_url, 
            '-vframes', '1', 
            '-q:v', '2', 
            output_name, 
            '-y'
        ]
        # 我们不捕获错误，让它直接输出到控制台日志
        subprocess.run(cmd)
        
        if os.path.exists(output_name):
            print(f"   SUCCESS: Saved {output_name} (Size: {os.path.getsize(output_name)} bytes)")
        else:
            print(f"   FAILED: ffmpeg finished but {output_name} not found.")
            
    except Exception as e:
        print(f"   CRITICAL ERROR: {e}")

def main():
    if not os.path.exists('screenshots'): os.makedirs('screenshots')
    
    if not os.path.exists('videos.txt'):
        print("Error: videos.txt not found!")
        return

    with open('videos.txt', 'r') as f:
        urls_data = [line.strip() for line in f if line.strip()]

    print(f"Found {len(urls_data)} videos to process.")

    for line in urls_data:
        parts = line.split()
        url = next((p for p in parts if p.startswith("http")), None)
        level_num = next((p for p in parts if not p.startswith("http")), "unknown")
        
        if not url: continue

        v_id, total_sec = get_video_data(url)
        if v_id and total_sec:
            # 只截两张图做测试，减少失败概率
            take_screenshot(url, 5, f"screenshots/level_{level_num}_start.jpg")
            take_screenshot(url, total_sec - 5, f"screenshots/level_{level_num}_end.jpg")

if __name__ == "__main__":
    main()
