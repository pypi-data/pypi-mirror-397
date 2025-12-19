#version 330

uniform mat4 image_to_world;
uniform mat4 image_to_model;
uniform mat4 world_to_clip;
uniform sampler2D tex;
uniform float diff_scale;
uniform float height_scale;

in vec2 vertex_texture_coords;

out float height;
out float zscale;
out vec2 image_derivs_homo;
out vec2 model_coords_homo;

void main() {
  vec2 texcoords = vertex_texture_coords;

  vec2 bottom_left    = texture(tex, texcoords + vec2(-diff_scale, -diff_scale)).xy;
  vec2 bottom_right   = texture(tex, texcoords + vec2(diff_scale, -diff_scale)).xy;
  vec2 bottom_rright  = texture(tex, texcoords + vec2(2*diff_scale, -diff_scale)).xy;
  vec2 top_left       = texture(tex, texcoords + vec2(-diff_scale, diff_scale)).xy;
  vec2 ttop_left      = texture(tex, texcoords + vec2(-diff_scale, 2*diff_scale)).xy;
  vec2 top_right      = texture(tex, texcoords + vec2(diff_scale, diff_scale)).xy;
  vec2 ttop_right     = texture(tex, texcoords + vec2(diff_scale, 2*diff_scale)).xy;
  vec2 top_rright     = texture(tex, texcoords + vec2(2*diff_scale, diff_scale)).xy;

  vec2 value_integ = bottom_left + top_right - bottom_right - top_left;
  vec2 right_integ = bottom_right + top_rright - bottom_rright - top_right;
  vec2 up_integ = top_left + ttop_right - top_right - ttop_left;
  float height = value_integ.x / value_integ.y;
  float height_right = right_integ.x / right_integ.y;
  float height_up = up_integ.x / up_integ.y;

  float height_scaled = height_scale * height;

  vec4 world_coords = image_to_world * vec4(vertex_texture_coords.xy, height_scaled, 1.0);
  vec3 world_coords_adjusted = world_coords.xyz / world_coords.w;
  zscale = 1/distance(world_coords_adjusted.xyz, vec3(0));

  vec2 dxy = height_scale * vec2(height_right - height, height_up - height) / (2*diff_scale);
  image_derivs_homo = dxy * zscale;

  vec4 model_coords = image_to_model * vec4(vertex_texture_coords.xy, 0, 1);
  vec2 model_coords_2d = model_coords.xy / model_coords.w;
  model_coords_homo = model_coords_2d * zscale;

  vec4 clip_coords = world_to_clip * world_coords;
  gl_Position = vec4(clip_coords.xyz / clip_coords.w, 1.0);
  height = clip_coords.z;
}
