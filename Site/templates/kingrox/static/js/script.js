document.addEventListener("DOMContentLoaded", function () {
    // Esconde as mensagens após 10 segundos (para .messages)
    setTimeout(function () {
        $('.messages').fadeOut('slow');
    }, 7000);  // 7000 milissegundos (7 segundos)

    // Verifica se há erros na página e esconde a lista de mensagens de erro após 7 segundos
    if (document.querySelector('ul.errorlist')) {
        setTimeout(function () {
            $('ul.errorlist').fadeOut('slow');
        }, 7000);  // 7000 milissegundos = 7 segundos
    }
});



var swiper = new Swiper(".mySwiper", {
    loop: true, // Permite rotação infinita
    autoplay: {
        delay: 3000, // Troca de slide a cada 3 segundos
        disableOnInteraction: false,
    },
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
});


function updateRanking() {
    let limit = document.getElementById("ranking-limit").value;
    window.location.href = "?limit=" + limit; // Atualiza a URL com o parâmetro de limite
}

function searchRanking() {
  let input = document.getElementById("search-name").value.toLowerCase();
  let rows = document.querySelectorAll(".ranking-row");
  let found = false;

  rows.forEach(row => {
      let name = row.cells[0].innerText.toLowerCase();
      if (name.includes(input)) {
          row.style.display = "";
          found = true;
      } else {
          row.style.display = "none";
      }
  });

  // Exibir ou ocultar a mensagem de "Personagem não encontrado"
  let noResultsMessage = document.getElementById("no-results");
  if (found) {
      noResultsMessage.style.display = "none";
  } else {
      noResultsMessage.style.display = "inline-block";
      noResultsMessage.style.marginLeft = "20px";
  }
}

  


// Escolhe aleatoriamente um vídeo
const randomVideo = window.videos[Math.floor(Math.random() * window.videos.length)];

// Define a fonte do vídeo
document.getElementById('video-source').src = randomVideo;

// Recarrega o vídeo para garantir que o novo arquivo seja carregado
document.getElementById('background-video').load();




