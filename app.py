import os
import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

st.title("🎬 Ứng dụng Tạo Video Từ Ảnh Tự Động")
st.write("Tải ảnh lên, tùy chỉnh thông số và xuất video của bạn ngay lập tức!")

# --- Khu vực cấu hình sidebar ---
st.sidebar.header("Tùy chỉnh Video")
duration_per_image = st.sidebar.slider("Thời lượng mỗi ảnh (giây):", 1, 10, 3)
fps = st.sidebar.selectbox("Khung hình (FPS):", [24, 30, 60], index=1)

resolution_option = st.sidebar.selectbox(
    "Độ phân giải:", 
    ["HD (1280x720)", "Full HD (1920x1080)"], 
    index=1
)
if resolution_option == "HD (1280x720)":
    resolution = (1280, 720)
else:
    resolution = (1920, 1080)

# --- Khu vực tải file lên ---
uploaded_images = st.file_uploader(
    "Chọn các file ảnh (PNG, JPG):", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

uploaded_audio = st.file_uploader(
    "Chọn file nhạc nền (Tùy chọn - MP3, WAV):", 
    type=["mp3", "wav"]
)

# --- Xử lý khi bấm nút ---
if st.button("🚀 Bắt đầu tạo video"):
    if not uploaded_images:
        st.error("Vui lòng tải lên ít nhất một ảnh!")
    else:
        with st.spinner("Đang xử lý video, vui lòng đợi trong giây lát..."):
            temp_image_paths = []
            
            # Lưu tạm các ảnh người dùng tải lên vào thư mục làm việc
            for i, img_file in enumerate(uploaded_images):
                temp_path = f"temp_img_{i}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(img_file.getbuffer())
                temp_image_paths.append(temp_path)
            
            # Lưu file nhạc tạm nếu có
            audio_path = None
            if uploaded_audio:
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

            # Tạo video bằng MoviePy
            clips = []
            for img_path in temp_image_paths:
                clip = (ImageClip(img_path)
                        .set_duration(duration_per_image)
                        .resize(newsize=resolution)
                        .crossfadein(0.5))
                clips.append(clip)
            
            final_video = concatenate_videoclips(clips, method="compose")
            
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                if audio.duration > final_video.duration:
                    audio = audio.subclip(0, final_video.duration)
                final_video = final_video.set_audio(audio)

            output_filename = "output_video.mp4"
            final_video.write_videofile(
                output_filename,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4
            )
            
            st.success("Tạo video thành công!")
            
            # Hiển thị video và nút tải xuống
            st.video(output_filename)
            with open(output_filename, "rb") as file:
                st.download_button(
                    label="📥 Tải xuống Video",
                    data=file,
                    file_name="video_cua_toi.mp4",
                    mime="video/mp4"
                )
            
            # Dọn dẹp file tạm
            for path in temp_image_paths:
                if os.path.exists(path):
                    os.remove(path)
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)