function toggleDescription(taskId) {
    var descriptionElement = document.getElementById('descricao-' + taskId);
    if (descriptionElement.style.display === 'none') {
        descriptionElement.style.display = 'block';
    } else {
        descriptionElement.style.display = 'none';
    }
}

function editarTarefa(tarefaId) {
    window.location.href = '/editartarefas/' + tarefaId;
}
