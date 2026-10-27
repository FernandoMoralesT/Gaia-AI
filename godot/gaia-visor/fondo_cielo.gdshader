shader_type sky;
#include "res://fondo.gdshaderinc"

void sky() {
	vec2 uv = vec2(atan(EYEDIR.x, EYEDIR.z) / TAU + 0.5, EYEDIR.y * 0.5 + 0.5);
	COLOR = color_fondo(uv, TIME);
}
