# grid_cortex_client/src/grid_cortex_client/models/graspgen.py
"""GraspGen wrapper.

Grasp generation from depth + segmentation + camera intrinsics.

Takes depth image, segmentation mask, camera intrinsics, and auxiliary
arguments to generate grasp poses and confidence scores.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence, Union

import numpy as np
from PIL import Image

from ..preprocessing import load_image, array_to_npy_bytes

from .base_model import BaseModel


class GraspGen(BaseModel):
    """Grasp generation from depth + segmentation (GraspGen).

    Preferred usage
    ---------------
    ```pycon
    >>> grasps, conf = CortexClient().run(
    ...     "graspgen",
    ...     depth_image=depth, seg_image=seg,
    ...     camera_intrinsics=K, aux_args=aux
    ... )
    ```
    """

    name: str = "graspgen"
    model_id: str = "graspgen"

    # ------------------------------------------------------------------
    # BaseModel implementation
    # ------------------------------------------------------------------

    def preprocess(
        self,
        *,
        depth_image: Union[str, Image.Image, np.ndarray, None] = None,
        seg_image: Union[str, Image.Image, np.ndarray, None] = None,
        camera_intrinsics: Union[str, np.ndarray, None] = None,
        point_cloud: Union[str, np.ndarray, Sequence[Sequence[float]], None] = None,
        aux_args: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Prepare JSON payload for GraspGen.

        Args:
            depth_image: Depth image (path/URL/PIL/ndarray).
            seg_image: Segmentation mask (path/URL/PIL/ndarray).
            camera_intrinsics: 3x3 camera intrinsics matrix.
            point_cloud: Optional direct point cloud (path to .npy, ndarray, or list of lists).
            aux_args: Dict with "num_grasps", "gripper_config", "camera_extrinsics".
        """
        # Backward compat: older cortex_client passed the entire kwargs dict as the
        # first positional argument (bound to aux_args in older signatures). If we
        # detect depth/seg/intrinsics keys hiding in aux_args, treat it as that dict.
        if aux_args is not None and isinstance(aux_args, dict):
            possible_input_keys = {
                "depth_image",
                "seg_image",
                "camera_intrinsics",
                "point_cloud",
            }
            if possible_input_keys.intersection(aux_args.keys()):
                input_payload = aux_args
                aux_args = input_payload.get("aux_args")
                depth_image = input_payload.get("depth_image", depth_image)
                seg_image = input_payload.get("seg_image", seg_image)
                camera_intrinsics = input_payload.get(
                    "camera_intrinsics", camera_intrinsics
                )
                point_cloud = input_payload.get("point_cloud", point_cloud)

        if aux_args is None:
            raise ValueError("'aux_args' is required.")

        # Enforce mutual exclusivity: either point cloud OR depth+seg+intrinsics
        has_pc = point_cloud is not None
        has_depth_triplet = any(
            x is not None for x in (depth_image, seg_image, camera_intrinsics)
        )

        if has_pc and has_depth_triplet:
            raise ValueError(
                "Provide either point_cloud or depth_image+seg_image+camera_intrinsics, not both."
            )

        if not has_pc and not all(
            x is not None for x in (depth_image, seg_image, camera_intrinsics)
        ):
            raise ValueError(
                "When point_cloud is not provided, depth_image, seg_image, and camera_intrinsics are all required."
            )

        if has_pc:

            if isinstance(point_cloud, str):
                pc_array = np.load(point_cloud)
            else:
                pc_array = np.asarray(point_cloud)

            if pc_array.ndim != 2 or pc_array.shape[1] != 3:
                raise ValueError("point_cloud must be an (N, 3) array.")

            return {
                "point_cloud": array_to_npy_bytes(pc_array.astype(np.float32)),
                "aux_args": aux_args,
            }

        # Depth + segmentation + intrinsics path (existing behavior)
        if depth_image is None or seg_image is None or camera_intrinsics is None:
            raise ValueError(
                "depth_image, seg_image, and camera_intrinsics are required when point_cloud is not provided."
            )

        if isinstance(depth_image, (str, Image.Image)):
            depth_pil = load_image(depth_image)
            depth_array = np.array(depth_pil)
        else:
            depth_array = np.asarray(depth_image)

        if isinstance(seg_image, (str, Image.Image)):
            seg_pil = load_image(seg_image)
            seg_array = np.array(seg_pil)
        else:
            seg_array = np.asarray(seg_image)

        # Load intrinsics
        if isinstance(camera_intrinsics, str):
            intrinsics = np.load(camera_intrinsics)
        else:
            intrinsics = np.asarray(camera_intrinsics)

        # Encode arrays
        depth_bytes = array_to_npy_bytes(depth_array)
        seg_bytes = array_to_npy_bytes(seg_array)
        intrinsics_bytes = array_to_npy_bytes(intrinsics)

        # Send aux_args as dict (server expects dict, not bytes)
        return {
            "depth_image": depth_bytes,
            "seg_image": seg_bytes,
            "camera_intrinsics": intrinsics_bytes,
            "aux_args": aux_args,  # Send as dict directly
        }

    def postprocess(
        self, response_data: Dict[str, Any], **_: Any
    ) -> Dict[str, Any]:  # noqa: D401
        """Decode grasps and confidence from response."""
        grasps = np.array(response_data["output"])
        conf = np.array(response_data["confidence"])
        return {
            "grasps": grasps,
            "confidence": conf,
            "latency_ms": response_data.get("latency_ms"),
        }

    def run(
        self,
        *,
        aux_args: Dict[str, Any],
        depth_image: Union[str, Image.Image, np.ndarray, None] = None,
        seg_image: Union[str, Image.Image, np.ndarray, None] = None,
        camera_intrinsics: Union[str, np.ndarray, None] = None,
        point_cloud: Union[str, np.ndarray, Sequence[Sequence[float]], None] = None,
        timeout: float | None = None,
    ) -> Dict[str, Any]:
        """Generate grasps using GraspGen.

        Args:
            aux_args: Auxiliary parameters (num_grasps, gripper_config, camera_extrinsics).
            depth_image: Depth image (required if point_cloud is None).
            seg_image: Segmentation mask (required if point_cloud is None).
            camera_intrinsics: 3x3 intrinsics matrix (required if point_cloud is None).
            point_cloud: Optional (N,3) point cloud as array/list/path to .npy. When
                provided, depth/seg/intrinsics are ignored and sent directly.
            timeout (float | None): Optional HTTP timeout.

        Returns:
            Dict with:
                - grasps: Array of 4x4 grasp poses (N, 4, 4)
                - confidence: Array of confidence scores (N,)
                - latency_ms: Optional server-reported latency in milliseconds

        Raises:
            ValueError: If images cannot be loaded or parameters are invalid.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.

        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> K = np.eye(3)
            >>> aux = {"num_grasps": 128, "gripper_config": "single_suction_cup_30mm", "camera_extrinsics": np.eye(4)}
            >>> depth_image = np.load("depth.npy")
            >>> seg_image = np.array(Image.open("seg.png"))
            >>> grasps, conf = client.run(ModelType.GRASPGEN, depth_image=depth_image, seg_image=seg_image, camera_intrinsics=K, aux_args=aux)
            >>> print(f"Generated {len(grasps)} grasps")
        """
        return super().run(
            depth_image=depth_image,
            seg_image=seg_image,
            camera_intrinsics=camera_intrinsics,
            aux_args=aux_args,
            point_cloud=point_cloud,
            timeout=timeout,
        )
