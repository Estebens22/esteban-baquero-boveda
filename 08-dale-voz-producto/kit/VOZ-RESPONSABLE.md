# Voz responsable — la guía corta

Darle voz a un producto es poderoso y fácil de usar mal. Cuatro reglas que el kit
asume (la compuerta de `sintetizar()` aplica la primera):

1. **Consentimiento antes de clonar.** Nunca uses la voz de una persona real —
   clonada o imitada — sin su permiso explícito. En el kit, cualquier voz que no
   sea genérica (`neutral`) exige `consentimiento=True`; si no, la síntesis se
   bloquea. Eso es a propósito.

2. **Etiqueta lo sintético.** Si un usuario puede confundir la voz con una
   persona real, avísale que es generada. Una voz que miente sobre lo que es,
   engaña.

3. **El audio es dato personal.** La voz identifica a una persona. Trata las
   grabaciones como datos sensibles: minimiza lo que guardas, cifra en reposo,
   bórralo cuando ya no lo necesites, y di para qué lo usas.

4. **Nada de suplantación ni fraude.** No generes voz para hacerte pasar por
   alguien, burlar verificación por voz o manipular. Si tu caso de uso roza eso,
   no lo construyas.

Estas reglas no frenan el producto: lo hacen confiable. Un sistema de voz en el
que la gente confía vale más que uno que asusta.
