shader_type canvas_item;
// Título de tierra con pasto: lee el alfa del texto (SubViewport) y pinta
// tierra por dentro, pasto encima y un contorno oscuro alrededor.

uniform float crecimiento : hint_range(0.0, 1.0) = 1.0;
uniform float grosor_pasto = 18.0;     // px de franja verde dentro de la letra
uniform float alto_brizna = 14.0;      // px que suben las briznas sobre la letra
uniform float grosor_contorno = 5.0;   // px de contorno oscuro
// La misma ViewportTexture del TextureRect (la asigna titulo.gd). Va como uniform porque
// TEXTURE no se puede mandar como argumento a funciones propias.
uniform sampler2D textura : filter_linear;

const vec3 VERDE_CLARO = vec3(0.482, 0.749, 0.227);   // #7BBF3A
const vec3 VERDE_OSCURO = vec3(0.310, 0.541, 0.169);  // #4F8A2B
const vec3 CONTORNO = vec3(0.169, 0.102, 0.063);      // #2B1A10
const vec3 TIERRA = vec3(0.478, 0.290, 0.165);        // #7A4A2A
const vec3 CAPA = vec3(0.369, 0.216, 0.125);          // #5E3720
const vec3 MOTA = vec3(0.627, 0.478, 0.333);          // #A07A55

float hash(float n) {
	return fract(sin(n * 127.1) * 43758.5453);
}

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Ruido de valor suave en [0, 1].
float ruido(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	float a = hash2(i);
	float b = hash2(i + vec2(1.0, 0.0));
	float c = hash2(i + vec2(0.0, 1.0));
	float d = hash2(i + vec2(1.0, 1.0));
	return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float alfa(vec2 uv) {
	return texture(textura, uv).a;
}

bool dentro_en(vec2 uv) {
	return alfa(uv) > 0.5;
}

// True si ningún trazo de letra tapa este punto desde arriba (el pasto
// solo crece donde le da el cielo: no en el piso de los huecos de la "a").
bool cielo_libre(vec2 uv, vec2 px) {
	for (int i = 1; i <= 50; i++) {
		vec2 p = uv - vec2(0.0, float(i) * 4.0 * px.y);
		if (p.y < 0.0) {
			break;
		}
		if (dentro_en(p)) {
			return false;
		}
	}
	return true;
}

// True si la superficie en este punto (fuera, justo encima del borde) es
// casi plana y la letra sigue de lado: en laderas empinadas (lados de la "A")
// y en puntas angostas (la colita de la "a") no hay pasto.
bool plano(vec2 uv, vec2 px) {
	return !dentro_en(uv + vec2(4.0, -5.0) * px)
			&& !dentro_en(uv + vec2(-4.0, -5.0) * px)
			&& (dentro_en(uv + vec2(6.0, 4.0) * px)
				|| dentro_en(uv + vec2(-6.0, 4.0) * px));
}

void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE;
	float h = hash(floor(UV.x / px.x / 3.0));
	bool dentro = dentro_en(UV);
	vec4 color = vec4(0.0);

	if (dentro) {
		// Distancia (px) al borde de arriba y al de abajo de la letra.
		float arriba = 64.0;
		float abajo = 64.0;
		for (int i = 1; i <= 32; i++) {
			float d = float(i) * 2.0;
			if (arriba > 63.0 && !dentro_en(UV - vec2(0.0, d * px.y))) {
				arriba = d;
			}
			if (abajo > 63.0 && !dentro_en(UV + vec2(0.0, d * px.y))) {
				abajo = d;
			}
		}
		float franja = grosor_pasto * (0.7 + 0.3 * h);
		bool expuesto = arriba <= franja
				&& plano(UV - vec2(0.0, arriba * px.y), px)
				&& cielo_libre(UV - vec2(0.0, arriba * px.y), px);
		if (expuesto) {
			color.rgb = mix(VERDE_CLARO, VERDE_OSCURO, arriba / franja);
		} else {
			float n = ruido(UV / px / 18.0);
			vec3 tierra = TIERRA;
			float capa = step(0.5, fract(UV.y / px.y / 22.0 + n * 0.3));
			tierra = mix(tierra, CAPA, capa);
			if (ruido(UV * 90.0) > 0.82) {
				tierra = MOTA;
			}
			color.rgb = tierra;
		}
		// Sombreado en la mitad de abajo de cada letra.
		if (abajo < arriba) {
			color.rgb *= 0.85;
		}
		color.a = 1.0;
	} else {
		// Briznas: la letra está justo debajo y es su borde superior.
		// Todas asoman sobre el contorno (mínimo 35 %) y varían de alto.
		float alto = alto_brizna * crecimiento * (0.35 + 0.65 * h);
		vec2 debajo = UV + vec2(0.0, alto * px.y);
		bool brizna = crecimiento > 0.0 && alto >= 1.0
				&& dentro_en(debajo)
				&& !dentro_en(debajo - vec2(0.0, alto_brizna * px.y));
		if (brizna) {
			// sobre = px entre este punto y el borde de la letra.
			float sobre = alto;
			for (int i = 1; i <= 32; i++) {
				if (float(i) < sobre && dentro_en(UV + vec2(0.0, float(i) * px.y))) {
					sobre = float(i);
				}
			}
			vec2 borde = UV + vec2(0.0, (sobre - 1.0) * px.y);
			brizna = plano(borde, px) && cielo_libre(UV, px);
			// Punta: en el último 40 % de la brizna solo queda la columna
			// central de las 3, así se lee como hoja y no como borde.
			float columna = mod(floor(UV.x / px.x), 3.0);
			if (sobre > alto * 0.6 && columna != 1.0) {
				brizna = false;
			}
		}
		if (brizna) {
			// Cada brizna con su tono, para que se distingan entre sí.
			float tono = hash(floor(UV.x / px.x / 3.0) + 17.0) * 0.45;
			color = vec4(mix(VERDE_CLARO, VERDE_OSCURO, tono), 1.0);
		} else {
			float r = grosor_contorno;
			float maximo = 0.0;
			for (int i = 0; i < 8; i++) {
				float ang = float(i) * 0.785398;
				vec2 o = vec2(cos(ang), sin(ang)) * r * px;
				maximo = max(maximo, alfa(UV + o));
			}
			if (maximo > 0.5) {
				color = vec4(CONTORNO, 1.0);
			}
		}
	}
	COLOR = color;
}
