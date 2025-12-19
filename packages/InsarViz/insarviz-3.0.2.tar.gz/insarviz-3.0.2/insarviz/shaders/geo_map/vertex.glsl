#version 330

uniform mat4 model_to_clip;
uniform mat3 model_to_geo;

in vec3 vertex_model_coord;

out vec2 VS_geo_coords;

void main() {
  vec4 clip_coords = model_to_clip * vec4(vertex_model_coord, 1.0);
  gl_Position = vec4(clip_coords.xyz / clip_coords.w, 1.0);

  vec3 geo_coords_homo = model_to_geo * vec3(vertex_model_coord.xy, 1);
  VS_geo_coords = geo_coords_homo.xy / geo_coords_homo.z;
}
