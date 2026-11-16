#version 440
// Uma "rua" do Encante: luzes vivas correndo por uma curva, maiores quanto mais perto. Não há imagem:
// cada ponto de luz é calculado aqui, e somado por cima do que já está desenhado.
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float tempo;
    float n;          // quantas luzes (até 24)
    float dura;       // segundos para percorrer a curva
    vec2 origem;      // canto do retângulo desta rua, na cena
    vec2 tamanho;
    vec2 raios;       // raio do brilho no começo e no fim da curva
    vec2 p0; vec2 p1; vec2 p2; vec2 p3;     // a curva (Bézier cúbica), em pixels da cena
};
void main() {
    vec2 px = origem + qt_TexCoord0 * tamanho;
    vec3 soma = vec3(0.0);
    for (int i = 0; i < 24; i++) {
        float fi = float(i);
        if (fi >= n) break;
        float u = fract(fi / n + tempo / dura);
        float v = 1.0 - u;
        vec2 c = v * v * v * p0 + 3.0 * v * v * u * p1 + 3.0 * v * u * u * p2 + u * u * u * p3
               + 6.0 * vec2(sin(fi * 2.4 + tempo * 0.7), cos(fi * 1.7 + tempo * 0.5));
        float r = mix(raios.x, raios.y, u);
        float d2 = dot(px - c, px - c);
        float brilho = sin(u * 3.14159) * (0.65 + 0.35 * sin(fi * 3.1 + tempo * 1.3));
        soma += brilho * (vec3(0.37, 0.89, 0.85) * 0.5 * exp(-d2 / (r * r * 0.5)) + vec3(0.90, 1.0, 0.98) * exp(-d2 / (r * r * 0.02)));
    }
    fragColor = vec4(soma, 0.0) * qt_Opacity;
}
