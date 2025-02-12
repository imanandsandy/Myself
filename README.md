<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Scheduler</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container mt-5">
    <h2 class="text-center">Task Scheduler</h2>
    
    <form method="POST" action="/add" class="mb-4">
        <div class="row">
            <div class="col">
                <input type="text" class="form-control" name="name" placeholder="Task Name" required>
            </div>
            <div class="col">
                <input type="text" class="form-control" name="command" placeholder="Command" required>
            </div>
            <div class="col">
                <input type="text" class="form-control" name="cron" placeholder="Cron Expression (*/5 * * * *)" required>
            </div>
            <div class="col">
                <button type="submit" class="btn btn-primary">Add Task</button>
            </div>
        </div>
    </form>

    <h3>Scheduled Tasks</h3>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Name</th>
                <th>Command</th>
                <th>Cron Expression</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for task in tasks %}
            <tr>
                <td>{{ task.name }}</td>
                <td>{{ task.command }}</td>
                <td>{{ task.cron }}</td>
                <td><a href="/delete/{{ task.name }}" class="btn btn-danger">Delete</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <a href="/logs" class="btn btn-info">View Logs</a>
</body>
</html>
