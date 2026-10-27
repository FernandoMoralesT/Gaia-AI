shader_type canvas_item;
#include "res://fondo.gdshaderinc"

void fragment() {
	COLOR.rgb = color_fondo(vec2(UV.x, 1.0 - UV.y), TIME);
}
