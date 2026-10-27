shader_type spatial;

// Paredes del bloque: musgo arriba y capas de tierra que ondulan.
// escala_vertical = escala_altura * multiplicador_altura (lo fija terreno.gd).
uniform float escala_vertical = 60.0;
uniform float grosor_pasto = 1.2;

varying float superficie;
varying float posicion_y;
varying vec2 posicion_xz;
varying float es_fondo;

float azar(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Ruido de valor 2D en [0, 1].
float ruido(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = azar(i);
	float b = azar(i + vec2(1.0, 0.0));
	float c = azar(i + vec2(0.0, 1.0));
	float d = azar(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void vertex() {
	superficie = COLOR.r * escala_vertical;
	posicion_y = VERTEX.y;
	posicion_xz = VERTEX.xz;
	es_fondo = NORMAL.y < -0.5 ? 1.0 : 0.0;
}

void fragment() {
	vec3 c;
	if (es_fondo > 0.5) {
		c = vec3(0.168627, 0.109804, 0.070588); // #2B1C12
	} else if (superficie - posicion_y < grosor_pasto) {
		c = vec3(0.309804, 0.419608, 0.203922); // #4F6B34
	} else {
		float desvio = (ruido(vec2(posicion_xz.x + posicion_xz.y, posicion_y)) - 0.5) * 1.6; // amplitud 0.8
		int capa = int(mod(floor((posicion_y + desvio) / 4.0), 4.0));
		if (capa == 0) {
			c = vec3(0.419608, 0.266667, 0.160784); // #6B4429
		} else if (capa == 1) {
			c = vec3(0.356863, 0.227451, 0.141176); // #5B3A24
		} else if (capa == 2) {
			c = vec3(0.478431, 0.321569, 0.2); // #7A5233
		} else {
			c = vec3(0.290196, 0.184314, 0.113725); // #4A2F1D
		}
	}
	ALBEDO = c;
	ROUGHNESS = 1.0;
}
