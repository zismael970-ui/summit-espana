# SUMMIT España — v0.9.1

Aplicación web experimental de senderismo para España, publicada mediante GitHub Pages.

## Funcionalidades
- Mapa OpenStreetMap y OpenTopoMap con Leaflet.
- Búsqueda de lugares mediante Nominatim y consulta de cimas/refugios mediante Overpass.
- Importación/exportación de GPX, longitud y perfil de elevación cuando hay datos.
- GPS experimental con centrado y registro de recorrido.
- Guardado local de rutas y carga de GeoJSON.

## Revisión técnica 0.9.1
- Corrección de sintaxis de la versión anterior preservada.
- Eliminación del texto superpuesto al mapa y diagnóstico de errores de teselas.
- Optimización del perfil de elevación: evita expandir grandes arreglos en Math.min/Math.max.
- Validación básica del tamaño de rutas y visualización de rutas de un único punto.
- Reinicio de recorrido GPS al iniciar una nueva sesión y filtro básico de puntos próximos.
- Ajustes de espacio seguro y altura del panel móvil.
- Service Worker versionado con preferencia por red para evitar HTML antiguo en caché.

## Limitaciones y pendientes
No se ha completado una prueba integral en iOS ni pruebas automatizadas de navegación. La elevación GPX puede contener ruido y el desnivel no está filtrado. El cálculo de desviación GPS usa proximidad a puntos, no segmentos. El guardado de GeoJSON en localStorage tiene límites de tamaño. El mapa offline no está garantizado: Leaflet y los mapas base se cargan de servidores externos. El GPS no garantiza funcionamiento en segundo plano. No utilizar como sistema único de orientación o seguridad en montaña.

## Publicación
GitHub Pages → rama main → /(root).

Créditos: © OpenStreetMap contributors, © OpenTopoMap.
