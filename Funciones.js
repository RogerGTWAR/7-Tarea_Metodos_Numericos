function toggleSubmenu(id) {
  const submenu = document.getElementById(id);
  const isVisible = submenu.style.display === 'block';

  // No cerramos los demás, solo alternamos este
  submenu.style.display = isVisible ? 'none' : 'block';
}


// ✅ Función para cargar los resultados desde el backend
function cargarResultados() {
  fetch("http://127.0.0.1:5000/resultados-biseccion")
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#tabla-resultados tbody");
      tbody.innerHTML = "";
      data.forEach(fila => {
        const tr = document.createElement("tr");
        fila.forEach(celda => {
          const td = document.createElement("td");
          td.textContent = celda;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error("Error cargando los datos:", error);
    });
}

// ✅ Se ejecuta todo cuando carga la página
document.addEventListener("DOMContentLoaded", function () {
  cargarResultados(); // 👈 Se carga la tabla al iniciar

  const form = document.querySelector("form");
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    fetch("http://127.0.0.1:5000/biseccion", {
      method: "POST",
      body: formData
    })
      .then(response => response.text())
      .then(msg => {
        console.log("Servidor:", msg);
        cargarResultados(); // 👈 Se actualiza la tabla después del cálculo
      })
      .catch(error => {
        console.error("Error al enviar los datos:", error);
      });
  });
});


function eliminarEjercicio() {
  const ejercicio = document.getElementById("ejercicio").value;

  if (!ejercicio) {
    alert("Por favor, ingresa el número de ejercicio a eliminar.");
    return;
  }

  if (!confirm(`¿Estás seguro de eliminar los datos del ejercicio #${ejercicio}?`)) {
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-biseccion/${ejercicio}`, {
    method: "DELETE"
  })
    .then(response => response.text())
    .then(msg => {
      alert(msg);
      cargarResultados(); // actualiza tabla
    })
    .catch(error => {
      console.error("Error al eliminar:", error);
      alert("Error al eliminar los datos.");
    });
}

function actualizarEjercicio() {
  const form = document.querySelector("form");
  const formData = new FormData(form);

  fetch("http://127.0.0.1:5000/actualizar-biseccion", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      console.log("✅ Actualización completada");
      cargarResultados(); // ⬅️ recarga la tabla
    })
    .catch(error => {
      console.error("❌ Error al actualizar:", error);
    });
}

// FUNCIONES PARA FALSA POSICION

function cargarResultadosFalsa() {
  fetch('http://127.0.0.1:5000/resultados-falsa-posicion')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-falsa').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();
        fila.forEach(valor => {
          const celda = nuevaFila.insertCell();
          celda.textContent = valor;
        });
      });
    })
    .catch(error => console.error('Error cargando resultados:', error));
}

function eliminarEjercicioFalsa(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-falsa').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-falsa-posicion/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosFalsa();
    })
    .catch(error => console.error('Error al eliminar ejercicio:', error));
}

function actualizarEjercicioFalsa(event) {
  event.preventDefault();
  const formData = new FormData();
  formData.append('ejercicio', document.getElementById('ejercicio-falsa').value);
  formData.append('funcion', document.getElementById('funcion-falsa').value);
  formData.append('xa', document.getElementById('xa-falsa').value);
  formData.append('xb', document.getElementById('xb-falsa').value);
  formData.append('es', document.getElementById('es-falsa').value);

  fetch('http://127.0.0.1:5000/actualizar-falsa-posicion', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosFalsa();
    })
    .catch(error => console.error('Error al actualizar ejercicio:', error));
}

// Cargar resultados automáticamente al abrir la página
window.addEventListener('load', function () {
  cargarResultadosFalsa();
});

// 🔥 NUEVO: FORMULARIO FALSA POSICIÓN
const formFalsa = document.querySelector('form[action="http://127.0.0.1:5000/falsa-posicion"]');
formFalsa.addEventListener("submit", function (event) {
  event.preventDefault();

  const formData = new FormData(formFalsa);
  fetch("http://127.0.0.1:5000/falsa-posicion", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(msg => {
      console.log("Servidor (Falsa):", msg);
      cargarResultadosFalsa(); // 👈 actualizar tabla
    })
    .catch(error => {
      console.error("Error Falsa Posición:", error);
    });
});





