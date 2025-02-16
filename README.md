<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Scheduler</title>

    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    
    <style>
        body {
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 800px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        .form-control {
            margin-bottom: 10px;
        }
        .btn-primary, .btn-danger, .btn-info {
            width: 100%;
            margin-top: 10px;
        }
        table {
            margin-top: 20px;
        }
        th {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>

<div class="container">
    <h1 class="text-center">Task Scheduler</h1>

    <form method="POST" action="/crystal-onyxscheduler-service/add">
        <div class="form-group">
            <input type="text" class="form-control" name="name" placeholder="Task Name" required>
        </div>
        <div class="form-group">
            <input type="text" class="form-control" name="command" placeholder="Command" required>
        </div>
        <div class="form-group">
            <input type="text" class="form-control" name="cron" placeholder="Min Hour DOM Month DOW (Cron Expression)" required>
        </div>
        <button type="submit" class="btn btn-primary">Add Task</button>
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
                    <a href="/crystal-onyxscheduler-service/delete/{{ task.name }}" class="btn btn-danger btn-sm">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h3>Completed Jobs</h3>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Name</th>
                <th>Command</th>
                <th>Status</th>
                <th>Output</th>
            </tr>
        </thead>
        <tbody>
            {% for job in completed_jobs %}
            <tr>
                <td>{{ job.name }}</td>
                <td>{{ job.command }}</td>
                <td>{{ job.status }}</td>
                <td>{{ job.output }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <a href="/crystal-onyxscheduler-service/completed-jobs" class="btn btn-info">Refresh Completed Jobs</a>
</div>

</body>
</html>
