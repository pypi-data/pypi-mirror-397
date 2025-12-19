#version 330

uniform mat4 image_to_world;
uniform vec4 profile_color;
uniform mat4 model_to_image;
uniform float selected_band_position;
uniform float selected_band_width;
uniform float focus_position;
uniform float focus_width;

in float height;
in float zscale;
in vec2 image_derivs_homo;
in vec2 model_coords_homo;

out vec4 color;

vec3 hsv2rgb(vec3 rgb);

void main() {
  vec2 image_derivs = image_derivs_homo / zscale;
  vec3 image_normal = vec3(-image_derivs, -1);
  vec3 normal = normalize((image_to_world * vec4(image_normal, 0.0)).xyz);
  vec3 light_direction = normalize(vec3(-0.5, -0.5, -1.0));
  float specular = 0.1*clamp(dot(normal, -light_direction),0.0,1.0);

  vec2 model_coords = model_coords_homo / zscale;
  vec2 model_coords_sq = model_coords * model_coords;
  float alpha = model_coords_sq.x > 1 || model_coords_sq.y > 1 ? 0.0 : 1.0;

  if(alpha < 0.5) {
    discard;
  }
  vec4 image_coords_homo = model_to_image * vec4(model_coords, 0, 1);
  vec2 image_coords = image_coords_homo.xy / image_coords_homo.w;
  vec2 hv = (1+image_coords.xy)*0.5;
  vec2 hue_sat =
    abs(image_coords.y - selected_band_position) < selected_band_width
    ? vec2(0.25, 1)
    : abs(image_coords.x - focus_position) < focus_width
    ? vec2(0.75, 1)
    : vec2((4+4*hv.x)/12, 0.5);

  vec3 color_rgb = hsv2rgb(vec3(hue_sat, 0.3+0.6*hv.y+specular));
  color = vec4(color_rgb.xyz, alpha);
}
