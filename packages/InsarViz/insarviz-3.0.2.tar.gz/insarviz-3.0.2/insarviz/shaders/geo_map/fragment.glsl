#version 400

in vec2 VS_geo_coords;

out vec4 frag_color;

vec4 geo_color(vec3 geo_coords);

void main() {
  frag_color = geo_color(vec3(VS_geo_coords, 1));
}
