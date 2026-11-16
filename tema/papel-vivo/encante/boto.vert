#version 440
// O Boto e os botos pequenos. A imagem vem deitada (cauda à esquerda, u = 0; bico à direita, u = 1).
// Aqui ela ondula como golfinho, de cima para baixo e mais na cauda, e é levada pelo caminho:
// modo 0, uma passagem em linha que serpenteia, dentro de um ciclo; modo 1, uma volta larga sem fim.
layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 qt_TexCoord0;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float tempo;
    float modo;
    float amplitude;   // da ondulada, em pixels da imagem
    float batida;      // segundos de cada ondulada
    vec4 ciclo;        // modo 0: duração da volta inteira, começo e duração desta passagem, (livre)
    vec4 a;            // modo 0: de onde (x, y) para onde (x, y) | modo 1: centro (x, y) e raios (x, y)
    vec4 b;            // modo 0: serpenteio (pixels, vezes), escala, lado (1 direita, -1 esquerda) | modo 1: período, atraso, escala
};
void main() {
    qt_TexCoord0 = qt_MultiTexCoord0;
    float u = qt_MultiTexCoord0.x;
    float fase = 6.2832 * tempo / batida;
    vec2 q = qt_Vertex.xy - vec2(330.0, 155.0);                 // o meio do corpo na origem
    q.y += amplitude * pow(1.0 - u, 1.7) * sin(fase - (1.0 - u) * 3.0) + amplitude * 0.10 * u * sin(fase + 1.4);

    vec2 pos; float escala; float lado; float graus; bool some = false;
    if (modo < 0.5) {
        float t = (mod(tempo, ciclo.x) - ciclo.y) / ciclo.z;
        some = t <= 0.0 || t >= 1.0;
        pos = mix(a.xy, a.zw, t) + vec2(0.0, b.x * sin(t * 3.14159 * b.y));
        escala = b.z; lado = b.w;
        graus = -(10.0 + 5.0 * sin(t * 3.14159 * 3.0));
    } else {
        float ang = 6.2832 * tempo / b.x + b.y;
        pos = a.xy + a.zw * vec2(cos(ang), sin(ang)) + vec2(0.0, 4.0 * sin(ang * 5.0));
        escala = b.z;
        lado = clamp(-sin(ang) * 4.0, -1.0, 1.0);               // nas pontas da volta ele vira
        graus = -8.0 * cos(ang);
    }
    q *= vec2(lado * escala, escala);
    float r = radians(graus) * (lado < 0.0 ? -1.0 : 1.0);
    vec2 p = pos + vec2(q.x * cos(r) - q.y * sin(r), q.x * sin(r) + q.y * cos(r));
    if (some) p = vec2(-9000.0, -9000.0);
    gl_Position = qt_Matrix * vec4(p, 0.0, 1.0);
}
