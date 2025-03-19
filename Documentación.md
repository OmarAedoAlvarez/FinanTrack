### Documentación FinanTrack

Este conjunto de vistas corresponde a un sistema de gestión de gastos donde los usuarios pueden registrar, editar, eliminar y consultar sus gastos, además de generar reportes en formato CSV. A continuación se proporciona una descripción detallada de cada vista y su funcionamiento.

---

### 1. **`index`**

- **Descripción**: Esta vista maneja la página de inicio de la aplicación, donde se muestra la pantalla principal de bienvenida.
- **Método**: `GET`
- **Entrada**: No tiene parámetros específicos.
- **Salida**: Renderiza la plantilla `index.html`.

---

### 2. **`register`**

- **Descripción**: Vista para permitir que los nuevos usuarios se registren en la plataforma.
- **Método**: `POST` para crear un nuevo usuario, `GET` para mostrar el formulario de registro.
- **Entrada**:
    - `POST`: Los datos del formulario de creación de usuario.
- **Salida**:
    - Si el formulario es válido, crea al usuario y lo autentica, redirigiendo al usuario a la página de login.
    - Si no es válido, renderiza la plantilla `register.html` con el formulario.

---

### 3. **`login_view`**

- **Descripción**: Vista para gestionar el inicio de sesión de los usuarios registrados.
- **Método**: `POST` para procesar el inicio de sesión, `GET` para mostrar el formulario de login.
- **Entrada**:
    - `POST`: El formulario de inicio de sesión con el nombre de usuario y la contraseña.
- **Salida**:
    - Si el usuario es autenticado correctamente, lo redirige al dashboard (`home`).
    - Si no es válido, renderiza el formulario de login con el error.

---

### 4. **`home`**

- **Descripción**: Vista principal donde se muestran los gastos del usuario.
- **Método**: `GET`
- **Entrada**: No tiene parámetros específicos.
- **Salida**:
    - Renderiza la plantilla `home.html` con el resumen de los gastos agrupados por categoría, el total de gastos, la categoría con mayor gasto y el gasto individual más grande.

---

### 5. **`obtener_filtro_fecha`**

- **Descripción**: Función que devuelve la fecha límite para los filtros de tiempo predefinidos.
- **Método**: `GET`
- **Entrada**: Parámetro `filtro` que puede ser "ultimo_mes", "ultimos_3_meses" o "este_anio".
- **Salida**: La fecha correspondiente al filtro.

---

### 6. **`generar_reporte`**

- **Descripción**: Vista que permite generar un reporte de los gastos en formato CSV, con filtros de fecha aplicados.
- **Método**: `GET`
- **Entrada**:
    - `filtro_tiempo`: Parámetro que determina el tipo de filtro a aplicar (por ejemplo, "ultimo_mes", "este_anio").
    - `fecha_inicio`, `fecha_fin`: Fechas de filtro personalizadas en formato `YYYY-MM-DD`.
- **Salida**:
    - Un archivo CSV con los gastos filtrados que el usuario puede descargar.

---

### 7. **`lista_gastos`**

- **Descripción**: Vista para mostrar la lista de gastos del usuario con la opción de filtrar por tiempo.
- **Método**: `GET`
- **Entrada**:
    - `filtro_tiempo`: Parámetro que determina el filtro de tiempo ("ultimo_mes", "este_anio", "personalizado").
    - `fecha_inicio`, `fecha_fin`: Fechas personalizadas para el filtro.
- **Salida**:
    - Renderiza la plantilla `lista_gastos.html` con la lista de gastos filtrados y las fechas de filtro.

---

### 8. **`registrar_gasto`**

- **Descripción**: Vista para permitir a los usuarios registrar un nuevo gasto.
- **Método**: `POST` para procesar el formulario, `GET` para mostrar el formulario de registro de gastos.
- **Entrada**:
    - `POST`: Datos del formulario para registrar el gasto (título, categoría, monto, fecha, descripción).
- **Salida**:
    - Si el gasto se guarda correctamente, redirige a la vista `lista_gastos`.

---

### 9. **`deshacer_gasto`**

- **Descripción**: Vista para deshacer el último gasto registrado (basado en una "pila" de gastos).
- **Método**: `GET`
- **Entrada**: No tiene parámetros específicos.
- **Salida**:
    - El último gasto registrado se elimina de la base de datos y de la "pila" en la sesión.

---

### 10. **`editar_gasto`**

- **Descripción**: Vista para editar un gasto previamente registrado.
- **Método**: `POST` para actualizar el gasto, `GET` para mostrar el formulario de edición.
- **Entrada**:
    - `gasto_id`: El ID del gasto que se desea editar.
    - `POST`: Datos del formulario para actualizar el gasto.
- **Salida**:
    - Si el gasto se edita correctamente, redirige a la vista `lista_gastos`.

---

### 11. **`eliminar_gasto`**

- **Descripción**: Vista para eliminar un gasto registrado.
- **Método**: `GET`
- **Entrada**:
    - `gasto_id`: El ID del gasto que se desea eliminar.
- **Salida**:
    - El gasto se elimina de la base de datos y, si se encuentra en la "pila", también se elimina de esta.

---

### **Modelo de Datos**

- **`Gasto`**: Representa un gasto realizado por el usuario, con atributos como `titulo`, `categoria`, `monto`, `fecha` y `descripcion`.
- **`Categoria`**: Representa las categorías de los gastos (por ejemplo, "Comida", "Transporte").

---

### **Funcionalidad de la Pila de Gastos**

La aplicación utiliza una pila global (`pila_gastos`) para mantener un registro temporal de los últimos gastos añadidos. Esto permite a los usuarios "deshacer" el último gasto realizado. La pila se maneja utilizando la sesión de Django, asegurando que el historial sea persistente durante la sesión del usuario.

---

### **Seguridad**

- Las vistas que requieren que el usuario esté autenticado están protegidas mediante el decorador `@login_required`.
- Las sesiones de usuario son utilizadas para gestionar la pila de gastos, lo que permite mantener un estado persistente de las acciones del usuario.
