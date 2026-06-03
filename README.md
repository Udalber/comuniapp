# ComuniApp — Librería Virtual Comunitaria

MVP web académico (Universidad Iberoamericana, Análisis y Diseño de Sistemas). Plataforma para conectar lectores con vendedores y servicios del libro en la comunidad.

**Prototipo de referencia:** [Figma — ComuniApp](https://www.figma.com/design/sUIJIYy4Wf3Y7oI0oWeH41)

## Stack

- Django (última versión estable)
- Python 3.11+
- HTML, CSS y JavaScript vanilla (sin React, Vue, Tailwind ni Bootstrap)

## Inicio rápido

```bash
cd comuniapp
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # opcional; ajustar SECRET_KEY en producción
python manage.py migrate
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

## Estructura de apps

| App       | Responsabilidad                                      | Estado en esta sesión   |
|-----------|------------------------------------------------------|-------------------------|
| `config`  | Settings, URLs raíz, WSGI                            | Configurado             |
| `core`    | `base.html`, navbar, footer, landing, CSS de diseño  | Implementado            |
| `accounts`| Modelo `User` (`AbstractUser`)                       | Modelo + `AUTH_USER_MODEL` |
| `catalog` | Catálogo y búsqueda                                  | Vacía (TODO)            |
| `cart`    | Carrito                                              | Vacía (TODO)            |
| `orders`  | Pedidos y checkout                                   | Vacía (TODO)            |

## Convenciones para agentes / desarrolladores

1. **Plantillas:** Toda vista renderiza una plantilla que extiende `core/base.html`.
2. **Estilos:** Usar únicamente variables CSS de `core/static/css/design.css`. No hardcodear colores, espaciados ni radios.
3. **URLs:** Cada app expone su `urls.py` e inclúyelo en `config/urls.py` con `include()`.
4. **Responsive:** Mobile-first; breakpoints en `layout.css`: móvil &lt;768px, tablet 768–1024px, escritorio &gt;1024px.
5. **Accesibilidad:** WCAG 2.1 AA — contraste ≥ 4.5:1, etiquetas visibles en formularios, foco visible, landmarks ARIA.
6. **Usuario custom:** `AUTH_USER_MODEL = "accounts.User"` — no cambiar tras migraciones en producción.

## Variables de entorno

| Variable        | Descripción                          | Por defecto              |
|-----------------|--------------------------------------|--------------------------|
| `SECRET_KEY`    | Clave Django                         | valor dev (cambiar)      |
| `DEBUG`         | Modo depuración                      | `True`                   |
| `ALLOWED_HOSTS` | Hosts permitidos (coma-separados)    | `localhost,127.0.0.1`  |
| `DATABASE_URL`  | URL PostgreSQL (dj-database-url)     | SQLite local           |

WhiteNoise sirve archivos estáticos en producción (`collectstatic`).

## Comandos útiles

```bash
python manage.py createsuperuser
python manage.py collectstatic
python manage.py check
```

## Sesiones futuras (no incluidas aquí)

- Login, registro y perfil (`accounts`)
- Modelos y vistas de libros (`catalog`)
- Carrito y contador en navbar (`cart`)
- Checkout y pedidos (`orders`)
