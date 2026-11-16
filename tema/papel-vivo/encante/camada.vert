#version 440
// Encante: uma camada da cena. Todo o movimento é calculado aqui, na placa de vídeo, a partir do tempo:
// o processador só entrega o relógio. Uma camada pode andar sem parar e se emendar (cardumes, bolhas),
// ir e voltar (brilho da superfície), ondular na correnteza (plantas) e, no .frag, cintilar (luzes).
layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 qt_TexCoord0;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float tempo;      // segundos
    float copia;      // 0 ou 1: qual das duas cópias emendadas
    float faseVai;
    vec2 anda;        // pixels por segundo
    vec2 emenda;      // de quantos em quantos pixels a camada se repete (0 = não anda nesse eixo)
    vec4 vaiVem;      // amplitude x, amplitude y, período x, período y
    vec4 balanco;     // amplitude, período, preso em cima (0 ou 1), fase
    vec4 pisca;       // brilho base, amplitude, período, fase
};
void main() {
    qt_TexCoord0 = qt_MultiTexCoord0;
    vec4 p = qt_Vertex;
    if (balanco.x != 0.0) {
        float peso = mix(1.0, clamp(qt_MultiTexCoord0.y * 1.7, 0.0, 1.0), balanco.z);
        float f = 6.2832 * tempo / balanco.y + balanco.w;
        p.x += balanco.x * peso * (sin(f - p.y * 0.012 + p.x * 0.004) + 0.4 * sin(f * 1.7 + p.x * 0.011));
    }
    if (vaiVem.z > 0.0) p.x += vaiVem.x * sin(6.2832 * tempo / vaiVem.z + faseVai);
    if (vaiVem.w > 0.0) p.y += vaiVem.y * sin(6.2832 * tempo / vaiVem.w + faseVai * 1.7);
    if (emenda.x > 0.0) p.x += mod(tempo * anda.x, emenda.x) - copia * emenda.x;
    if (emenda.y > 0.0) p.y += mod(tempo * anda.y, emenda.y) - copia * emenda.y;
    gl_Position = qt_Matrix * p;
}
