$(document).ready(function () {
    // Toggle user details when clicking the "View" button
    $(".view-button").on("click", function () {
        var userId = $(this).data("user-id");
        $("#user_card_" + userId + " .user-details").toggle();
    });

    // Toggle message form when clicking the "Message" button
    $(".message-button").on("click", function () {
        // Get the user ID associated with the clicked button
        var userId = $(this).data("user-id");
        // Toggle the message form corresponding to the user ID
        $("#messageForm_" + userId).toggle();
    });

    // Toggle sidebar
    $("#sidebarCollapseBtn").on("click", function () {
        $(".sidebar").toggleClass("collapsed");
        $(".main-content").toggleClass("collapsed");
    });

    // Toggle user creation form when clicking the button
    $("#toggleUserForm").on("click", function () {
        $("#userCreationForm").toggleClass("show");
        $("#overlay").toggleClass("show"); // Toggle overlay
    });

    // Submit user creation form
    $("#createUserForm").on("submit", function (event) {
        event.preventDefault();
        var formData = {
            username: $("#username").val(),
            email: $("#email").val(),
            phoneNumber: $("#phoneNumber").val(),
            rentPayDate: $("#rentPayDate").val(),
            rentEndDate: $("#rentEndDate").val(),
        };

        // Send form data to the backend (Django view)
        $.ajax({
            type: "POST",
            url: "/create_client/",
            data: formData,
            success: function (response) {
                // Handle successful response (if needed)
                console.log(response);
                // Refresh the page or update the user list, etc.
                window.location.reload();
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle error (if needed)
                console.error(xhr.responseText);
            },
        });
    });

    // Delete client when clicking the "Delete" button
    $(".delete-button").on("click", function () {
        var userId = $(this).data("user-id");
        if (confirm("Are you sure you want to delete this user?")) {
            $.ajax({
                type: "DELETE",
                url: `/delete_client/${userId}/`,
                success: function (response) {
                    console.log(response);
                    // Remove the card from the UI if deletion was successful
                    $("#user_card_" + userId).remove();
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.error(xhr.responseText);
                },
            });
        }
    });

    // Submit message form when clicking the "Send Message" button
    $(".message-button").on("click", function () {
        // Get the user ID associated with the clicked button
        var userId = $(this).data("user-id");

        // Submit the corresponding message form
        $("#sendMessageForm_" + userId).on("submit", function (event) {
            event.preventDefault();
            var formData = new FormData(this); // Create FormData object from the form

            // Send form data to the backend (Django view)
            $.ajax({
                type: "POST",
                url: "/send_message/", // Adjust the URL to your Django view
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    // Handle successful response (if needed)
                    console.log(response);
                    // You can display a success message or update the UI as needed
                },
                error: function (xhr, textStatus, errorThrown) {
                    // Handle error (if needed)
                    console.error(xhr.responseText);
                },
            });
        });
    });
});
