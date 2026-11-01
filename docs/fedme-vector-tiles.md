# FEDME: prueba técnica de acceso a teselas oficiales

Fuente oficial: https://blog.idee.es/ (IGN/CNIG), Senderos GR, PR y SL.
Teselas: https://vt-fedme.idee.es/vt.senderogr,vt.senderopr,vt.senderosl/{z}/{x}/{y}.pbf
Estilo: https://vt-fedme.idee.es/files/styles/style_gr.json

Este experimento comprueba la disponibilidad y estructura de una tesela.
No descarga el país entero ni considera cada fragmento una ruta completa.

Uso: python3 scripts/inspect-fedme-tiles.py

Antes de importar un catálogo:
1. Revisar atributos reales de la capa y posibles IDs de ruta.
2. Determinar si existen identificadores estables para unir fragmentos.
3. Comprobar cobertura, duplicados, geometría, licencia y atribución.
4. Publicar índice solo después de validar trazados completos.
