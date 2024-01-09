$(document).ready(function() {
    // Make the task name draggable on mousedown
    $("tbody").on("mousedown", ".text-center", function(event) {
        // Make the task name draggable
        $(this).draggable({
            revert: "invalid",
            helper: "original"
        });
    });

    // Make the days droppable
    $(".day").droppable({
        drop: function(event, ui) {
            // Extract the task name and priority from the original row
            var taskName = ui.helper.text().trim();
            var taskPriority = ui.helper.parent().find(".text-center").text().trim();
            var dayOfWeek = $(this).attr("id");

            // Save the dropped task to the server
            saveTaskStateToServer(taskName, dayOfWeek);
        }
    });

    // Load the task state from the server
    loadTaskStateFromServer();
});

// Function to get the current task state
function getTaskState() {
    var taskState = {};

    // Iterate over each day of the week and capture the task assigned to it
    $(".day").each(function() {
        var dayOfWeek = $(this).attr("id");
        var taskName = $(this).text();

        // Check if the day has a task assigned
        if (taskName.trim() !== "") {
            taskState[dayOfWeek] = taskName;
        }
    });

    return taskState;
}

// Function to update the UI with the loaded task state
function updateUIWithTaskState(taskState) {
    Object.keys(taskState).forEach(function(dayOfWeek) {
        $("#" + dayOfWeek).text(taskState[dayOfWeek]);
    });
}

// Function to save the task state to the server
function saveTaskStateToServer(taskName, dayOfWeek) {
    $.ajax({
        url: '/save',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            taskName: taskName,
            dayOfWeek: dayOfWeek
        }),
        success: function(response) {
            console.log(response);
            location.reload(); // Reload the page after saving
        },
        error: function(error) {
            console.error('Error saving task state:', error);
        }
    });
}

// Function to load the task state from the server
function loadTaskStateFromServer() {
    $.ajax({
        url: '/load',
        type: 'GET',
        success: function(taskState) {
            // Update the UI with the loaded task state
            updateUIWithTaskState(taskState);
        },
        error: function(error) {
            console.error('Error loading task state:', error);
        }
    });
}
