# 🎬 Video to GIF Converter
> **브라우저 탭 크래시(Out of Memory) 없이, 1분 이상의 긴 영상도 내 PC에서 안전하고 빠르게 고화질 GIF로 변환해 주는 데스크톱 애플리케이션입니다.**

Python과 `moviepy`, `Tkinter`를 활용하여 제작되었으며, GitHub, Discord, 네이버 블로그 등 주요 플랫폼의 용량 제한(`too big` 에러)을 자동으로 방어해 주는 스마트 최적화 알고리즘이 탑재되어 있습니다.

---

## ✨ 주요 기능 (Key Features)

* **🚫 메모리 폭발 방지 (Out of Memory Free):** 브라우저 기반 변환기의 한계를 극복하고, PC의 자원을 활용하여 안정적으로 렌더링합니다.
* **🎯 플랫폼 맞춤형 스마트 최적화:** 
  * **GitHub (~10MB 제한):** 고해상도 유지 및 용량 초과 방지를 위한 스마트 FPS/해상도 가이드 제공
  * **Discord (~8MB 제한):** 무료 티어 규격에 맞춘 엄격한 용량 방어
  * **네이버 블로그/카페 (~20MB):** 상대적으로 넉넉한 블로그 업로드용 고화질 맞춤 설정
  * **Custom (자유 설정):** 해상도와 FPS를 온전히 직접 제어
  * *만약 설정한 플랫폼의 최대 용량 초과시 알림 창으로 확인 가능*
* **🖼️ 3-스냅샷 빠른 구간 설정:** 영상을 불러오면 시작점, 중간점, 끝점의 대표 이미지를 미리 보여주어 마우스 클릭 한 번으로 원하는 구간을 빠르게 지정할 수 있습니다.
* **🎛️ 원본 해상도 사수 모드:** 화질을 포기할 수 없을 때, 해상도는 원본 그대로 유지하되 FPS를 유연하게 낮춰 용량 제한을 우회합니다.
* **📦 원클릭 파일명 자동 매칭:** 변환된 GIF 파일이 원본 동영상 이름과 동일한 이름으로 자동 지정되어 저장됩니다.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language:** Python 3.x
* **GUI Framework:** Tkinter, ttk
* **Video Processing:** MoviePy (FFmpeg wrapper)
* **Image Processing:** Pillow (PIL)

---

## 🚀 설치 및 사용 방법 (Installation & Usage)

### 1. 소스코드 클론 및 환경 설정
```bash
# 레포지토리 클론
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

# 필수 라이브러리 설치
pip install moviepy Pillow
