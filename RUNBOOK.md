# Runbook — ComuniApp

Guía operativa para instalar, ejecutar y verificar el proyecto en local.

**Convenciones de código:** ver [README.md](README.md).

---

## 1. Requisitos previos

| Requisito | Cómo comprobarlo |
|-----------|------------------|
| Python 3.11 o superior | `python --version` |
| Git (opcional) | `git --version` |
| Puerto **8000** libre (o el que elijas para `runserver`) | Sin otro `runserver` activo en ese puerto |

No hace falta PostgreSQL en local: por defecto se usa **SQLite** (`db.sqlite3` en la raíz del proyecto).

---

## 2. Primera vez (setup completo)

Ejecutar desde la raíz del proyecto (`comuniapp/`).

### Windows (PowerShell)

```powershell
cd comuniapp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Opcional: variables de entorno
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

python manage.py migrate
python manage.py seed_catalog   # catálogo de demostración (opcional)
python manage.py check
```

### Linux / macOS (bash)

```bash
cd comuniapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env 2>/dev/null || true
python manage.py migrate
python manage.py seed_catalog
python manage.py check
```

**Criterio de éxito:** `python manage.py check` termina con `System check identified no issues`.

---

## 3. Encender el servidor

```powershell
cd comuniapp
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Salida esperada:

```text
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**URL base:** http://127.0.0.1:8000/

**Detener el servidor:** `Ctrl+C` (o `Ctrl+Break` en Windows) en la terminal donde corre `runserver`.

### Puerto alternativo

```powershell
python manage.py runserver 8765
```

→ http://127.0.0.1:8765/ — si usas otro puerto, actualiza las URLs en las secciones siguientes.

---

## 4. Verificación rápida

### 4.1 Comprobaciones en terminal

Con el venv activado (el servidor no es obligatorio para `check`/`migrate`):

```powershell
python manage.py check
python manage.py showmigrations accounts
```

`showmigrations accounts` debe mostrar `[X] 0001_initial`.

Con el servidor encendido, comprobar HTTP (PowerShell):

```powershell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing).StatusCode
```

Debe devolver `200`.

Comprobar estáticos y marca:

```powershell
$r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing
$r.Content -match "design.css"
$r.Content -match "ComuniApp"
```

Ambas expresiones deben ser `True`.

Comprobar autenticación:

```powershell
$login = Invoke-WebRequest -Uri "http://127.0.0.1:8000/accounts/login/" -UseBasicParsing
$login.StatusCode -eq 200
$login.Content -match "auth.css"

$reg = Invoke-WebRequest -Uri "http://127.0.0.1:8000/accounts/register/" -UseBasicParsing
$reg.StatusCode -eq 200
$reg.Content -match 'data-auth-form="register"'
```

### 4.2 Comprobaciones visuales

| Prueba | Qué validar |
|--------|-------------|
| Landing `/` | Hero, buscador, categorías desde BD |
| Estilos | Fondo crema, verde primario, fuente **Inter** |
| Catálogo `/catalog/` | Grid de libros, búsqueda y filtros |
| Detalle `/catalog/<slug>/` | Galería, metadatos, botón carrito |
| Carrito `/cart/` | Ítems, cantidades, total |
| Navbar (anónimo) | «Iniciar sesión» y «Registrarse» |
| Navbar (autenticado) | Nombre, menú usuario, carrito con contador |
| Checkout | Flujo dirección → pago → resumen → confirmación |
| Responsive | Probar ~375px, ~768px y ~1280px en DevTools |

### 4.3 Rutas principales

| URL | Comportamiento |
|-----|----------------|
| `/` | Landing |
| `/catalog/` | Catálogo con búsqueda y filtros |
| `/catalog/<slug>/` | Detalle del libro |
| `/cart/` | Carrito |
| `/orders/checkout/` | Checkout (requiere login) |
| `/orders/history/` | Historial de pedidos (requiere login) |
| `/accounts/register/` | Registro |
| `/accounts/login/` | Login |
| `/accounts/profile/` | Mi cuenta (requiere login) |
| `/admin/` | Django admin (`createsuperuser`) |
| `/accounts/password-reset/` | Placeholder «próximamente» |

---

## 5. Pruebas manuales sugeridas

