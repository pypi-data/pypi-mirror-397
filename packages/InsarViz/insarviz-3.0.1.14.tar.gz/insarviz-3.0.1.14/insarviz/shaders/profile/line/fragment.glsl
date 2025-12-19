#version 330

in float line_type;

out vec4 color;

void main() {
  float lightness = mix(0.9, 0.4, line_type);
  color = vec4(vec3(lightness),1.0);
}
