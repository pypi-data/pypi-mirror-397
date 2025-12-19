from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from ..dao import AbstractRequest, StorageKey


class Info(str, Enum):
    COMPOUND = "COMPOUND"
    CROP = "CROP"
    FIND = "FIND"
    HTQUANT = "HTQUANT"
    ALIGNMENT = "ALIGNMENT"
    EDOF = "EDOF"
    KIDNEY_CLASSIFIER = "KIDNEY_CLASSIFIER"
    DECONVOLUTION = "DECONVOLUTION"
    YOLO_SEGDETECT = "YOLO_SEGDETECT"
    RETINAL_LAYER = "RETINAL_LAYER"
    STAIN_ADAPTER = "STAIN_ADAPTER"
    UNKNOWN = "UNKNOWN"
    CONVERT = "CONVERT"


@dataclass
class AlignmentRequest(AbstractRequest):

    info: Optional[str] = Info.ALIGNMENT

    # Inputs
    align: Optional[StorageKey] = None
    reference: Optional[StorageKey] = None
    shg: Optional[StorageKey] = None

    # Outputs
    siftOutput: Optional[StorageKey] = None
    overlayedResult: Optional[StorageKey] = None

    # New parameters
    transform: Optional[bool] = True
    flip: Optional[bool] = True
    downsample: Optional[bool] = False
    max_size: Optional[int] = 9e7
    gamma: Optional[float] = 1.0

    resizedN: Optional[StorageKey] = None
    resizedSF: Optional[StorageKey] = None

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False


@dataclass(kw_only=True)
class EdofRequest(AbstractRequest):

    info: Optional[str] = Info.EDOF

    # Inputs
    inputFiles: List[StorageKey]
    outputPath: StorageKey

    inputZmap: Optional[StorageKey] = None

    # Size of kernel used for computation of image gradients.Must be 1, 3, 5, 7.
    gradientKernel: Optional[int] = 5
    # Size of median filter used to reduce noise in the z-map. Must be 0, 3 or 5
    imageNoiseFilter: Optional[int] = 3
    # Size of median filter used to reduce noise in the z-map. Must be 0, 3 or 5
    zmapNoiseFilter: Optional[int] = 3
    # zmap lowpass filter object size.
    lowPass: Optional[float] = 2.0

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False


@dataclass(kw_only=True)
class DeconvolutionRequest(AbstractRequest):

    info: Optional[str] = Info.DECONVOLUTION

    # Inputs
    inputPath: Optional[StorageKey] = None
    stain1: str | tuple[float, float, float] = "hematoxylin"
    stain2: str | tuple[float, float, float] = "eosin"
    stain1Max: float = 2.0
    stain2Max: float = 1.0
    alpha: int = 1
    beta: float = 0.15
    intensityNorm: int = 240
    grayscale: bool = False
    # Outputs
    stain1ImageOutput: Optional[StorageKey] = None
    stain2ImageOutput: Optional[StorageKey] = None
    normalizedImageOutput: Optional[StorageKey] = None
    imageStackOutput: Optional[StorageKey] = None

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False


@dataclass(kw_only=True)
class YoloSegdetectRequest(AbstractRequest):

    info: Optional[str] = Info.YOLO_SEGDETECT

    # Inputs
    inputPaths: Optional[List[StorageKey]] = None
    outputPath: Optional[StorageKey] = None
    weightsPath: Optional[str] = None
    downsamplingFactor: Optional[int] = 5
    visualize: Optional[bool] = False
    overlapX: Optional[int] = 0
    overlapY: Optional[int] = 0
    confidence: Optional[float] = 0.6
    iouThreshold: Optional[float] = 0.5
    nmsThreshold: Optional[float] = 0.3
    saveSegment: Optional[bool] = False
    level: Optional[int] = 2

    # Set if we want the activity to store the
    # classification to claris to be run.
    db_upsert: Optional[bool] = False

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False


@dataclass
class StainAdapterRequest(AbstractRequest):

    info: Optional[str] = Info.STAIN_ADAPTER

    inputPaths: Optional[List[StorageKey]] = None
    outputPath: Optional[StorageKey] = None
    model: str = (
        "/app/models/GAN-stain-adapter-retinal-python3-10-tf-2-10-lab-2L-E27-batchnorm-bs1.h5"
    )
    patchSize: int = 512
    normMethod: str = None
    channelMode: str = "default"
    normTargetPath: str = None
    saveNormalization: bool = True
    normOnly: bool = False
    mode: str = "lab"

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False


class RetinalModelType(Enum):
    """
    Enum for the different model types used in the retinal layer processing.
    These model files are located in the dockerfile created.
    TODO: put this in a config file
    """

    RESUNET_A_2D = {
        "name": "resunet_a_2d",
        "models": [
            "/app/models/resunet-a-2d-RL-40x.keras",
            "/app/models/resunet-a-2d-RL-20x.keras",
            "/app/models/resunet-a-2d-RL-40x-old.keras",
        ],
    }
    VNET_2D = {"name": "vnet_2d", "models": ["/app/modelsvnet-2d-RL-40x.keras"]}

    def __getitem__(self, key):
        return self.value[key]


@dataclass
class RetinalLayerRequest(AbstractRequest):

    info: Optional[str] = Info.RETINAL_LAYER

    # Inputs
    images: Optional[List[StorageKey]] = None
    predModel: str = field(
        default_factory=lambda: RetinalModelType.RESUNET_A_2D["models"][0]
    )
    model: str = field(default_factory=lambda: RetinalModelType.RESUNET_A_2D["name"])
    step: int = 512
    patchSize: int = 512

    # Outputs
    outputPath: Optional[StorageKey] = None

    # Test parameters local to this repo,
    # not in the json used on the server.
    test: Optional[bool] = False
