// 1. Разрешаем бросать карточки в эту область
function allowDrop(ev) {
    ev.preventDefault();
    
    // Находим саму колонку
    let column = ev.target.closest('.kanban-column');
    if (column) {
        column.classList.add('drag-over');
    }
}

// 2. Убираем подсветку, когда карточка улетает из колонки
document.addEventListener("dragleave", function(ev) {
    let column = ev.target.closest('.kanban-column');
    if (column) {
        column.classList.remove('drag-over');
    }
});

// 3. Начало перетаскивания
function drag(ev) {
    // Передаем ID элемента (например, "task-5")
    ev.dataTransfer.setData("text", ev.target.id);
    ev.target.classList.add('dragging');
}

// 4. Обработка броска (Drop)
function drop(ev) {
    ev.preventDefault();
    
    // Получаем ID перетаскиваемой карточки
    const data = ev.dataTransfer.getData("text");
    const taskElement = document.getElementById(data);
    
    if (!taskElement) return;

    // Находим колонку, в которую бросили
    let column = ev.target.closest('.kanban-column');
    
    if (column) {
        column.classList.remove('drag-over');
        taskElement.classList.remove('dragging');

        // Получаем новый статус (todo, doing или done)
        const newStatus = column.getAttribute('data-status');
        // Получаем ID задачи (убираем приставку "task-")
        const taskId = taskElement.getAttribute('data-id');
        
        // Находим внутренний контейнер колонки, куда нужно вставить карточку
        // В твоем HTML это <div id="todo-column"> и т.д.
        const targetContainer = document.getElementById(`${newStatus}-column`);
        
        if (targetContainer) {
            // Визуально переносим (чтобы не было рывка до обновления страницы)
            targetContainer.appendChild(taskElement);
            
            console.log(`Перемещаем задачу ${taskId} в статус ${newStatus}`);
            
            // Отправляем запрос на сервер для сохранения в БД
            // Используем window.location.href, так как твой FastAPI делает Redirect
            window.location.href = `/move/${taskId}/${newStatus}`;
        }
    }
}