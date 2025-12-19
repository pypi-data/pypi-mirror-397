#version 330

uniform mat3 tile_to_crs;
uniform mat3 crs_to_model;
uniform mat4 model_to_world;
uniform mat4 world_to_clip;

in vec3 vertex_model_coord;
in vec2 vertex_texcoord;

out vec3 fragment_texcoord;

void main() {
  vec3 map_model_coord = crs_to_model * tile_to_crs * vec3(vertex_model_coord.xy, 1.0);
  vec4 world_coord = model_to_world * vec4(map_model_coord.xy / map_model_coord.z, 0.0, 1.0);
  vec4 clip_coord = world_to_clip * world_coord;

  float dist_to_eye = distance(world_coord.xyz, vec3(0.0,0.0,0.0));
  float adjust = 1. / dist_to_eye;

  gl_Position = vec4(clip_coord.xy / clip_coord.w, 0.9999999, 1.0);
  fragment_texcoord = vec3(vertex_texcoord * adjust, adjust);
}
