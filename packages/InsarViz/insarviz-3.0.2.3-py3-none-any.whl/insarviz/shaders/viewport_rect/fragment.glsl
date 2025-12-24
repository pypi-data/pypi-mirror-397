#version 330
uniform vec4 rect_color;

out vec4 frag_color;

void main() {
  frag_color = rect_color; 
}
