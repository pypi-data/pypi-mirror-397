#version 330
uniform sampler2D image;
uniform sampler2D reference_image;
uniform mat3 texture_to_image;
uniform mat2 value_to_color;
uniform sampler1D colormap;

in vec2 fragment_texcoord;

out vec4 frag_color;

void main() {
  vec3 img_coord = texture_to_image * vec3(fragment_texcoord, 1.0);
  vec4 value = texture(image, img_coord.xy / img_coord.z);
  vec4 ref_value = texture(reference_image, img_coord.xy / img_coord.z);
  value.xyz -= ref_value.xyz * ref_value.w;
  float alpha = value.w <= 0.999 ? 0.0 : 1.0;
  vec4 color = texture(colormap, (value_to_color * vec2(value.x, 1.0)).x);

  frag_color = vec4(color.xyz, alpha);
}
