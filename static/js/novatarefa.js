document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-nova-tarefa');
    const prioridadeRadios = document.getElementsByName('prioridade');
    const mensagemErro = document.createElement('div');
    mensagemErro.id = 'mensagem-erro';
    mensagemErro.style.display = 'none';
    mensagemErro.style.color = 'red';
    mensagemErro.style.marginBottom = '20px';
    mensagemErro.textContent = 'Selecione uma prioridade para prosseguir.';
    form.prepend(mensagemErro);

    form.addEventListener('submit', function(event) {
        let prioridadeSelecionada = false;
        for (const radio of prioridadeRadios) {
            if (radio.checked) {
                prioridadeSelecionada = true;
                break;
            }
        }
        if (!prioridadeSelecionada) {
            event.preventDefault();
            mensagemErro.style.display = 'block';
        } else {
            mensagemErro.style.display = 'none';
        }
    });
});
