import argparse
import time
import cv2
import imutils
from FlowPuser import StreamPusher
from Yolov5Compents import YOLOv5

rtmp_server = 'rtmp://10.16.16.10:1935/video'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--imgpath', type=str, default='0', help="image path or camera index")
    parser.add_argument('--modelpath', type=str, default='../models/yolov5s.onnx', help="onnx filepath")
    parser.add_argument('--confThreshold', default=0.3, type=float, help='class confidence')
    parser.add_argument('--nmsThreshold', default=0.5, type=float, help='nms iou thresh')
    args = parser.parse_args()

    yolov5_detector = YOLOv5(args.modelpath, conf_thres=args.confThreshold, iou_thres=args.nmsThreshold)

    imgpath = args.imgpath
    cap = None
    pusher = None

    try:
        # 处理摄像头 or 视频文件
        if imgpath.isnumeric() and len(imgpath) == 1:
            cap = cv2.VideoCapture(int(imgpath))  # 读取摄像头
        else:
            cap = cv2.VideoCapture(imgpath)  # 读取视频文件

        if not cap.isOpened():
            print(f"Error: Could not open {imgpath}")
            exit()

        pusher = StreamPusher(rtmp_server)

        # 获取摄像头 FPS
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"摄像头 FPS: {fps}")

        fail_count = 0
        MAX_FAILS = 30  # 最多允许 30 帧读取失败

        prev_time = time.time()
        while True:
            success, srcimg = cap.read()
            if not success:
                fail_count += 1
                if fail_count > MAX_FAILS:
                    print("连续30帧无法读取，退出")
                    break
                continue  # 跳过当前帧

            srcimg = imutils.resize(srcimg, width=640)

            # 目标检测
            boxes, scores, class_ids = yolov5_detector.detect(srcimg)

            # 计算 FPS
            cur_time = time.time()
            fps = 1 / (cur_time - prev_time)
            prev_time = cur_time
            print(f"当前 FPS: {fps:.2f}")

            # 画出检测结果
            dstimg = yolov5_detector.draw_detections(srcimg, boxes, scores, class_ids)

            # 推送到 RTMP 服务器
            try:
                pusher.streamPush(dstimg)
            except Exception as e:
                print(f"推流失败: {e}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"程序异常: {e}")
    finally:
        if cap:
            cap.release()
        if pusher:
            pusher.close()
        cv2.destroyAllWindows()
