#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float tempo;
    float copia;
    float faseVai;
    vec2 anda;
    vec2 emenda;
    vec4 vaiVem;
    vec4 balanco;
    vec4 pisca;
};
layout(binding = 1) uniform sampler2D source;
void main() {
    float k = pisca.x;
    if (pisca.z > 0.0)      // um vai-e-vem lento e um tremor curto por cima
        k += pisca.y * sin(6.2832 * tempo / pisca.z + pisca.w) + 0.3 * pisca.y * sin(6.2832 * tempo / (pisca.z * 0.23) + pisca.w * 2.0);
    fragColor = texture(source, qt_TexCoord0) * qt_Opacity * clamp(k, 0.0, 1.3);
}
