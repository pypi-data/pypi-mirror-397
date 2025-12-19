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
import numpy as np
from mediapipe.framework.formats import landmark_pb2


MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red

# Visualization parameters
row_size = 50  # pixels
left_margin = 24  # pixels
text_color = (0, 0, 0)  # black
fps_avg_frame_count = 10

# Label box parameters
label_font_size = 1
label_thickness = 2


class AiUtil(object):
    @staticmethod
    def draw_boundingbox(
        image,
        detection_result,
        cpc
    ) -> np.ndarray:
        """Draws bounding boxes on the input image and return it.
        Args:
            image: The input RGB image.
            detection_result: The list of all "Detection" entities to be visualized.
        Returns:
            Image with bounding boxes.
        """
        category_names = []
        coordinates_list = []  # To store the center coordinates
        for detection in detection_result.detections:
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = bbox.origin_x, bbox.origin_y
            end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
            cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            category_names.append(category_name)
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x,
                            MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)
            
            # Draw center point coordinates
            if cpc == True:
                center_x = int(bbox.origin_x + bbox.width / 2)
                center_y = int(bbox.origin_y + bbox.height / 2)
                center_point = (center_x, center_y)
                coordinates_list.append(center_point)
                cv2.circle(image, center_point, 5, TEXT_COLOR, -1)
                
                coordinates_text = f"({center_point[0]}, {center_point[1]})"
                display_text = f"{coordinates_text}"
                text_position = (center_point[0] + 10, center_point[1] - 10)
                cv2.putText(image, display_text, text_position, cv2.FONT_HERSHEY_PLAIN, 
                            FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

        return (image, category_names, coordinates_list)  # But returns only the last detection
    
    @staticmethod
    def get_handlandmarks(current_frame, detection_result_list):
        category_name = None
        hand_landmarks_proto = []

        for hand_index, hand_landmarks in enumerate(
            detection_result_list.hand_landmarks):
            # Calculate the bounding box of the hand
            x_min = min([landmark.x for landmark in hand_landmarks])
            y_min = min([landmark.y for landmark in hand_landmarks])
            y_max = max([landmark.y for landmark in hand_landmarks])

            # Convert normalized coordinates to pixel values
            frame_height, frame_width = current_frame.shape[:2]
            x_min_px = int(x_min * frame_width)
            y_min_px = int(y_min * frame_height)
            y_max_px = int(y_max * frame_height)

            # Get gesture classification results
            if detection_result_list.gestures:
                gesture = detection_result_list.gestures[hand_index]
                category_name = gesture[0].category_name
                score = round(gesture[0].score, 2)
                result_text = f'{category_name} ({score})'

                # Compute text size
                text_size = \
                cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX, label_font_size,
                                label_thickness)[0]
                text_width, text_height = text_size

                # Calculate text position (above the hand)
                text_x = x_min_px
                text_y = y_min_px - 10  # Adjust this value as needed

                # Make sure the text is within the frame boundaries
                if text_y < 0:
                    text_y = y_max_px + text_height

                # Draw the text
                cv2.putText(current_frame, result_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_DUPLEX, label_font_size,
                            TEXT_COLOR, label_thickness, cv2.LINE_AA)

                # Draw hand landmarks on the frame
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(
                        x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
                ])
                
        return (hand_landmarks_proto, category_name)