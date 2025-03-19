# Documentación del Sistema de Gestión de Gastos

Este documento describe las vistas y funcionalidades principales del sistema de gestión de gastos, desarrollado con Django. Los usuarios pueden registrar, editar, eliminar y consultar sus gastos, además de generar reportes en formato CSV.

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Vistas](#vistas)
   - [`index`](#index)
   - [`register`](#register)
   - [`login_view`](#login_view)
   - [`home`](#home)
   - [`obtener_filtro_fecha`](#obtener_filtro_fecha)
   - [`generar_reporte`](#generar_reporte)
   - [`lista_gastos`](#lista_gastos)
   - [`registrar_gasto`](#registrar_gasto)
   - [`deshacer_gasto`](#deshacer_gasto)
   - [`editar_gasto`](#editar_gasto)
   - [`eliminar_gasto`](#eliminar_gasto)
3. [Modelo de Datos](#modelo-de-datos)
4. [Funcionalidad de la Pila de Gastos](#funcionalidad-de-la-pila-de-gastos)
5. [Seguridad](#seguridad)

---

## Introducción

El sistema de gestión de gastos permite a los usuarios controlar y administrar sus finanzas personales, registrando los gastos en categorías definidas. Los usuarios pueden acceder a su historial de gastos, filtrar por fechas y generar reportes en formato CSV.

---

## Vistas

### `index`
- **Descripción**: Página principal de la aplicación donde se muestra una vista de bienvenida.
- **Método**: `GET`
- **Parámetros**: Ninguno.
- **Salida**: Renderiza la plantilla `index.html`.

### `register`
- **Descripción**: Vista para registrar un nuevo usuario en el sistema.
- **Método**: `POST` para crear un nuevo usuario, `GET` para mostrar el formulario de registro.
- **Parámetros**: 
  - `POST`: Datos del formulario de creación de usuario.
- **Salida**:
  - Si el formulario es válido, crea al usuario y lo autentica, redirigiendo al login.
  - Si el formulario no es válido, se renderiza la plantilla `register.html` con el formulario y errores.

### `login_view`
- **Descripción**: Vista para iniciar sesión de un usuario registrado.
- **Método**: `POST` para procesar el inicio de sesión, `GET` para mostrar el formulario de login.
- **Parámetros**: 
  - `POST`: Nombre de usuario y contraseña.
- **Salida**:
  - Si la autenticación es exitosa, el usuario es redirigido a la vista `home`.
  - Si la autenticación falla, se renderiza la plantilla `login.html` con los errores correspondientes.

### `home`
- **Descripción**: Vista principal del usuario donde se muestran sus gastos.
- **Método**: `GET`
- **Parámetros**: Ninguno.
- **Salida**:
  - Renderiza `home.html` con los gastos del usuario agrupados por categoría, el total de gastos, la categoría con mayor gasto y el gasto más alto.

### `obtener_filtro_fecha`
- **Descripción**: Función para obtener la fecha límite según el filtro seleccionado.
- **Método**: `GET`
- **Parámetros**: 
  - `filtro`: Puede ser "ultimo_mes", "ultimos_3_meses", "este_anio".
- **Salida**: Devuelve la fecha límite según el filtro.

### `generar_reporte`
- **Descripción**: Genera un reporte de los gastos del usuario en formato CSV.
- **Método**: `GET`
- **Parámetros**:
  - `filtro_tiempo`: Tipo de filtro (último mes, últimos 3 meses, etc.).
  - `fecha_inicio` y `fecha_fin`: Fechas personalizadas.
- **Salida**: Un archivo CSV descargable con los gastos filtrados.

### `lista_gastos`
- **Descripción**: Vista que muestra una lista de los gastos del usuario con filtros aplicados.
- **Método**: `GET`
- **Parámetros**:
  - `filtro_tiempo`: Tipo de filtro (último mes, este año, etc.).
  - `fecha_inicio` y `fecha_fin`: Fechas para filtro personalizado.
- **Salida**: Renderiza `lista_gastos.html` con los gastos filtrados.

### `registrar_gasto`
- **Descripción**: Permite al usuario registrar un nuevo gasto.
- **Método**: `POST` para crear el gasto, `GET` para mostrar el formulario.
- **Parámetros**: 
  - `POST`: Datos del formulario de registro (título, categoría, monto, fecha, descripción).
- **Salida**:
  - Redirige a `lista_gastos` después de guardar el gasto.

### `deshacer_gasto`
- **Descripción**: Elimina el último gasto registrado por el usuario.
- **Método**: `GET`
- **Parámetros**: Ninguno.
- **Salida**: Elimina el último gasto registrado y redirige a `lista_gastos`.

### `editar_gasto`
- **Descripción**: Permite al usuario editar un gasto previamente registrado.
- **Método**: `POST` para actualizar el gasto, `GET` para mostrar el formulario de edición.
- **Parámetros**:
  - `gasto_id`: ID del gasto a editar.
- **Salida**: Redirige a `lista_gastos` después de guardar los cambios.

### `eliminar_gasto`
- **Descripción**: Elimina un gasto registrado por el usuario.
- **Método**: `GET`
- **Parámetros**:
  - `gasto_id`: ID del gasto a eliminar.
- **Salida**: Elimina el gasto de la base de datos y redirige a `lista_gastos`.

---

## Modelo de Datos

### `Gasto`
- Representa un gasto realizado por el usuario, con los siguientes atributos:
  - `titulo`: Nombre o título del gasto.
  - `categoria`: Categoría asociada al gasto.
  - `monto`: Monto del gasto.
  - `fecha`: Fecha en que se realizó el gasto.
  - `descripcion`: Descripción adicional del gasto.

### `Categoria`
- Representa una categoría de gastos (por ejemplo, "Comida", "Transporte").

---

## Funcionalidad de la Pila de Gastos

El sistema implementa una pila (`pila_gastos`) para mantener un registro temporal de los gastos recién registrados. Esto permite "deshacer" el último gasto registrado. La pila se almacena en la sesión del usuario y se actualiza cada vez que un gasto es añadido o eliminado.

---

## Seguridad

- Se utiliza el decorador `@login_required` para proteger las vistas que requieren autenticación.
- La pila de gastos se gestiona a través de la sesión de Django, garantizando que la información esté disponible solo durante la sesión del usuario.
- Se manejan los errores de autenticación y validación de formularios para proteger las operaciones de los usuarios.

---

### Notas Adicionales

- Asegúrate de que todas las dependencias de Django estén instaladas y correctamente configuradas.
- El sistema está diseñado para ser escalable, permitiendo la futura adición de nuevas funcionalidades como el soporte para múltiples monedas o la integración con servicios externos de pago.

