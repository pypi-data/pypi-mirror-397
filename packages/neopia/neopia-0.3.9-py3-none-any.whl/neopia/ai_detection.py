# Part of the RoboticsWare project - https://roboticsware.uz
# Copyright (C) 2022 RoboticsWare (neopia.uz@gmail.com)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import cv2
import speech_recognition as sr
import gtts
import uuid, os, time
import playsound3
from neopia.opencv_camera import Camera
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from neopia.ai_util import AiUtil

mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# For face mesh:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

class FaceMeshDetection(Camera):
    def __init__(self):
        super().__init__()

    def start_detection(self, just_rtn_frame=False):
        rtn_val = False
        _, frame = self._videoInput.read()
        frame = cv2.flip(frame, 1)
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Draw face mesh landmarks on the image.
        if results.multi_face_landmarks:
            annotated_image = frame.copy()
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)
            
            frame = annotated_image 
            rtn_val = True
        
        # Just return frame
        if just_rtn_frame:
            return frame
        else:
            cv2.imshow('Face detection', frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)
            rtn_val = False
    
        return rtn_val

    def __del__(self):
        super().__del__()


class FaceDetection(Camera):
    def __init__(self):
        super().__init__()
        self._face_cascade = cv2.CascadeClassifier(
            os.path.join(os.path.dirname(__file__), 'model', 'haarcascade_frontalface_default.xml'))

    def start_detection(self, just_rtn_frame=False):
        _, frame = self._videoInput.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, 1.1, 5)
        
        # Show rect on faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Just return frame
        if just_rtn_frame:
            return (frame, len(faces))
        else:
            cv2.imshow('Face detection', frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)
    
        return len(faces)

    def __del__(self):
        super().__del__()


class PoseDetection(Camera):
    def __init__(self):
        super().__init__()

    def start_detection(self, just_rtn_frame=False):
        rtn_val = (0, 0)  # Tuple
        success, frame = self._videoInput.read()
        if not success:
            print("Frame is not ready!, Try again.")
            return rtn_val
        frame = cv2.flip(frame, 1) 
        result = pose.process(frame)
        if result.pose_landmarks:
            # Save the coords of nose
            rtn_val = (result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * self._width,
                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * self._height)
        
            #Draw the framework of body onto the processed image and then show it in the preview window
            mp_drawing.draw_landmarks(frame,result.pose_landmarks,mp_pose.POSE_CONNECTIONS)
        else:
            rtn_val = (0, 0)

        # Just return frame
        if just_rtn_frame:
            return (frame, rtn_val)
        else:
            cv2.imshow('Pose detection', frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)
    
        return rtn_val

    def __del__(self):
        super().__del__()


