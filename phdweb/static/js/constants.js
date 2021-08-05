const AUTO_RECONNECT_DELAY = 5000;
const CLIENT_ID = Date.now()
const PHD2_EVENTS = [
  {
    "event": "StartCalibration",
    "label": "Start Calibration"
  },
  {
    "event": "Calibrating",
    "label": "Calibrating"
  },
  {
    "event": "CalibrationDataFlipped",
    "label": "Calibration Data Flipped"
  },
  {
    "event": "CalibrationComplete",
    "label": "Done Calibrating"
  },
  {
    "event": "CalibratingFailed",
    "label": "Calibrating Failed"
  },
  {
    "event": "StarSelected",
    "label": "Star Selected"
  },
  {
    "event": "StartGuiding",
    "label": "Start Guiding"
  },
  {
    "event": "LockPositionShiftLimitReached",
    "label": "Lock Position Shift Limit"
  },
  {
    "event": "LoopingExposures",
    "label": "Looping Exposures"
  },
  {
    "event": "LoopingExposuresStopped",
    "label": "Looping Exposures Stopped"
  },
  {
    "event": "SettleBegin",
    "label": "Settle Begin"
  },
  {
    "event": "Settling",
    "label": "Settling"
  },
  {
    "event": "SettleDone",
    "label": "Settle Done"
  },
  {
    "event": "StarLost",
    "label": "Star Lost"
  },
  {
    "event": "GuidingStopped",
    "label": "Guiding Stopped"
  },
  {
    "event": "GuideStep",
    "label": "Guiding"
  },
  {
    "event": "GuidingDithered",
    "label": "Guiding Dithered"
  },
  {
    "event": "LockPositionLost",
    "label": "Lock Position Lost"
  },
  {
    "event": "GuideParamChange",
    "label": "Guide Parameter Change"
  },
  {
    "event": "ConfigurationChange",
    "label": "Configuration Change"
  },
  {
    "event": "Alert",
    "label": "Alert"
  },
  {
    "event": "Paused",
    "label": "Paused"
  },
  {
    "event": "Resumed",
    "label": "Resumed"
  },
]
const CARD_DATA = [
  {
    "header": "Connection",
    "id": "connection",
    "class": "card-green",
    "body": [
      {
        "event": "get_current_equipment",
        "name": "camera__connected",
        "label": "Camera Name",
        "hint": ""
      },
      {
        "event": "get_current_equipment",
        "name": "camera__connected",
        "label": "Camera Connected",
        "hint": ""
      }
    ]
  },
  {
    "header": "Cooler",
    "id": "cooler",
    "class": "card-blue",
    "body": [
      {
        "event": "get_cooler_status",
        "name": "coolerOn",
        "label": "Cooler On?",
        "hint": ""
      },
    ]
  },
  {
    "header": "Errors",
    "id": "errors",
    "class": "card-red",
    "body": [
      {
        "event": "error",
        "name": "message",
        "label": "Errors",
        "hint": ""
      }
    ]
  },
  {
    "header": "Status",
    "id": "status",
    "body": [
      {
        "event": "get_current_equipment",
        "name": "camera__name",
        "label": "Camera Name",
        "hint": ""
      },
      {
        "event": "get_current_equipment",
        "name": "camera__connected",
        "label": "Camera Connected",
        "hint": ""
      },
      {
        "event": "get_cooler_status",
        "name": "temperature",
        "label": "Sensor Temperature",
        "hint": ""
      },
      {
        "event": "get_cooler_status",
        "name": "coolerOn",
        "label": "Cooler On",
        "hint": ""
      },
      {
        "event": "get_cooler_status",
        "name": "setpoint",
        "label": "Cooler Setpoint",
        "hint": ""
      },
      {
        "event": "get_cooler_status",
        "name": "power",
        "label": "Cooler Power",
        "hint": ""
      },
    ]
  },
  {
    "header": "Guiding",
    "id": "guiding",
    "body": [
      {
        "event": "GuideStep",
        "name": "Frame",
        "label": "Frame",
        "hint": "The frame number; starts at 1 each time guiding starts",
      },
      {
        "event": "GuideStep",
        "name": "Time",
        "label": "Started X Seconds Ago",
        "hint": "the time in seconds, including fractional seconds, since guiding started",
      },
      {
        "event": "GuideStep",
        "name": "Mount",
        "label": "Mount",
        "hint": "the name of the mount",
      },
      {
        "event": "GuideStep",
        "name": "dx",
        "label": "X Offset",
        "hint": "the X-offset in pixels",
      },
      {
        "event": "GuideStep",
        "name": "dy",
        "label": "Y Offset",
        "hint": "the Y-offset in pixels",
      },
      {
        "event": "GuideStep",
        "name": "RADistanceRaw",
        "label": "RA Offset Distance ",
        "hint": "the RA distance in pixels of the guide offset vector",
      },
      {
        "event": "GuideStep",
        "name": "DECDistanceRaw",
        "label": "Dec Offset Distance",
        "hint": "the Dec distance in pixels of the guide offset vector",
      },
      {
        "event": "GuideStep",
        "name": "RADistanceGuide",
        "label": "RA Guide Distance",
        "hint": "the guide algorithm-modified RA distance in pixels of the guide offset vector",
      },
      {
        "event": "GuideStep",
        "name": "DECDistanceGuide",
        "label": "Dec Guide Distance",
        "hint": "the guide algorithm-modified Dec distance in pixels of the guide offset vector",
      },
      {
        "event": "GuideStep",
        "name": "RADuration",
        "label": "RA Pulse Duration",
        "hint": "the RA guide pulse duration in milliseconds",
      },
      {
        "event": "GuideStep",
        "name": "DECDuration",
        "label": "Dec Pulse Duration",
        "hint": "the Dec guide pulse duration in milliseconds",
      },
      {
        "event": "GuideStep",
        "name": "RADirection",
        "label": "RA Direction",
        "hint": "\"East\" or \"West\"",
      },
      {
        "event": "GuideStep",
        "name": "DECDirection",
        "label": "Dec Direction",
        "hint": "\"North\" or \"South\"",
      },
      {
        "event": "GuideStep",
        "name": "StarMass",
        "label": "Star Mass",
        "hint": "the Star Mass value of the guide star",
      },
      {
        "event": "GuideStep",
        "name": "SNR",
        "label": "SNR",
        "hint": "the computed Signal-to-noise ratio of the guide star",
      },
      {
        "event": "GuideStep",
        "name": "HFD",
        "label": "Half-Flux Diameter",
        "hint": "the guide star half-flux diameter (HFD) in pixels",
      },
      {
        "event": "GuideStep",
        "name": "AvgDist",
        "label": "Avg Distance",
        "hint": "a smoothed average of the guide distance in pixels (equivalent to value returned by socket server MSG_REQDIST)",
      },
      {
        "event": "GuideStep",
        "name": "ErrorCode",
        "label": "Error Code",
        "hint": "the star finder error code",
      },
    ]
  },
  {
    "header": "Calibration",
    "id": "calibration",
    "body": [
      {
        "event": "Calibrating",
        "name": "Mount",
        "label": "Mount",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "Calibrating",
        "name": "dir",
        "label": "Phase",
        "hint": "calibration direction (phase)",
      },
      {
        "event": "Calibrating",
        "name": "dist",
        "label": "Distance from Start (DS)",
        "hint": "distance from starting location",
      },
      {
        "event": "Calibrating",
        "name": "dx",
        "label": "X Offset DS",
        "hint": "x offset from starting position",
      },
      {
        "event": "Calibrating",
        "name": "dy",
        "label": "Y Offset DS",
        "hint": "y offset from starting position",
      },
      {
        "event": "Calibrating",
        "name": "pos",
        "label": "X & Y Star Coodinates",
        "hint": "star coordinates in pixels",
      },
      {
        "event": "Calibrating",
        "name": "step",
        "label": "Step #",
        "hint": "step number",
      },
      {
        "event": "Calibrating",
        "name": "State",
        "label": "State",
        "hint": "calibration status message",
      },
    ]
  },
  {
    "header": "Star Lost",
    "id": "starLost",
    "body": [
      {
        "event": "StarLost",
        "name": "Frame",
        "label": "Frame",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "Time",
        "label": "Time",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "StarMass",
        "label": "Star Mass",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "SNR",
        "label": "SNR",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "HFD",
        "label": "HFD",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "AvgDist",
        "label": "Avg Distance",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "ErrorCode",
        "label": "Error Code",
        "hint": "name of the mount that was calibrated",
      },
      {
        "event": "StarLost",
        "name": "Status",
        "label": "Status",
        "hint": "name of the mount that was calibrated",
      }
    ]
  }
]
