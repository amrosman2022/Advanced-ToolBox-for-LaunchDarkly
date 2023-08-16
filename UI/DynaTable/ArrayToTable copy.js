
function ArrayToTable() { // ArrayToTable class definiton
    var self = this;
    
    this.replaceRules = {};
    this.tableclasses = '';
    this.tableid = '';
    
} // ArrayToTable class definition END
    
ArrayToTable.prototype.putTableHtmlToId = function(dataArray, id, skipfields) {
    var tableDiv = document.getElementById(id);
    tableDiv.innerHTML = '';
    tableDiv.innerHTML = this.getHtmlForArray(dataArray, skipfields);
};

ArrayToTable.prototype.getHtmlForArray = function(dataArray, skipfields) {
    var self = this;
    n_Row_Num_ID = 0;

    if (Object.keys(dataArray).length === 0) {
        return '';
    }

    var newhtml = '<table';
    if (this.tableclasses !== '') {
        newhtml += ' class="' + this.tableclasses + '"';
    }
    if (this.tableid !== '') {
        newhtml += ' id="' + this.tableid + '"';
    }
    newhtml += '>';

    newhtml += '<thead><tr><th calss="material-icons">view_day</th>';
    var footer = '<tfoot><tr><th calss="material-icons">view_day</th>';
    Object.keys(dataArray[0]).forEach(function(col) {                   
        if (typeof(self.replaceRules) === 'undefined' || typeof(self.replaceRules[col]) === 'undefined') {
            newhtml += '<th class="col_' + col.trim().replace(/\s+/g, '') + '">' + col + '</th>';
            footer += '<th class="col_' + col.trim().replace(/\s+/g, '') + '">' + col + '</th>';
        } else {
            newhtml += '<th class="col_' + col.trim().replace(/\s+/g, '') + '">' + self.replaceRules[col] + '</th>';
            footer += '<th class="col_' + col.trim().replace(/\s+/g, '') + '">' + self.replaceRules[col] + '</th>';                
        }
    });
    newhtml += '</tr></thead>';
    footer += '</tr></tfoot>';

    Object.keys(dataArray).forEach(function(row) {
        newhtml += '<tr id="' + n_Row_Num_ID + '" onClick="func_ExpandRow(this)">';
        n_Row_Num_ID++; 
        //---- Add expand Column
        newhtml += '<td calss="material-icons">view_day</td>'
        Object.keys(dataArray[row]).forEach(function(col) {
            newhtml += '<td class="col_' + col.trim().replace(/\s+/g, '') + '">';
            // Skip COLUMNS named below as they do not contain JSON
            const regex = new RegExp(col, 'i');
            //if (col == 's_proj_id' || col == 's_proj_tags')
            if (regex.test(skipfields) == true)
            {
                output = dataArray[row][col];
            }else{
                var JSONobj = JSON.parse(dataArray[row][col]);
                output = formatJsonToHtml(JSONobj);
            }
            newhtml += output; //dataArray[row][col];
            newhtml += '</td>';
        });        

        newhtml += '</tr>';
    });

    newhtml += footer;

    newhtml += '</table>';

    return newhtml;
};


    // Local function within the constructor
    function formatJsonToHtml(data) {
        function createHtml(jsonData) {
            let html = '';
            if (Array.isArray(jsonData)) {
                html += '<ul>';
                for (const item of jsonData) {
                    html += '<li>';
                    html += createHtml(item);
                    html += '</li>';
                }
                html += '</ul>';
            } else if (typeof jsonData === 'object' && jsonData !== null) {
                html += '<ul>';
                for (const key in jsonData) {
                    html += '<li>';
                    html += `<strong>${key}:</strong> `;
                    html += createHtml(jsonData[key]);
                    html += '</li>';
                }
                html += '</ul>';
            } else {
                html += String(jsonData);
            }
            return html;
        }

        const formattedHtml = createHtml(data);
        return formattedHtml;
    }

// end define once prototypes of class ArrayToTable
