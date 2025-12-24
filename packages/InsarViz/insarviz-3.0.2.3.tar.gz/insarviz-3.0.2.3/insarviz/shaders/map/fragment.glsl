#version 400

uniform mat4 model_to_world;
uniform mat3 image_to_texture;
uniform float near;
uniform float heightUnits;

uniform mat3 image_to_geo;

in vec3 TES_image_coord;

out vec4 frag_color;

vec4 getHeightInfo(vec2);
vec4 geo_color(vec3);

vec3 rgb2hsv(vec3);
vec3 hsv2rgb(vec3);

void main() {
  vec2 uv = TES_image_coord.xy / TES_image_coord.z;
  vec4 height = getHeightInfo(uv);
  float alpha = height.w <= 0.999 ? 0.0 : 1.0;

  // Compute the normal vector (the cross-product between (1,0,dh/dx) and (0,1,dh/dy))
  vec2 dheight = (image_to_texture * vec3(height.yz * heightUnits, 0.0)).xy;
  vec3 model_normal = vec3(-dheight, -1);
  vec3 normal = normalize((model_to_world * vec4(model_normal, 0.0)).xyz);
  vec3 light_direction = normalize(vec3(0.5, 0.5, 1.0));

  float specular = 0.2*clamp(dot(normal, -light_direction),0.0,1.0);

  vec3 geo_coords_homo = image_to_geo * TES_image_coord;
  vec2 geo_coords = geo_coords_homo.xy / geo_coords_homo.z;
  vec4 overlay_color = geo_color(geo_coords_homo);
  if(overlay_color.w < 0.5)
    discard;

  frag_color = vec4(mix(overlay_color.xyz, vec3(1), specular), overlay_color.w * alpha);
}
