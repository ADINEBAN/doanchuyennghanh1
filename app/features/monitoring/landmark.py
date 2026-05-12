"""MediaPipe face landmark detection wrapper with head pose estimation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np

from app.shared.core.exceptions import CameraError

LEFT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
RIGHT_EYE_INDICES = (362, 385, 387, 263, 373, 380)
MOUTH_INDICES = (61, 81, 13, 311, 291, 402, 14, 178)

# Landmark indices used for head pose estimation (nose tip, chin, left/right
# eye corners, left/right mouth corners).
POSE_LANDMARK_INDICES = (1, 152, 33, 263, 61, 291)

# Approximate 3-D model points for the six landmarks above (generic face).
_MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose tip
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),   # Right eye right corner
    (-150.0, -150.0, -125.0), # Left mouth corner
    (150.0, -150.0, -125.0),  # Right mouth corner
], dtype=np.float64)


@dataclass
class HeadPose:
    """Estimated head rotation angles in degrees."""
    yaw: float = 0.0    # Quay trái/phải
    pitch: float = 0.0  # Ngẩng lên/cúi xuống
    roll: float = 0.0   # Nghiêng đầu


@dataclass
class FaceFeaturePoints:
    left_eye: list[tuple[float, float]]
    right_eye: list[tuple[float, float]]
    mouth: list[tuple[float, float]]
    head_pose: HeadPose = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.head_pose is None:
            self.head_pose = HeadPose()


@dataclass
class _LandmarkListAdapter:
    landmark: list[Any]


class FaceLandmarkDetector:
    def __init__(self) -> None:
        self._face_mesh: Optional[Any] = None
        self._load_error: Optional[str] = None
        self._backend: str = ""

    def _ensure_face_mesh(self) -> Any:
        if self._face_mesh is not None:
            return self._face_mesh
        if self._load_error is not None:
            raise CameraError(self._load_error)

        try:
            # Import the solutions module directly so runtime Face Mesh use
            # does not depend on the broader tasks package import path.
            from mediapipe.python.solutions import face_mesh as mp_face_mesh
        except Exception as exc:
            solutions_error = exc
        else:
            self._face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._backend = "solutions"
            return self._face_mesh

        try:
            from mediapipe.tasks.python import vision
            from mediapipe.tasks.python.core.base_options import BaseOptions
        except Exception as exc:
            self._load_error = (
                "Could not load MediaPipe Face Mesh. "
                "Check the installed MediaPipe runtime on this machine."
            )
            raise CameraError(self._load_error) from solutions_error or exc

        model_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "models"
            / "face_landmarker.task"
        )
        if not model_path.exists():
            self._load_error = (
                "Missing MediaPipe face landmarker model at "
                f"{model_path}."
            )
            raise CameraError(self._load_error)

        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._face_mesh = vision.FaceLandmarker.create_from_options(options)
        self._backend = "tasks"
        return self._face_mesh

    def detect(self, frame_rgb):
        face_mesh = self._ensure_face_mesh()
        if self._backend == "tasks":
            import mediapipe as mp

            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            result = face_mesh.detect(image)
            if not result.face_landmarks:
                return None
            return _LandmarkListAdapter(landmark=result.face_landmarks[0])

        result = face_mesh.process(frame_rgb)
        if not result.multi_face_landmarks:
            return None
        return result.multi_face_landmarks[0]

    def extract_feature_points(
        self,
        face_landmarks,
        frame_width: int,
        frame_height: int,
    ) -> FaceFeaturePoints:
        head_pose = self._estimate_head_pose(face_landmarks, frame_width, frame_height)
        return FaceFeaturePoints(
            left_eye=self._extract_points(
                face_landmarks,
                LEFT_EYE_INDICES,
                frame_width,
                frame_height,
            ),
            right_eye=self._extract_points(
                face_landmarks,
                RIGHT_EYE_INDICES,
                frame_width,
                frame_height,
            ),
            mouth=self._extract_points(
                face_landmarks,
                MOUTH_INDICES,
                frame_width,
                frame_height,
            ),
            head_pose=head_pose,
        )

    def close(self) -> None:
        if self._face_mesh is not None:
            self._face_mesh.close()
            self._face_mesh = None

    # ------------------------------------------------------------------
    # Head pose estimation using solvePnP
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_head_pose(
        face_landmarks,
        frame_width: int,
        frame_height: int,
    ) -> HeadPose:
        try:
            import cv2
        except ImportError:
            return HeadPose()

        # Build 2-D image points from the six selected landmarks.
        image_points = np.array(
            [
                (
                    face_landmarks.landmark[idx].x * frame_width,
                    face_landmarks.landmark[idx].y * frame_height,
                )
                for idx in POSE_LANDMARK_INDICES
            ],
            dtype=np.float64,
        )

        # Approximate camera intrinsics.
        focal_length = frame_width
        center = (frame_width / 2.0, frame_height / 2.0)
        camera_matrix = np.array(
            [
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vector, _ = cv2.solvePnP(
            _MODEL_POINTS,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return HeadPose()

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        proj_matrix = np.hstack((rotation_matrix, np.zeros((3, 1))))
        euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

        pitch = float(euler_angles[0, 0])
        yaw = float(euler_angles[1, 0])
        roll = float(euler_angles[2, 0])

        return HeadPose(yaw=yaw, pitch=pitch, roll=roll)

    @staticmethod
    def _extract_points(
        face_landmarks,
        indices: tuple[int, ...],
        frame_width: int,
        frame_height: int,
    ) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        for index in indices:
            landmark = face_landmarks.landmark[index]
            points.append((landmark.x * frame_width, landmark.y * frame_height))
        return points
