namespace cpp rescuer

struct THRIFT_SMS_FMAN_DATA {
  1: double dbObjectId,
  2: double dbXCoordinate,
  3: double dbYCoordinate,
  // Set true if search count button is pressed
  4: bool isSearchCount,
  // Set true if people found button is pressed
  5: bool isSearchPeople,
  6: bool isSosFman
}

struct THRIFT_MAP_IMAGE {
  // String of file extension, e.g., "jpg", "png", etc
  1: string mapFormat,
  2: binary mapBinary
}

struct THRIFT_SENSOR_DATA {
  1: double Temperature,
  2: double Fire,
  3: double Smoke,
  4: double Humidity,
  5: double Motion
}

struct THRIFT_IPLIMAGE {
  // Necessary information to reconstruct IplImage
  1: i16 width,
  2: i16 height,
  3: i16 nChannels,
  4: i16 widthStep,
  5: i16 depth,
  6: binary imageData
}

struct THRIFT_QIMAGE {
  // Necessary information to reconstruct QtImage
  1: i16 width,
  2: i16 height,
  3: binary imageData
}

service Control {
  // Raspberry Pi reports its position to USN client
  oneway void rescuerPosition(1: THRIFT_SMS_FMAN_DATA sms_fman_data)
  // Raspberry Pi downloads binary of a map image from USN client
  THRIFT_MAP_IMAGE mapImage()
  // Raspberry Pi downloads a map image in a IplImage format from USN client
  THRIFT_IPLIMAGE mapIplImage()
  // Upload an image captured by a camera in a QtImage format to USN client (inefficient)
  oneway void sceneImage(1: double dbObjectId, 2: THRIFT_QIMAGE scene_image)
  // Upload binary of an image captured by a camera to USN client
  bool sceneImageBinary(1: double dbObjectId, 2: THRIFT_MAP_IMAGE scene_image_binary)
  // Retrieve sensor data in a tunnel
  THRIFT_SENSOR_DATA sensorData()
}
