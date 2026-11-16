#version 440
// A luz que entra pela superfície: feixes em leque a partir de onde o sol bate, cada um acendendo e
// apagando no seu tempo, como acontece quando a água de cima se mexe. Soma luz por cima do que já existe.
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float tempo;
    float largura;
    float altura;
    float forca;
};
void main() {
    vec2 p = qt_TexCoord0 * vec2(largura, altura) - vec2(560.0, -70.0);
    float ang = atan(p.x, p.y);                 // 0 = reto para baixo
    float d = length(p);
    float a = 0.5 + 0.5 * sin(ang * 21.0 + tempo * 0.23);
    float b = 0.5 + 0.5 * sin(ang * 37.0 - tempo * 0.31 + 1.7);
    float c = 0.5 + 0.5 * sin(ang * 9.0 + tempo * 0.13 + 4.0);
    float e = 0.5 + 0.5 * sin(ang * 63.0 + tempo * 0.41 + 2.2);
    float feixe = 1.25 * pow(a * b, 1.5) + 0.55 * pow(c, 3.0) + 0.30 * pow(e * a, 2.0);
    float leque = smoothstep(1.08, 0.2, abs(ang));
    float luz = feixe * leque * exp(-d / 440.0) * forca;
    fragColor = vec4(vec3(0.90, 1.0, 0.93) * luz, 0.0) * qt_Opacity;
}