class ObjectDetection(Camera):
    def __init__(self, target_fps=30, center_point_xy = False):
        super().__init__()
        self._detection_result_list = []
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'efficientdet.tflite')
        # Initialize the object detection model
        # model_asset_buffer is from https://github.com/google-ai-edge/mediapipe/issues/4983
        base_options = python.BaseOptions(model_asset_buffer = open(model_path, "rb").read())
        options = vision.ObjectDetectorOptions(base_options=base_options,
                                                running_mode=vision.RunningMode.LIVE_STREAM,
                                                score_threshold=0.5,
                                                result_callback=self._visualize_callback)
        self._detector = vision.ObjectDetector.create_from_options(options)
        self._counter = 0

        self.target_fps = target_fps
        self.prev_time = 0

        self.center_point_xy = center_point_xy

    def _visualize_callback(self, result,
                         output_image: mp.Image, timestamp_ms: int):
        result.timestamp_ms = timestamp_ms
        self._detection_result_list.append(result)

    def start_detection(self, just_rtn_frame=False):
        current_time = time.time()
        # Limiting framerate
        if (current_time - self.prev_time) < 1.0 / self.target_fps:
            return None
        
        rtn_val = None
        _, frame = self._videoInput.read()
        self._counter += 1
        frame = cv2.flip(frame, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run object detection using the model.
        self._detector.detect_async(mp_image, self._counter)
        current_frame = mp_image.numpy_view()
        current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

        if self._detection_result_list:
            vis_image, obj_name, obj_coords = AiUtil.draw_boundingbox(
                current_frame, self._detection_result_list[0], self.center_point_xy)
            rtn_val = (obj_name, obj_coords) 
            self._detection_result_list.clear()
            current_frame = vis_image
        
        # Update the previous time after processing the frame
        self.prev_time = current_time
            
        # Just return frame
        if just_rtn_frame:
            return (current_frame, rtn_val)
        else:
            cv2.imshow('Object detection', current_frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)

        return rtn_val

    def __del__(self):
        super().__del__()


class GestureDetection(Camera):
    def __init__(self, target_fps=30):
        super().__init__()
        self._detection_result_list = []
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'gesture_recognizer.task')
        # Initialize the object detection model
        # model_asset_buffer is from https://github.com/google-ai-edge/mediapipe/issues/4983
        base_options = python.BaseOptions(model_asset_buffer = open(model_path, "rb").read())
        options = vision.GestureRecognizerOptions(base_options=base_options,
                                                running_mode=vision.RunningMode.LIVE_STREAM,
                                                result_callback=self._visualize_callback)
        self._detector = vision.GestureRecognizer.create_from_options(options)

        self.target_fps = target_fps
        self.prev_time = 0

    def _visualize_callback(self, result,
                         output_image: mp.Image, timestamp_ms: int):
        result.timestamp_ms = timestamp_ms
        self._detection_result_list.append(result)

    def start_detection(self, just_rtn_frame=False):
        current_time = time.time()
        # Limiting framerate
        if (current_time - self.prev_time) < 1.0 / self.target_fps:
            return None
        
        rtn_val = None
        success, frame = self._videoInput.read()
        if not success:
            print("Frame is not ready!, Try again.")
            return rtn_val
        frame = cv2.flip(frame, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run object detection using the model.
        self._detector.recognize_async(mp_image, time.time_ns() // 1_000_000)
        current_frame = frame

        if self._detection_result_list:
            hand_landmarks_proto, category_name = AiUtil.get_handlandmarks(current_frame, self._detection_result_list[0])
            rtn_val = category_name
            mp_drawing.draw_landmarks(
                current_frame,
                hand_landmarks_proto,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            self._detection_result_list.clear()
    
        # Update the previous time after processing the frame
        self.prev_time = current_time

        # Just return frame
        if just_rtn_frame:
            return (current_frame, rtn_val)
        else:
            cv2.imshow('Gesture detection', current_frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)
        
        return rtn_val

    def __del__(self):
        super().__del__()        


class QRDetection(Camera):
    def __init__(self):
        super().__init__()
        self._detector = cv2.QRCodeDetector()

    def start_detection(self, just_rtn_frame=False):
        _, frame = self._videoInput.read()
        data, bbox, _ = self._detector.detectAndDecode(frame)

        if bbox is not None:
            bb_pts = bbox.astype(int).reshape(-1, 2)
            num_bb_pts = len(bb_pts)
            for i in range(num_bb_pts):
                cv2.line(frame, tuple(bb_pts[i]), tuple(bb_pts[(i+1) % num_bb_pts]),
                        color=(255, 0, 0), thickness=2)
                cv2.putText(frame, data, (bb_pts[0][0], bb_pts[0][1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)        
                
        # Just return frame
        if just_rtn_frame:
            return (frame, data)
        else:
            cv2.imshow('QR detection', frame)
            if cv2.waitKey(1) == 27:  # ESC pressed
                os._exit(1)
        return data

    def __del__(self):
        super().__del__()


import threading
shared_fname = None
tl = threading.Lock()
def thread_run(lock):
    lock.acquire()
    playsound3.playsound(shared_fname, block=True)
    lock.release()

class Voice(object):
    @staticmethod
    def stt(audioId=0, language='uz-UZ'):
        r = sr.Recognizer()
        mic = sr.Microphone(audioId)
        audio = None
        with mic:
            r.adjust_for_ambient_noise(mic)
            audio = r.listen(mic, 3)  # Timeout in 3 sec
        try:
            result = r.recognize_google(audio, language=language)
        except sr.UnknownValueError:  # The speech is unintelligible
            result = False
        except Exception as error:
            raise error
        return result
    
    @staticmethod
    def tts(text, lang='en'):
        tts = gtts.gTTS(text=text, lang=lang)
        fname = str(uuid.uuid1()) + ".mp3"
        with open(fname, 'wb+') as f:
            tts.write_to_fp(f)
        playsound3.playsound(fname)
        os.remove(fname)

    @staticmethod
    def playsound(fname):
        global shared_fname
        shared_fname = fname
        thread = threading.Thread(target=thread_run, args=(tl,))
        thread.start()