#version 330
in vec3 vertex_model_coord;
in vec2 vertex_texcoord;

uniform mat4 clip_to_map_model;
uniform mat4 model_to_clip;

vec2 clip_to_ground(vec2 clip_coord) {
  vec4 v1_model = clip_to_map_model * vec4(clip_coord, -0.5, 1.0);
  vec4 v2_model = clip_to_map_model * vec4(clip_coord, 0.5, 1.0);
  vec3 v1_cart = v1_model.xyz / v1_model.w;
  vec3 v2_cart = v2_model.xyz / v2_model.w;

  vec3 ray = v2_cart - v1_cart;
  float zMul = -v2_cart.z/ray.z;
  return (v2_cart.xy + zMul * ray.xy);
}

void main() {
  vec2 vertex_ground_coord = clip_to_ground(vertex_model_coord.xy);
  gl_Position = model_to_clip * vec4(vertex_ground_coord, 0.0, 1.0);
}
