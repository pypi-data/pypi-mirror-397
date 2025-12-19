from common_image_tools import OpencvBackendMode, VideoSource


def main():
    raw_source = "rtsp://admin:admin@192.168.1.47:554/live/ch0"
    # raw_source = "videos/test1.mp4"
    # raw_source = 0
    source = VideoSource(
        raw_source,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
        target_frame_width=640,
        target_frame_height=360,
        target_fps=7,
    )

    print(source.parsed_source)


if __name__ == "__main__":
    main()
