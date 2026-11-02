shader_type canvas_item;
// Fondo de las páginas 2D: curvas de nivel de un terreno que la IA "sueña" y se
// deforma despacio. Una de cada cinco curvas es maestra, como en un mapa topográfico.
#include "res://fondo.gdshaderinc"

const float CURVAS = 14.0;       // curvas en todo el rango de altura
const float VELOCIDAD = 0.017;   // ~1 ciclo por minuto

float ruido(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	float a = fract(sin(dot(i, vec2(127.1, 311.7))) * 43758.5453);
	float b = fract(sin(dot(i + vec2(1.0, 0.0), vec2(127.1, 311.7))) * 43758.5453);
	float c = fract(sin(dot(i + vec2(0.0, 1.0), vec2(127.1, 311.7))) * 43758.5453);
	float d = fract(sin(dot(i + vec2(1.0, 1.0), vec2(127.1, 311.7))) * 43758.5453);
	return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

// Altura suave: tres octavas que se desplazan en direcciones distintas.
float altura(vec2 p, float t) {
	float fase = t * VELOCIDAD * TAU;
	float h = ruido(p * 1.6 + vec2(cos(fase), sin(fase)) * 0.6) * 0.6;
	h += ruido(p * 3.1 - vec2(sin(fase), cos(fase)) * 0.4) * 0.3;
	h += ruido(p * 6.3 + vec2(fase * 0.05, 0.0)) * 0.1;
	return h;
}

void fragment() {
	vec2 uv = vec2(UV.x, 1.0 - UV.y);
	float aspecto = SCREEN_PIXEL_SIZE.y / SCREEN_PIXEL_SIZE.x;
	vec2 p = vec2(uv.x * aspecto, uv.y) * 1.4;

	float nivel = altura(p, TIME) * CURVAS;
	// Distancia a la curva más cercana medida en píxeles: líneas de ~1 px a cualquier resolución.
	float ancho = fwidth(nivel);
	float dist = abs(fract(nivel - 0.5) - 0.5) / max(ancho, 1e-4);
	float maestra = step(abs(mod(round(nivel), 5.0)), 0.5);
	float linea = 1.0 - smoothstep(0.5 + maestra * 0.5, 1.5 + maestra * 0.5, dist);

	float fuerza = mix(0.08, 0.16, maestra) * mix(0.35, 1.0, uv.y);
	COLOR.rgb = degradado_fondo(uv) + FONDO_PUNTO * linea * fuerza;
}
