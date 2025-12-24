#version 330
uniform sampler2D image;
uniform sampler2D ref_image;
uniform mat2 value_to_elevation;

uniform mat3 image_to_geo;

float geo_height(vec3 geo_coords);

float uv_height(vec2 uv) {
  return geo_height(image_to_geo * vec3(uv, 1));
}

vec4 getHeightInfo(vec2 uv) {
  float height = uv_height(uv);
  float height_right = uv_height(uv + vec2(0.005, 0));
  float height_up = uv_height(uv + vec2(0, 0.005));

  return vec4(height, (height_right-height)/0.005, (height_up-height)/0.005, 1.0);
  // vec4 raw_data = texture(image, uv);
  // vec4 ref_data = texture(ref_image, uv);
  // raw_data.xyz -= ref_data.xyz * ref_data.w;

  // float height = (value_to_elevation * vec2(raw_data.x, 1.0)).x;
  // float dx = (value_to_elevation * vec2(raw_data.y, 0.0)).x;
  // float dy = (value_to_elevation * vec2(raw_data.z, 0.0)).x;
  // return vec4(height, dx, dy, raw_data.w);
}
