let tasks = [];

async function addTask() {
    const title = document.getElementById('taskTitle').value;
    const category = document.getElementById('taskCat').value;

    if (!title) return alert("Введите описание!");

    // Запрос к FastAPI
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ title, category })
    });

    const data = await response.json();

    // Добавляем в массив
    tasks.push({
        title: title,
        priority: data.priority,
        time: data.time
    });

    renderTasks();
}

function renderTasks() {
    const table = document.getElementById('taskTable');
    table.innerHTML = '';

    // Сортировка по приоритету (High -> Medium -> Low)
    const pMap = { 'High': 1, 'Medium': 2, 'Low': 3 };
    tasks.sort((a, b) => pMap[a.priority] - pMap[b.priority]);

    tasks.forEach(t => {
        let color = t.priority === 'High' ? 'table-danger' : (t.priority === 'Medium' ? 'table-warning' : 'table-info');
        table.innerHTML += `
            <tr class="${color}">
                <td>${t.title}</td>
                <td><strong>${t.priority}</strong></td>
                <td>${t.time} ч.</td>
            </tr>
        `;
    });
}