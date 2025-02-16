<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Scheduler</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding: 20px; }
        .form-control { margin-bottom: 10px; }
        .btn-primary { width: 100%; }
        table { margin-top: 20px; }
        .btn-danger, .btn-info { margin-right: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Task Scheduler</h1>
        
        <form method="POST" action="/crystal-onyxscheduler-service/add">
            <div class="row">
                <div class="col">
                    <input type="text" class="form-control" name="name" placeholder="Task Name" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="command" placeholder="Command" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" name="cron" placeholder="Cron Expression" required>
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
                    <td>
                        <a href="/crystal-onyxscheduler-service/delete/{{ task.name }}" class="btn btn-danger">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h3>Completed Jobs</h3>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Command</th>
                    <th>Cron Expression</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for job in completed_jobs %}
                <tr>
                    <td>{{ job.name }}</td>
                    <td>{{ job.command }}</td>
                    <td>{{ job.cron }}</td>
                    <td class="{% if job.status == 'Success' %}text-success{% elif job.status == 'Failed' %}text-danger{% else %}text-warning{% endif %}">
                        {{ job.status }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
