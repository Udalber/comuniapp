# ComuniApp — Librería Virtual Comunitaria

MVP web académico de la **Universidad Iberoamericana** (Análisis y Diseño de Sistemas). Plataforma para conectar lectores con vendedores y servicios del libro en la comunidad.

**Prototipo de referencia:** [Figma — ComuniApp](https://www.figma.com/design/sUIJIYy4Wf3Y7oI0oWeH41)

## Stack

- Django (última versión estable)
- Python 3.11+
- HTML, CSS y JavaScript vanilla (sin React, Vue, Tailwind ni Bootstrap)
- SQLite (desarrollo) / PostgreSQL (producción)
- WhiteNoise para archivos estáticos en producción

## Funcionalidades del MVP

- Registro e inicio de sesión por correo electrónico
- Catálogo de libros con búsqueda, filtros y detalle
- Carrito de compras (sesión)
- Checkout en cuatro pasos (dirección, pago simulado, resumen, confirmación)
- Historial de pedidos, perfil de usuario y direcciones guardadas

## Documentación

| Documento | Contenido |
|-----------|-----------|
| **[RUNBOOK.md](RUNBOOK.md)** | Instalación local, encender el servidor y solución de problemas frecuentes |

## Inicio rápido

```bash
cd comuniapp
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
copy .env.example .env          # opcional; ajustar SECRET_KEY en producción
python manage.py migrate
python manage.py seed_catalog   # catálogo de demostración (opcional)
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

## Estructura de apps

| App | Responsabilidad |
|-----|-----------------|
| `config` | Settings, URLs raíz, WSGI |
| `core` | Layout global (`base.html`), landing, CSS de diseño |
| `accounts` | Autenticación, perfil y cambio de contraseña |
| `catalog` | Catálogo, búsqueda, filtros y detalle de libros |
| `cart` | Carrito de compras en sesión |
| `orders` | Checkout, pedidos, historial y direcciones |

## Convenciones de desarrollo

1. **Plantillas:** Toda vista renderiza una plantilla que extiende `core/base.html`.
2. **Estilos:** Usar únicamente variables CSS de `core/static/css/design.css`. No hardcodear colores, espaciados ni radios.
3. **URLs:** Cada app expone su `urls.py` e inclúyelo en `config/urls.py` con `include()`.
4. **Responsive:** Mobile-first; breakpoints en `layout.css`: móvil &lt;768px, tablet 768–1024px, escritorio &gt;1024px.
5. **Accesibilidad:** WCAG 2.1 AA — contraste ≥ 4.5:1, etiquetas visibles en formularios, foco visible, landmarks ARIA.
6. **Usuario custom:** `AUTH_USER_MODEL = "accounts.User"` — no cambiar tras migraciones en producción.

## Variables de entorno

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `SECRET_KEY` | Clave Django | valor dev (cambiar en producción) |
| `DEBUG` | Modo depuración | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (coma-separados) | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL PostgreSQL (dj-database-url) | SQLite local |

## Comandos útiles

```bash
python manage.py test
python manage.py createsuperuser
python manage.py collectstatic
python manage.py check
python manage.py seed_catalog
```

## Pruebas

```bash
python manage.py test
```

El proyecto incluye pruebas unitarias e de integración del flujo de compra completo.

## Despliegue

El proyecto está preparado para **Render**: conectar el repositorio con el Blueprint `render.yaml`. El script `build.sh` instala dependencias, recopila estáticos, aplica migraciones y ejecuta `seed_catalog`.
