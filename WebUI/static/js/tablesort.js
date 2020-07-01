/**
 * Sorts a HTML table.
 *
 * @param {HTMLTableElement} table The table to sort
 * @param {number} column The index of the column to sort
 * @param {boolean} asc Determines if the sorting will be in ascending
 */
function sortTableByColumn(table, column, asc = true) {
    var dtext = document.getElementById("demo");
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));
    // Sort each row
    const sortedRows = rows.sort((a, b) => {
        dtext.textContent = column;
        const aColText = a.querySelector(`td:nth-child(${ column + 1})`).textContent.trim();
        const bColText = b.querySelector(`td:nth-child(${ column + 1})`).textContent.trim();
        const aTime = new Date(aColText);
        const bTime = new Date(bColText);
        // Time
        if(!isNaN(aTime) && aColText.includes('-')){
            console.log(aTime);
            return aTime > bTime ? (1 * dirModifier) : (-1 * dirModifier);
        }
        else{
            // If it is not a time, separate by ":"
            if(aColText.includes(':')){
                var idA = aColText.split(":");
                var idB = bColText.split(":");
                var index = 0;
                // Fetch each part and compare.
                for(index; index < idA.length; index++){
                    if(parseFloat(idA[index]) > parseFloat(idB[index])){
                        return (1 * dirModifier);
                    }else if(parseFloat(idA[index]) < parseFloat(idB[index])){
                        return (-1 * dirModifier)
                    }
                }
                // If two values are the same
                return (-1 * dirModifier);
            }
            // Not an integer and not a running time
            else if(isNaN(parseInt(aColText))){
                return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
            }else{
                // Integer
                return parseInt(aColText) > parseInt(bColText) ? (1 * dirModifier) : (-1 * dirModifier);
            }
        }

    });

    // Remove all existing TRs from the table
    while (tBody.firstChild) {
        tBody.removeChild(tBody.firstChild);
    }

    // Re-add the newly sorted rows
    tBody.append(...sortedRows);

    // Remember how the column is currently sorted
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
}

document.querySelectorAll(".content-table th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAscending = headerCell.classList.contains("th-sort-asc");

        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });
});