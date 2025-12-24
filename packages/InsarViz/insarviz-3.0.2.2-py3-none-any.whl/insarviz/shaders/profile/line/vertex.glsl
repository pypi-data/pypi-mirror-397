#version 330

uniform mat4 grid_to_clip;

in vec4 grid_coords;

out float line_type;

void main() {
  vec4 clip_coords = grid_to_clip * vec4(grid_coords.xyz, 1.0);

  gl_Position = vec4(clip_coords.xyz / clip_coords.w, 1.0);
  line_type = grid_coords.w;
}
