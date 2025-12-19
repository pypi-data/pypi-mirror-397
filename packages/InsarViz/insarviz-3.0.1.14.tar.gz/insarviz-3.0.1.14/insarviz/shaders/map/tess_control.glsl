#version 410 core

layout (vertices = 3) out;

uniform mat4 world_to_clip;
uniform mat4 model_to_world;
uniform mat3 texture_to_image;

in vec3 VS_world_coord[];
in vec2 VS_tex_coord[];

out vec3 TCS_world_coord[];
out vec2 TCS_image_coord[];

vec3 to_clip(vec3 p) {
   vec4 clip_coord = world_to_clip * vec4(p, 1.0);
   return clip_coord.xyz / clip_coord.w;
}

void main() {
   vec3 p0 = to_clip(VS_world_coord[0]);
   vec3 p1 = to_clip(VS_world_coord[1]);
   vec3 p2 = to_clip(VS_world_coord[2]);

   float d0 = distance(p1.xy, p2.xy);
   float d1 = distance(p0.xy, p2.xy);
   float d2 = distance(p0.xy, p1.xy);

   if(   p0.z < -1.0 || p0.z > 1.0
      || p1.z < -1.0 || p1.z > 1.0
      || p2.z < -1.0 || p2.z > 1.0) {
     gl_TessLevelOuter[0] = 0.0;
     gl_TessLevelOuter[1] = 0.0;
     gl_TessLevelOuter[2] = 0.0;
     gl_TessLevelInner[0] = 0.0;
   }
   else {
     // adapt tesselation depending on the screen size
     // gl_TessLevelOuter[0] = 100.0 * d0;
     // gl_TessLevelOuter[1] = 100.0 * d1;
     // gl_TessLevelOuter[2] = 100.0 * d2;
     // gl_TessLevelInner[0] = 100.0 * max(d0, max(d1, d2));
     gl_TessLevelOuter[0] = 100.0;
     gl_TessLevelOuter[1] = 100.0;
     gl_TessLevelOuter[2] = 100.0;
     gl_TessLevelInner[0] = 100.0;
   }

   vec3 image_coord = texture_to_image * vec3(VS_tex_coord[gl_InvocationID], 1.0);

   TCS_world_coord[gl_InvocationID]   = VS_world_coord[gl_InvocationID];
   TCS_image_coord[gl_InvocationID]   = image_coord.xy;
}
