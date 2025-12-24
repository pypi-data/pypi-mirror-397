#version 330
uniform mat4 model_to_clip;
uniform mat3 model_to_texture;

in vec3 vertex_model_coord;
in vec2 vertex_texcoord;

out vec2 fragment_texcoord;

void main() {
  vec3 texcoord_homo = model_to_texture * vec3(vertex_texcoord.xy, 1.0);
  fragment_texcoord = texcoord_homo.xy / texcoord_homo.z;
  vec4 clip_coord = model_to_clip * vec4(vertex_model_coord, 1.0);
  gl_Position = vec4(clip_coord.xyz / clip_coord.w, 1.0);
}