### 5.1 Registro e inicio de sesión

1. Abrir `/accounts/register/` y crear una cuenta.
2. Verificar toast de bienvenida y navbar con tu nombre.
3. Cerrar sesión e iniciar sesión de nuevo en `/accounts/login/`.
4. Probar credenciales incorrectas → mensaje genérico de error.

### 5.2 Catálogo y carrito

1. Buscar «García Márquez» en `/catalog/?q=García`.
2. Abrir el detalle de un libro.
3. Agregar al carrito y revisar `/cart/`.
4. Actualizar cantidad y eliminar un ítem.

### 5.3 Checkout

1. Con ítems en el carrito, ir a «Proceder al pago».
2. Completar dirección, método de pago (simulado) y resumen.
3. Confirmar pedido → pantalla con número `CMA-XXXXXX`.
4. Verificar el pedido en `/orders/history/`.

### 5.4 Regresión general

1. Landing, navbar sticky y footer sin roturas visuales.
2. Menú hamburguesa en móvil.
3. Perfil en `/accounts/profile/` y direcciones en `/orders/addresses/`.

---

## 6. Pruebas automatizadas

```powershell
python manage.py test
```

**Resultado esperado:** `Ran 34 tests` — todos OK. Incluye pruebas unitarias e integración del flujo de compra completo.

---

## 7. Admin (opcional)

```powershell
python manage.py createsuperuser
```

Abrir http://127.0.0.1:8000/admin/ (el admin usa **username**, no el flujo de correo de la app).

---

## 8. Despliegue en Render

1. Subir el repositorio a GitHub.
2. En [Render](https://render.com): **New → Blueprint** y conectar el repo.
3. Render lee `render.yaml` y crea el web service + PostgreSQL.
4. El `build.sh` instala dependencias, ejecuta `collectstatic`, `migrate` y `seed_catalog`.
5. Copiar la URL pública (`https://comuniapp-xxxx.onrender.com/`) para la entrega académica.
6. Crear superusuario desde la **Shell** de Render: `python manage.py createsuperuser`.

---

## 9. Problemas frecuentes

| Síntoma | Causa probable | Acción |
|---------|----------------|--------|
| `Couldn't import Django` | venv no activado | Activar `.venv` y `pip install -r requirements.txt` |
| `Port already in use` | Otro `runserver` activo | Cerrar el proceso anterior o usar otro puerto |
| `No module named 'dotenv'` | Dependencias incompletas | `pip install -r requirements.txt` |
| Página sin estilos | `DEBUG=False` sin collectstatic | `DEBUG=True` en local; recargar forzado |
| `InconsistentMigrationHistory` | BD anterior incompatible | **Solo en dev:** borrar `db.sqlite3` y `python manage.py migrate` |
| Error al activar venv (PowerShell) | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |

**Importante:** no cambiar `AUTH_USER_MODEL` ni borrar `accounts/migrations/0001_initial.py` en un entorno con datos reales.

---

## 10. Variables de entorno

Archivo plantilla: `.env.example`.

| Variable | Uso en local |
|----------|----------------|
| `SECRET_KEY` | Opcional en dev (hay fallback en settings) |
| `DEBUG` | `True` para desarrollo |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` |
| `DATABASE_URL` | Omitir → SQLite en `db.sqlite3` |

---

## 11. Checklist antes de entregar o desplegar

```
[ ] venv activado + pip install -r requirements.txt
[ ] python manage.py migrate
[ ] python manage.py check → 0 issues
[ ] python manage.py test → 34/34 OK
[ ] python manage.py runserver → sin traceback
[ ] GET / → HTTP 200 con design.css
[ ] Flujo manual: registro → catálogo → carrito → checkout → historial
[ ] No commitear .env, db.sqlite3 ni .venv/
```

---

## 12. Referencias

| Recurso | Ubicación |
|---------|-----------|
| [README.md](README.md) | Resumen del proyecto y convenciones |
| Prototipo UI | https://www.figma.com/design/sUIJIYy4Wf3Y7oI0oWeH41 |
| Settings | `config/settings.py` |
| Plantilla base | `core/templates/core/base.html` |
| Tokens CSS | `core/static/css/design.css` |
| Deploy | `render.yaml`, `build.sh` |
