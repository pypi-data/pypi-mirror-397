#version 330

uniform mat4 model_to_world;

in vec3 vertex_model_coord;
in vec2 vertex_texcoord;

out vec3 VS_world_coord;
out vec2 VS_tex_coord;

void main() {
  VS_world_coord = (model_to_world * vec4(vertex_model_coord, 1.0)).xyz;
  VS_tex_coord = vertex_texcoord;
}
