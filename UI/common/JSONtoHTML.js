
function JSONtoHTML ()
{
    var self = this;
}


JSONtoHTML.prototype.formatJsonToHtml = function(data2) 
{
    function formatJsonToHtml_i(data){
        if (typeof data !== 'object' || data === null) {
            return String(data);
        }

        let html = '<ul>';
        for (const key in data) {
            html += '<li>';

            if (typeof data[key] === 'object' && data[key] !== null) {
                html += `${key}: `;
                html += formatJsonToHtml_i(data[key]);
            } else {
                html += `${key}: ${data[key]}`;
            }

            html += '</li>';
        }
        html += '</ul>';

        return html;
    }
}