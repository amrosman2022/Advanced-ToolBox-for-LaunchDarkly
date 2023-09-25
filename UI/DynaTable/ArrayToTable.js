// ***************************************************************************
// ************** ArrayToTable class definiton - Initialization Entry point ***
// *************************************************************************** 
function ArrayToTable() { 
    var self = this;
    
    this.replaceRules = {};
    this.tableclasses = '';
    this.tableid = '';
} 
 

// ------------------ ------------------ ------------------ ------------------ 
// ------------- ArrayToTable class function 1 - putTableHtmlToId -------------
// ------------------ ------------------ ------------------ ------------------ 
ArrayToTable.prototype.putTableHtmlToId = function(dataArray, id, skipfields) {
    var tableDiv = document.getElementById(id);
    tableDiv.innerHTML = '';
    tableDiv.innerHTML = this.getHtmlForArray(dataArray, skipfields);
};

// ------------------ ------------------ ------------------ ------------------ 
// ------------- ArrayToTable class function 2 - getHtmlForArray -------------
// ------------------ ------------------ ------------------ ------------------ 
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

    newhtml += '<thead><tr><th> </th>';
    var footer = '<tfoot><tr><th> </th>';
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
        newhtml += '<tr class="row-collapse" id="' + n_Row_Num_ID + '">';
        n_Row_Num_ID++; 
        //---- Add expand Column
        //newhtml += '<td onClick="func_ExpandRow(this)"></td>'
        newhtml += '<td></td>'
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
                output = '<div class="divJSON"><div class="rightCircle" onclick="func_ExpanDiv(this,' + n_Row_Num_ID + ')"><i class="material-icons" data-bs-toggle="offcanvas" data-bs-target="#offcanvasEnd" aria-controls="offcanvasEnd">unfold_more</i></div>' + output + '</div>'
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


// ********************************************************************
// ************* Local functions within the constructor *****************
//*********************************************************************

//------------------------------------------------------------------ 
//--------show the JSON Pop Modal and copy the TD LI's into it ------
//------------------------------------------------------------------ 
//show and hide of the pop-out slider is controlled by the ARIA tags on the clickable elements data-bs-toggle="offcanvas" data-bs-target="#offcanvasEnd" aria-controls="offcanvasEnd"
//------------------------------------------------------------------
function func_ExpanDiv(obj_ID, n_TrNum)     // n_TrNum = not implemented yet
{
    var html_ParentContent = obj_ID.parentNode.innerHTML;
    var content = document.getElementById("myModalContent3");
    content.innerHTML = html_ParentContent;
}
//------------------------------------------------------------------ 
//------ (Not Used) Expand the table
//------------------------------------------------------------------ 
function func_ExpandRow_old(obj_RowID)
{
    //console.log(obj_RowID.id);
    e= obj_RowID.parentNode;
    //get table id so you know what table to manipulate row from
    const tableID = e.parentNode.parentNode.id;

    //get row index and increment by 1 so you know what row to expand/collapse
    const i = e.rowIndex;

    //get the row to change the css class on
    let row = document.getElementById(tableID).rows[i]

    // Add and remove the appropriate  css classname to expand/collapse the row

    if (row.classList.contains('row-collapse')){
        row.classList.remove('row-collapse')
        row.classList.add('row-expand')
        return
    }
    if (row.classList.contains('row-expand')){
        row.classList.remove('row-expand')
        row.classList.add('row-collapse')
        return
    }
}
//--------------------------------------------------------------------------
// ------ format JSON to HTML - Convert the Data Column coming from CRDB ----
// -------- into a nested UL/LI HTML object ---------------------------------
//--------------------------------------------------------------------------
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
