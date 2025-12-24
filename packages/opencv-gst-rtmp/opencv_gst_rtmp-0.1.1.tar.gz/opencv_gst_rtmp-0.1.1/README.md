## What is this?

Push opencv frame to rtmp server using gstreamer.

## Usecases?

Modified opencv frame and push to rtmp server.

## Fundamental?

Read opencv frame from appsrc and convert to flv and push to rtmp server using rtmpsink.

## Test with example:
### Setup environment:
Create virtual environment (Optional):

`python3 -m venv .venv`

Run setup_env.sh

`source setup_env.sh`

Run install

`python3 -m pip install .`

### Run

`python3 examples/main_frame.py` or  `python3 examples/main_stream.py`

Play using ffplay or vlc:

`ffplay rtmp://localhost:1935/live`

### Build

Install wheel:

`python3 -m pip install wheel`

Build:

`python3 setup.py bdist_wheel`

Install:

`python3 -m pip install build/opencv_gst_rtmp-0.1.1-py3-none-any.whl`
