$(document).ready(function () {
        const entriesPerPage = 20;
        const totalEntries = $(".entry-row").length;
        const totalPages = Math.ceil(totalEntries / entriesPerPage);
        let currentPage = 1;

        function showPage(page) {
            $(".entry-row").hide();
            $(".entry-row").slice((page - 1) * entriesPerPage, page * entriesPerPage).show();
            $("#section-number").text("Section " + page + " of " + totalPages);

            // Disable prev button on the first page
            if (page === 1) {
                $("#prev-btn").prop('disabled', true);
            } else {
                $("#prev-btn").prop('disabled', false);
            }

            // Disable next button on the last page
            if (page === totalPages) {
                $("#next-btn").prop('disabled', true);
            } else {
                $("#next-btn").prop('disabled', false);
            }
        }

        $("#prev-btn").click(function () {
            if (currentPage > 1) {
                currentPage--;
                showPage(currentPage);
            }
        });

        $("#next-btn").click(function () {
            if (currentPage < totalPages) {
                currentPage++;
                showPage(currentPage);
            }
        });

        showPage(currentPage);

        // Function to sort entries based on roll number
        $("#sort-roll-icon").click(function () {
            var entries = $(".entry-row");
            entries.sort(function (a, b) {
                var rollA = parseInt($(a).find("td:eq(2)").text());
                var rollB = parseInt($(b).find("td:eq(2)").text());
                return rollA - rollB;
            });
            $("#entries-table tbody").empty().append(entries);
            $("#sort-name-icon").removeClass("desc");
            $(this).toggleClass("desc");
        });

        // Function to sort entries based on name
        $("#sort-name-icon").click(function () {
            var entries = $(".entry-row");
            entries.sort(function (a, b) {
                var nameA = $(a).find("td:eq(1)").text().toUpperCase();
                var nameB = $(b).find("td:eq(1)").text().toUpperCase();
                return (nameA < nameB) ? -1 : (nameA > nameB) ? 1 : 0;
            });
            $("#entries-table tbody").empty().append(entries);
            $("#sort-roll-icon").removeClass("desc");
            $(this).toggleClass("desc");
        });

        // Function to reset sorting to default
        $("#reset-icon").click(function () {
            location.reload();
        });

        // Handling success message display
        var urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('success') && urlParams.get('success') === 'true') {
            $('#success-popup').fadeIn().delay(5000).fadeOut();
        }

        // Handle CSV download button click
        $("#download-csv").click(function () {
            var topicId = "{{ topic.id }}";
            window.location.href = `/attendance/${topicId}/download-csv/`;
        });

         $("#search-box").on("input", function () {
            var query = $(this).val().toLowerCase().trim(); // Get the search query
            $(".entry-row").each(function () {
                var name = $(this).find("td:eq(1)").text().toLowerCase().trim(); // Get name in lowercase
                var rollNumber = $(this).find("td:eq(2)").text().toLowerCase().trim(); // Get roll number in lowercase
                if (name.includes(query) || rollNumber.includes(query)) {
                    $(this).show(); // Show row if matches query
                } else {
                    $(this).hide(); // Hide row if does not match query
                }
            });
        });
    });

