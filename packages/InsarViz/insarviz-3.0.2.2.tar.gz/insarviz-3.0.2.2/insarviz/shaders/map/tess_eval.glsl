#version 410 core

layout (triangles, fractional_even_spacing, ccw) in;

uniform float nodata;
uniform float heightUnits;

uniform mat4 world_to_clip;
uniform mat4 model_to_world;

in vec3 TCS_world_coord[];
in vec2 TCS_image_coord[];

out vec3 TES_image_coord;
out vec2 TES_world_z;

#pragma include "getHeightInfo"

vec4 getHeightInfo(vec2);

vec2 interpolate2D(vec3 bary, vec2 v0, vec2 v1, vec2 v2) {
    return bary.x * v0 + bary.y * v1 + bary.z * v2;
}
vec3 interpolate3D(vec3 bary, vec3 v0, vec3 v1, vec3 v2) {
    return bary.x * v0 + bary.y * v1 + bary.z * v2;
}

void main() {
  vec3 bary = gl_TessCoord;
  vec3 world_coord = interpolate3D(bary, TCS_world_coord[0], TCS_world_coord[1], TCS_world_coord[2]);
  vec2 image_coord = interpolate2D(bary, TCS_image_coord[0], TCS_image_coord[1], TCS_image_coord[2]);

  // The DEM texture contains vector of shape (h, dh/dx, dh/dy), used
  // to compute the height of the vertex and the normal vector at
  // that point
  vec4 data = getHeightInfo(image_coord);

  float height = data.w <= 0.95 ? 0.0 : data.x;
  height = clamp(height, -1.0, 1.0);
  height = height * heightUnits;

  vec4 clip_coord = world_to_clip *
    (vec4(world_coord, 1.0) - model_to_world * vec4(0.0,0.0,height,0.0));
  gl_Position = vec4(clip_coord.xyz / clip_coord.w, 1.0);

  // Compute texture coordinates in homogeneous coordinates w.r.t
  // linear interpolation
  // (https://en.wikipedia.org/wiki/Texture_mapping#Perspective_correctness)
  float dist_to_eye = distance(world_coord.xyz, vec3(0.0,0.0,0.0));
  float adjust = 1. / dist_to_eye;
  TES_image_coord = vec3(image_coord * adjust, adjust);
}
