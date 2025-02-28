document.addEventListener("DOMContentLoaded", function () {
    // Esconde as mensagens após 10 segundos
    setTimeout(function () {
        $('.messages').fadeOut('slow');
    }, 10000);  // 10000 milissegundos (10 segundos)
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


// Função para alternar entre os temas
function toggleDarkMode() {
const currentTheme = document.documentElement.classList.contains('dark-mode') ? 'light-mode' : 'dark-mode';
document.documentElement.classList.toggle('dark-mode');
document.documentElement.classList.toggle('light-mode');
localStorage.setItem('corMode', currentTheme); // Salva o tema selecionado
}


// Verifica se o tema foi previamente selecionado pelo usuário
document.addEventListener('DOMContentLoaded', function() {
    const corMode = localStorage.getItem('corMode');
    if (corMode) {
        document.documentElement.classList.add(corMode);
    } else {
        // Define um tema padrão se nenhum foi selecionado anteriormente
        document.documentElement.classList.add('light-mode'); // Ou 'dark-mode', dependendo do seu padrão
    }
});



function toggleScreen() {
    const screen = document.getElementById('infoScreen');
    
    // Verifica se a tela está visível ou não
    if (screen.style.display === "none" || screen.style.display === "") {
      screen.style.display = "block";
    } else {
      screen.style.display = "none";
    }
  }
  









  function updateCountdown(eventId, remainingSeconds) {
    const countdownElement = document.getElementById('countdown_' + eventId);
    if (!countdownElement) return;

    const remainingDays = Math.floor(remainingSeconds / 86400);
    const remainingHours = Math.floor((remainingSeconds % 86400) / 3600);
    const remainingMinutes = Math.floor((remainingSeconds % 3600) / 60);
    const remainingSecs = Math.round(remainingSeconds % 60);

    if (remainingSeconds > 86400) {
        countdownElement.innerText = `${remainingDays} dias e ${remainingHours} horas restantes`;
    } else if (remainingSeconds > 3600) {
        countdownElement.innerText = `${remainingHours} horas, ${remainingMinutes} minutos e ${remainingSecs} segundos restantes`;
    } else if (remainingSeconds > 60) {
        countdownElement.innerText = `${remainingMinutes} minutos e ${remainingSecs} segundos restantes`;
    } else if (remainingSeconds > 1) {
        countdownElement.innerText = `${remainingSecs} segundos restantes`;
    } else if (remainingSeconds >= 0) {
        countdownElement.innerText = "Evento iniciado!";
        
        // Adicionar um pequeno atraso antes de chamar o próximo evento
        setTimeout(fetchNextEvent, 30000);
    } else {
        countdownElement.innerText = "Evento finalizado!";
    }
}

// Busca os tempos dos eventos
function fetchEventTimes() {
    fetch('/event_time_remaining/')
        .then(response => response.json())
        .then(data => {
            if (data.events.length === 0) {
                console.log("Nenhum evento disponível.");
                return;
            }

            data.events.forEach(event => {
                updateCountdown(event.event_id, event.remaining_seconds);
            });
        })
        .catch(error => console.error('Erro ao buscar os tempos dos eventos:', error));
}

// Busca o próximo evento após o atual terminar
function fetchNextEvent() {
    fetch('/next_event/')
        .then(response => response.json())
        .then(data => {
            if (!data.next_event) {
                console.log("Nenhum próximo evento encontrado.");
                return;
            }

            const nextEvent = data.next_event;
            document.getElementById('event-name').innerText = nextEvent.name;
            document.getElementById('event-time').innerText = nextEvent.start_time;

            // Espera um pouco antes de atualizar os eventos novamente
            setTimeout(fetchEventTimes, 30000);
        })
        .catch(error => console.error('Erro ao buscar o próximo evento:', error));
}

// Atualiza a contagem regressiva a cada segundo
setInterval(fetchEventTimes, 1000);





