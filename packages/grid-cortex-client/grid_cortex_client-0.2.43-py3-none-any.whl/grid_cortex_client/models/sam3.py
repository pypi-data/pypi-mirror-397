"""
SAM-3 promptable segmentation client wrapper.

This wrapper targets the Ray Serve SAM-3 deployment and mirrors the simplified
payload structure documented in ``ray-serve/models/segmentation/sam3/sam3.py``.

The API supports exactly ONE prompt type per request:
- Text prompts: ``text="cat"``
- Point prompts: ``points=[[x, y], ...], labels=[1, 0, ...]``
- Box prompts: ``boxes=[[x0, y0, x1, y1], ...], labels=[1, 0, ...]``

Images may be supplied as file paths, URLs, PIL Images, or numpy arrays.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np
from PIL import Image

from ..preprocessing import image_to_bytes, load_image
from .base_model import BaseModel


class SAM3(BaseModel):
    """Prompt-based segmentation powered by SAM-3.

    Supports three prompt types (exactly one per request):
    - Text: ``text="cat"``
    - Points: ``points=[[x, y], ...], labels=[1, 0, ...]``
    - Boxes: ``boxes=[[x0, y0, x1, y1], ...], labels=[1, 0, ...]``

    Preferred usage
    ---------------
    ```pycon
    >>> # Text prompt
    >>> mask = CortexClient().run("sam3", image_input=img, text="cat")
    
    >>> # Point prompts
    >>> mask = CortexClient().run(
    ...     "sam3", image_input=img,
    ...     points=[[320, 240]], labels=[1]
    ... )
    
    >>> # Box prompts
    >>> mask = CortexClient().run(
    ...     "sam3", image_input=img,
    ...     boxes=[[100, 120, 520, 480]], labels=[1]
    ... )
    ```
    """

    name: str = "sam3"
    model_id: str = "sam3"

    @staticmethod
    def _validate_points(points: Iterable[Iterable[float]]) -> List[List[float]]:
        """Validate and normalize point coordinates."""
        pts: List[List[float]] = []
        for entry in points:
            if len(entry) != 2:
                raise ValueError(f"Point prompts must be [x, y]; received {entry!r}")
            pts.append([float(entry[0]), float(entry[1])])
        return pts

    @staticmethod
    def _validate_labels(labels: Iterable[int], count: int) -> List[int]:
        """Validate labels match count."""
        lbls = [int(v) for v in labels]
        if len(lbls) != count:
            raise ValueError(f"'labels' length {len(lbls)} must match prompt count {count}")
        return lbls

    @staticmethod
    def _validate_boxes(boxes: Iterable[Iterable[float]]) -> List[List[float]]:
        """Validate and normalize box coordinates."""
        bbox: List[List[float]] = []
        for entry in boxes:
            if len(entry) != 4:
                raise ValueError(f"Each box must be [x0, y0, x1, y1]; received {entry!r}")
            bbox.append([float(v) for v in entry])
        return bbox

    def preprocess(
        self,
        *,
        image_input: Union[str, Image.Image, np.ndarray],
        text: Optional[str] = None,
        points: Optional[Iterable[Iterable[float]]] = None,
        boxes: Optional[Iterable[Iterable[float]]] = None,
        labels: Optional[Iterable[int]] = None,
    ) -> Dict[str, Any]:
        """Encode payload for the SAM-3 endpoint.
        
        Args:
            image_input: RGB image as file path, URL, PIL Image, or numpy array.
            text: Text prompt (exclusive with points/boxes).
            points: List of [x, y] point coordinates (exclusive with text/boxes).
            boxes: List of [x0, y0, x1, y1] box coordinates (exclusive with text/points).
            labels: Required for points/boxes. 1=foreground, 0=background.
        
        Returns:
            Payload dictionary for SAM-3 endpoint.
        
        Raises:
            ValueError: If multiple prompt types provided or labels missing.
        """
        image = load_image(image_input)
        img_bytes = image_to_bytes(image, encoding_format="JPEG")

        # Validate exactly one prompt type
        prompt_count = sum([bool(text), bool(points), bool(boxes)])
        if prompt_count == 0:
            raise ValueError("Provide exactly one of 'text', 'points', or 'boxes'.")
        if prompt_count > 1:
            raise ValueError("Provide only ONE prompt type: 'text', 'points', OR 'boxes' (not multiple).")

        payload: Dict[str, Any] = {"image_input": img_bytes}

        if text:
            payload["text"] = text
        elif points:
            point_list = self._validate_points(points)
            if labels is None:
                raise ValueError("'labels' required when using 'points'")
            payload["points"] = point_list
            payload["labels"] = self._validate_labels(labels, len(point_list))
        else:  # boxes
            box_list = self._validate_boxes(boxes)
            if labels is None:
                raise ValueError("'labels' required when using 'boxes'")
            payload["boxes"] = box_list
            payload["labels"] = self._validate_labels(labels, len(box_list))

        return payload

    def postprocess(self, response_data: Dict[str, Any], **_: Any) -> np.ndarray:
        """Decode PNG mask bytes → numpy uint8 array.
        
        Args:
            response_data: Response dictionary containing 'output' PNG bytes.
        
        Returns:
            Binary mask as numpy array (H, W) with dtype uint8.
            Foreground pixels are 255, background pixels are 0.
        """
        if isinstance(response_data, list):
            if not response_data:
                raise ValueError("SAM-3 response is empty.")
            response_data = response_data[0]

        png_bytes = response_data.get("output")
        if png_bytes is None:
            raise ValueError("'output' field missing in SAM-3 response.")

        import io

        with Image.open(io.BytesIO(png_bytes)) as pil:
            mask = np.array(pil, dtype=np.uint8)
        return mask

    def run(
        self,
        image_input: Union[str, Image.Image, np.ndarray],
        text: Optional[str] = None,
        points: Optional[Iterable[Iterable[float]]] = None,
        boxes: Optional[Iterable[Iterable[float]]] = None,
        labels: Optional[Iterable[int]] = None,
        timeout: Optional[float] = None,
    ) -> np.ndarray:
        """Segment an image with SAM-3 using exactly one prompt type.
        
        Args:
            image_input: RGB image as file path, URL, PIL Image, or numpy array.
            text: Text prompt describing objects to segment (exclusive with points/boxes).
            points: List of [x, y] point coordinates (exclusive with text/boxes).
            boxes: List of [x0, y0, x1, y1] box coordinates (exclusive with text/points).
            labels: Required for points/boxes. 1=foreground, 0=background.
            timeout: Optional HTTP timeout in seconds.
        
        Returns:
            Binary segmentation mask as numpy array (H, W) with dtype uint8.
            Foreground pixels are 255, background pixels are 0.
        
        Raises:
            ValueError: If multiple prompt types provided, labels missing, or invalid inputs.
            RuntimeError: If no HTTP transport is configured.
            Exception: If the HTTP request fails.
        
        Examples:
            >>> from grid_cortex_client import CortexClient, ModelType
            >>> import numpy as np
            >>> from PIL import Image
            >>> client = CortexClient()
            >>> image = np.array(Image.open("cat.jpg"))
            
            >>> # Text prompt
            >>> mask = client.run(ModelType.SAM3, image_input=image, text="cat")
            
            >>> # Point prompts
            >>> mask = client.run(
            ...     ModelType.SAM3, image_input=image,
            ...     points=[[320, 240]], labels=[1]
            ... )
            
            >>> # Box prompts
            >>> mask = client.run(
            ...     ModelType.SAM3, image_input=image,
            ...     boxes=[[100, 120, 520, 480]], labels=[1]
            ... )
        """
        return super().run(
            image_input=image_input,
            text=text,
            points=points,
            boxes=boxes,
            labels=labels,
            timeout=timeout,
        )
