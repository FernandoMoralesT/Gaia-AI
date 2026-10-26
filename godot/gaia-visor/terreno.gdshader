shader_type spatial;

// La altura normalizada (0 a 1) llega en el canal rojo del color de vértice.
uniform vec3 color_bajo : source_color = vec3(0.30, 0.50, 0.20);
uniform vec3 color_medio : source_color = vec3(0.45, 0.32, 0.20);
uniform vec3 color_alto : source_color = vec3(0.85, 0.85, 0.82);
uniform float inicio_cafe : hint_range(0.0, 1.0) = 0.35;
uniform float inicio_gris : hint_range(0.0, 1.0) = 0.75;
uniform float transicion : hint_range(0.0, 0.3) = 0.08;

void fragment() {
	float h = COLOR.r;
	vec3 c = mix(color_bajo, color_medio, smoothstep(inicio_cafe - transicion, inicio_cafe + transicion, h));
	c = mix(c, color_alto, smoothstep(inicio_gris - transicion, inicio_gris + transicion, h));
	ALBEDO = c;
	ROUGHNESS = 0.9;
}
