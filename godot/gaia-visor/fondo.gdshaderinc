// Fondo de "espacio latente": degradado índigo con una retícula tenue de puntos.
// uv en [0,1] con y=0 abajo. Lo comparten el cielo 3D y el fondo 2D.
const vec3 FONDO_ABAJO = vec3(0.0392, 0.0706, 0.2078); // Abismo #0A1235
const vec3 FONDO_ARRIBA = vec3(0.2, 0.0980, 0.4196);   // Índigo #33196B
const vec3 FONDO_PUNTO = vec3(0.6627, 0.7137, 0.8784); // Bruma #A9B6E0

vec3 color_fondo(vec2 uv, float t) {
	vec3 base = mix(FONDO_ABAJO, FONDO_ARRIBA, clamp(uv.y, 0.0, 1.0));
	vec2 p = uv + vec2(t * 0.004, 0.0);
	vec2 celda = fract(p / 0.035) - 0.5;
	float punto = 1.0 - smoothstep(0.06 - 0.02, 0.06, length(celda));
	// La retícula se desvanece hacia abajo.
	return base + FONDO_PUNTO * punto * 0.10 * clamp(uv.y, 0.0, 1.0);
}
