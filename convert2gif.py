import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # pip install Pillow 필요
from moviepy import VideoFileClip

class VideoToGifApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convert2GIF(비디오 GIF 변환기)")
        self.root.geometry("540x760")
        self.root.resizable(False, False)
        
        self.video_path = ""
        self.video_duration = 0
        self.snapshot_images = []

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="🎬 비디오 GIF 변환기", font=("맑은 고딕", 15, "bold"))
        title_label.pack(pady=10)

        # 1. 파일 선택 프레임
        file_frame = tk.LabelFrame(self.root, text=" 1. 비디오 파일 선택 ", font=("맑은 고딕", 10, "bold"), padx=10, pady=8)
        file_frame.pack(fill="x", padx=20, pady=5)

        self.file_label = tk.Label(file_frame, text="선택된 파일 없음", fg="gray", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)

        btn_browse = tk.Button(file_frame, text="파일 찾기", command=self.load_video, bg="#4f46e5", fg="white", font=("맑은 고딕", 9, "bold"))
        btn_browse.pack(side="right", padx=5)

        # 2. 플랫폼 및 옵션 설정 프레임
        setting_frame = tk.LabelFrame(self.root, text=" 2. 플랫폼 맞춤 및 스마트 옵션 설정 ", font=("맑은 고딕", 10, "bold"), padx=10, pady=10)
        setting_frame.pack(fill="x", padx=20, pady=8)

        tk.Label(setting_frame, text="업로드 타겟 플랫폼:", font=("맑은 고딕", 9)).grid(row=0, column=0, sticky="w", pady=5)
        self.platform_combo = ttk.Combobox(setting_frame, values=["자유 설정 (Custom)", "깃허브 (GitHub - 10MB 제한)", "디스코드 (Discord - 8MB 제한)", "네이버 블로그/카페 (20MB)"], state="readonly", width=24)
        self.platform_combo.current(1) # 기본 깃허브 타겟
        self.platform_combo.grid(row=0, column=1, sticky="w", pady=5)
        self.platform_combo.bind("<<ComboboxSelected>>", lambda e: self.update_smart_optimizer())

        tk.Label(setting_frame, text="가로 해상도 (너비):", font=("맑은 고딕", 9)).grid(row=1, column=0, sticky="w", pady=5)
        self.res_combo = ttk.Combobox(setting_frame, values=["원본 유지", "640px(고화질)", "480px(일반/표준)", "320px(저화질)", "240px (초소형)"], state="readonly", width=24)
        self.res_combo.current(2) # 기본 480px 추천
        self.res_combo.grid(row=1, column=1, sticky="w", pady=5)
        self.res_combo.bind("<<ComboboxSelected>>", lambda e: self.update_smart_optimizer())

        tk.Label(setting_frame, text="프레임 레이트 (FPS):", font=("맑은 고딕", 9)).grid(row=2, column=0, sticky="w", pady=5)
        self.fps_spin = tk.Spinbox(setting_frame, from_=3, to=30, increment=1, width=26)
        self.fps_spin.delete(0, "end")
        self.fps_spin.insert(0, "8")
        self.fps_spin.grid(row=2, column=1, sticky="w", pady=5)

        self.guide_label = tk.Label(setting_frame, text="💡 깃허브 10MB 제한을 넘지 않도록 해상도와 FPS가 안전하게 최적화됩니다.", font=("맑은 고딕", 8), fg="#2563eb", wraplength=460, justify="left")
        self.guide_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        # 3. 구간 설정 프레임
        self.trim_frame = tk.LabelFrame(self.root, text=" 3. 구간 설정 (기본: 전체 영상) ", font=("맑은 고딕", 10, "bold"), padx=10, pady=10)
        self.trim_frame.pack(fill="x", padx=20, pady=8)

        self.snapshot_container = tk.Frame(self.trim_frame)
        self.snapshot_container.pack(fill="x", pady=5)

        self.range_status_label = tk.Label(self.trim_frame, text="영상을 불러오면 전체 구간이 기본 지정됩니다.", font=("맑은 고딕", 9, "bold"), fg="#4f46e5")
        self.range_status_label.pack(pady=5)

        input_frame = tk.Frame(self.trim_frame)
        input_frame.pack(pady=5)
        tk.Label(input_frame, text="시작 시간(초):", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=2)
        self.start_entry = tk.Entry(input_frame, width=8)
        self.start_entry.insert(0, "0")
        self.start_entry.pack(side="left", padx=5)
        
        tk.Label(input_frame, text="종료 시간(초):", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=2)
        self.end_entry = tk.Entry(input_frame, width=8)
        self.end_entry.insert(0, "0")
        self.end_entry.pack(side="left", padx=5)

        # 진행 상태바
        progress_frame = tk.Frame(self.root, padx=10, pady=5)
        progress_frame.pack(fill="x", padx=20)

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=460, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)

        self.status_label = tk.Label(progress_frame, text="대기 중...", font=("맑은 고딕", 9), fg="gray")
        self.status_label.pack(anchor="w")

        # 변환 버튼
        self.convert_btn = tk.Button(self.root, text="고화질 GIF 변환 시작", command=self.start_conversion_thread, bg="#10b981", fg="white", font=("맑은 고딕", 11, "bold"), state="disabled", pady=8)
        self.convert_btn.pack(fill="x", padx=20, pady=10)

    def update_smart_optimizer(self):
        platform = self.platform_combo.get()
        resolution = self.res_combo.get()
        
        recommended_fps = 8
        guide_msg = ""

        if "깃허브" in platform:
            recommended_fps = 8
            guide_msg = "⚠️ 깃허브 10MB 제한 안전 모드: 8 FPS 및 480px 이하 해상도를 권장합니다."
        elif "디스코드" in platform:
            recommended_fps = 7
            guide_msg = "⚠️ 디스코드 8MB 제한 안전 모드: 7 FPS 및 320px 이하를 권장합니다."
        elif "네이버" in platform:
            recommended_fps = 12
            guide_msg = "✨ 네이버 블로그/카페(~20MB): 12 FPS 적용."
        else:
            recommended_fps = 10
            guide_msg = "💡 자유 설정 모드입니다."

        self.fps_spin.delete(0, "end")
        self.fps_spin.insert(0, str(recommended_fps))
        self.guide_label.config(text=guide_msg)

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.webm *.mov *.avi *.mkv")])
        if file_path:
            self.video_path = file_path
            file_name = os.path.basename(file_path)
            
            try:
                self.file_label.config(text=f"{file_name} (정보 불러오는 중...)", fg="blue")
                self.convert_btn.config(state="disabled")
                
                threading.Thread(target=self.extract_thumbnails, args=(file_path,), daemon=True).start()

            except Exception as e:
                messagebox.showerror("오류", f"비디오를 불러올 수 없습니다:\n{e}")

    def extract_thumbnails(self, video_path):
        try:
            clip = VideoFileClip(video_path)
            self.video_duration = clip.duration
            
            for widget in self.snapshot_container.winfo_children():
                widget.destroy()
            self.snapshot_images = []

            times = [0, self.video_duration / 2, self.video_duration]
            labels = ["시작점 (클릭)", "중간점 50% (클릭)", "끝점 (클릭)"]

            for i, t in enumerate(times):
                frame = clip.get_frame(t)
                img = Image.fromarray(frame)
                img.thumbnail((150, 100))
                
                photo = ImageTk.PhotoImage(img)
                self.snapshot_images.append(photo)

                frame_btn = tk.Frame(self.snapshot_container)
                frame_btn.pack(side="left", padx=10, expand=True)
                
                tk.Label(frame_btn, text=labels[i], font=("맑은 고딕", 8, "bold")).pack()
                btn = tk.Button(frame_btn, image=photo, command=lambda time=t: self.on_snapshot_click(time))
                btn.pack()
                tk.Label(frame_btn, text=f"약 {t:.1f}초", font=("맑은 고딕", 8)).pack()

            clip.close()
            
            self.root.after(0, lambda: self.file_label.config(text=f"{os.path.basename(video_path)} ({self.video_duration:.1f}초)", fg="black"))
            self.root.after(0, lambda: self.start_entry.delete(0, "end"))
            self.root.after(0, lambda: self.start_entry.insert(0, "0"))
            self.root.after(0, lambda: self.end_entry.delete(0, "end"))
            self.root.after(0, lambda: self.end_entry.insert(0, f"{self.video_duration:.1f}"))
            
            self.root.after(0, lambda: self.range_status_label.config(text=f"기본 설정: 전체 구간 (0.0초 ~ {self.video_duration:.1f}초)"))
            self.root.after(0, lambda: self.convert_btn.config(state="normal"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"썸네일 추출 실패:\n{e}"))
            self.root.after(0, lambda: self.file_label.config(text="불러오기 실패", fg="red"))

    def on_snapshot_click(self, time_point):
        start_val = max(0, time_point - 2.5)
        end_val = min(self.video_duration, time_point + 2.5)
        
        self.range_status_label.config(text=f"구간 지정됨: {start_val:.1f}초 ~ {end_val:.1f}초")
        
        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, f"{start_val:.1f}")
        self.end_entry.delete(0, "end")
        self.end_entry.insert(0, f"{end_val:.1f}")

    def get_trim_times(self):
        try:
            start = float(self.start_entry.get())
            end = float(self.end_entry.get())
            return start, end
        except ValueError:
            return 0, self.video_duration

    def start_conversion_thread(self):
        threading.Thread(target=self.convert_video_to_gif, daemon=True).start()

    def convert_video_to_gif(self):
        try:
            self.convert_btn.config(state="disabled")
            self.status_label.config(text="변환 준비 중...", fg="blue")
            self.progress_bar['value'] = 15

            clip = VideoFileClip(self.video_path)

            start_trim, end_trim = self.get_trim_times()
            if end_trim > start_trim:
                clip = clip.subclipped(start_trim, min(end_trim, self.video_duration))

            platform = self.platform_combo.get()
            res_option = self.res_combo.get()

            # 해상도 적용
            if "원본" in res_option:
                if "깃허브" in platform and clip.w > 480:
                    clip = clip.resized(width=480)
                elif "디스코드" in platform and clip.w > 320:
                    clip = clip.resized(width=320)
            else:
                if "640px" in res_option: clip = clip.resized(width=640)
                elif "480px" in res_option: clip = clip.resized(width=480)
                elif "320px" in res_option: clip = clip.resized(width=320)
                elif "240px" in res_option: clip = clip.resized(width=240)

            fps = int(self.fps_spin.get())

            default_filename = os.path.splitext(os.path.basename(self.video_path))[0] + ".gif"
            save_path = filedialog.asksaveasfilename(defaultextension=".gif", initialfile=default_filename, filetypes=[("GIF File", "*.gif")])
            
            if not save_path:
                clip.close()
                self.convert_btn.config(state="normal")
                self.status_label.config(text="변환이 취소되었습니다.", fg="gray")
                self.progress_bar['value'] = 0
                return

            self.status_label.config(text="GIF 인코딩 중...", fg="blue")
            self.progress_bar['value'] = 40
            
            clip.write_gif(save_path, fps=fps)
            clip.close()

            # 📏 변환 완료 후 파일 용량 체크 및 맞춤형 안내 알림창 생성
            file_size_mb = os.path.getsize(save_path) / (1024 * 1024)

            self.progress_bar['value'] = 100
            self.status_label.config(text=f"변환 완료! ({file_size_mb:.2f} MB)", fg="green")
            
            # 플랫폼별 용량 제한 기준 정의 (MB)
            limit_mb = 10.0
            platform_name = "깃허브"
            if "디스코드" in platform:
                limit_mb = 8.0
                platform_name = "디스코드"
            elif "네이버" in platform:
                limit_mb = 20.0
                platform_name = "네이버 블로그/카페"

            if ("깃허브" in platform or "디스코드" in platform or "네이버" in platform) and file_size_mb > limit_mb:
                # 추천 대안 수치 계산
                current_duration = max(0.1, end_trim - start_trim)
                # 현재 초과 비율을 반영하여 안전한 최대 FPS 계산
                safe_fps = max(3, int(fps * (limit_mb / file_size_mb) * 0.9))
                
                # 구간 길이를 줄인다면 어느 정도로 줄여야 하는지 계산 (예: 제한 용량 비율만큼)
                suggested_duration = max(1.0, current_duration * (limit_mb / file_size_mb) * 0.9)
                suggested_end = start_trim + suggested_duration

                # 대안 해상도 추천 (현재 픽셀 너비 기준 한 단계 낮춘 너비 제안)
                current_width = clip.w
                if current_width > 480:
                    suggested_res = "480px"
                elif current_width > 320:
                    suggested_res = "320px"
                else:
                    suggested_res = "240px"

                warning_msg = (
                    f"생성된 파일 크기: {file_size_mb:.2f}MB\n"
                    f"{platform_name} 제한 용량({limit_mb}MB)을 초과합니다.\n\n"
                    f"파일 크기 축소를 위한 방법(택1):\n"
                    f"1. 구간 길이를 {start_trim:.1f}초 ~ {suggested_end:.1f}초로 줄이기\n"
                    f"2. 해상도를 {suggested_res}로 낮추기\n"
                    f"3. FPS를 {safe_fps} 이하로 낮추기"
                )
                messagebox.showwarning("용량 초과 경고", warning_msg)
            else:
                messagebox.showinfo("성공", f"GIF 변환 완료! (용량: {file_size_mb:.2f} MB)\n저장 경로: {save_path}")

        except Exception as e:
            self.status_label.config(text="변환 실패", fg="red")
            messagebox.showerror("오류", f"변환 중 오류가 발생했습니다:\n{e}")
        finally:
            self.convert_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToGifApp(root)
    root.mainloop()