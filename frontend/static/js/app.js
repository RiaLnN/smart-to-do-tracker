fetch("/api/tasks/")
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById("task-list");
    list.innerHTML = data.map(task => `<li>${task.title}</li>`).join("");
  });
