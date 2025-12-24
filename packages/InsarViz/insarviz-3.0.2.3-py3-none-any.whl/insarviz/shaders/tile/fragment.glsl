#version 330

uniform sampler2D tile_image;

in vec3 fragment_texcoord;

out vec4 frag_color;

void main() {
  vec2 tex_coord = fragment_texcoord.xy / fragment_texcoord.z;
  vec4 color = texture(tile_image, tex_coord);
  frag_color = vec4(color.xyz,1.0);
}
