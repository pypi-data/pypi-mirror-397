# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from typing import Dict
from .dao import Tools, ToolConf, AbstractRequest
from .model.crop import SegmentationRequest
from .model.convert import ConvertRequest, Option
from .model import (
    AlignmentRequest,
    DeconvolutionRequest,
    EdofRequest,
    YoloSegdetectRequest,
    RetinalLayerRequest,
)


def _create_template_requests() -> Dict | AbstractRequest:

    # TODO Do we want to have proper concrete types for these requests?
    # We could autogenerate them from the Java classes as we did for the
    # typescript JIT client.

    # We could also move the existing dao concrete types in all the python
    # tools to dao here then import them into each tool.
    # TODO Submit a ticket to do that.

    ret = {}

    # Crop
    request = SegmentationRequest()  # Default values are set in the dataclass
    ret[Tools.CROP] = request

    # Deconvolution
    # We set some defaults here for users to start with.
    request = DeconvolutionRequest()
    request.inputPath = None
    request.stain1 = [0.563, 0.72, 0.406]
    request.stain2 = [0.216, 0.801, 0.558]
    request.stain1Max = 2.0
    request.stain2Max = 1.0
    request.alpha = 1
    request.beta = 0.15
    request.intensityNorm = 240
    request.grayscale = False
    request.stain1ImageOutput = None
    request.stain2ImageOutput = None
    request.normalizedImageOutput = None
    request.imageStackOutput = None

    ret[Tools.DECONVOLUTION] = request

    # TODO Use concrete python class?
    request = YoloSegdetectRequest()
    ret[Tools.YOLO_SEGDETECT] = request

    # TODO Use concrete python class?
    request = AlignmentRequest()
    ret[Tools.ALIGNMENT] = request

    request = EdofRequest(inputFiles=[], outputPath=None)
    request.gradientKernel = 5
    request.imageNoiseFilter = 3
    request.zmapNoiseFilter = 3
    request.lowPass = 2
    request.threads = 2
    request.dryRun = False
    request.outputZmap = None
    request.inputZmap = None
    ret[Tools.EDOF] = request

    request = ConvertRequest()
    request.options = [Option.overwrite]
    #  You may use this string to override the reset of the parameters
    #  and provide all the command line apart from the input image and the
    #  output image as a string. Setting this will negative the other
    #  options. This is useful if you want to provide a command line
    #  which is already known. It is not intended to be part of the web UI
    #  but is useful for the CLI.
    request.cmd = None
    request.uploadDir = (
        None  # StorageKey for the dir to which we will upload the converted file(s)
    )
    request.useGeoJson = True
    # If any of the following patterns are present in out_file, they will
    # be replaced with the indicated metadata value from the input file.
    #
    #    Pattern:    Metadata value:
    #    ---------------------------
    #    %s        series index
    #    %n        series name
    #    %c        channel index
    #    %w        channel name
    #    %z        Z index
    #    %t        T index
    #    %A        acquisition timestamp
    #    %x        row index of the tile
    #    %y        column index of the tile
    #    %m        overall tile index
    #
    # For example: "tile_%x_%y.tiff" for the name of each tiled tiff extracted.
    # If you do not set outfile correctly then BioFormats will not generate the
    # correct images in the directory.
    request.outFile = None
    # This is the value of the [-compression codec] option in BioFormats.
    # Set to compress to a specific format.
    request.compression = None
    # The series which we want to extract for conversion from the
    # input file. Usually used (None) which defaults to (0) to extract the first series.
    request.series = None
    request.map = None
    # [-range start end] option on BioFormats command line.
    request.range = None
    # Set the rectangle to crop from the image.
    # [-crop x,y,w,h] example: request["crop"] = {100,100,400,400}
    # x,y top left corner, w width, h height
    request.crop = None
    # a polygon array of all the regions to crop and use for the converted
    # image example:
    # request["manualRegions"] = [ {
    #         "npoints" : 4,
    #         "xpoints" : [ 0, 0, 100, 100 ],
    #         "ypoints" : [ 0, 100, 100, 0 ]
    #       }, {
    #         "npoints" : 4,
    #         "xpoints" : [ 100, 100, 200, 200 ],
    #         "ypoints" : [ 0, 100, 100, 0 ]
    #       }, {
    #         "npoints" : 4,
    #         "xpoints" : [ 200, 200, 300, 300 ],
    #         "ypoints" : [ 0, 100, 100, 0 ]
    #       } ]
    request.manualRegions = None
    # [-channel channel] option on BioFormats command line.
    request.channel = None
    # [-z Z]
    request.z = None
    # [-timepoint timepoint]
    request.timepoint = None
    # [-option key value]
    request.option = None
    # [-tilex tileSizeX]
    request.tilex = None
    # [-tiley tileSizeY]
    request.tiley = None
    # [-pyramid-scale scale]
    request.pyramidScale = None
    # [-swap dimensionsOrderString]
    request.swap = None
    # [-fill color] 0-255
    request.fill = None
    # [-pyramid-resolutions numResolutionLevels]
    request.pyramidResolutions = None

    ret[Tools.CONVERT] = request

    request = RetinalLayerRequest()
    ret[Tools.RETINAL_LAYER] = request

    return ret


template_request_dict: Dict = _create_template_requests()


def create_template_request(type: ToolConf):
    if type not in template_request_dict:
        raise ValueError(f"No template request for type {type.name}")
    return template_request_dict[type]
