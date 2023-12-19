s_userID = '';

    // ---------------------------------------------
    // ---------------------------------------------
    // ---------------------------------------------
    function sleep(miliseconds) 
    {
      var currentTime = new Date().getTime();
      while (currentTime + miliseconds >= new Date().getTime()) {
      }
    }


    // ---------------------------------------------
    // -----UI: Show/Hide All the search Form ------
    // ----------------------------------------------
    function func_toggleDivState (me, s_element,)
    {
        state = document.getElementById(s_element);
        document.getElementById("form_search").reset();
        if (me.id == "LAP")
        {
            state.style.display = "none";
            document.getElementById("LAP").style.color="green";
            document.getElementById("SAP").style.color="Gray";
        }
        else
        {
            state.style.display = "block";
            document.getElementById("SAP").style.color="green";
            document.getElementById("LAP").style.color="Gray";
        }
    }


// ----------------------------------------------
// --------------  Check if looged in------------
// ----------------------------------------------
const isLoggedIn = async () => 
  {
      try
      {
          const response = await fetch('http://localhost:8080/validlogin');
          const myJson = await response.json(); //extract TEXT from the http response
          if (JSON.parse(myJson)['success']==true)
          {
            console.log('opening index.html');
            window.open('index.html','_self');
          }
          else  // if user is already logged - no action needed
          {
            console.log(JSON.parse(myJson)['message']);
            s_userID = JSON.parse(myJson)['userid'];
            document.getElementById('USERID_H').innerText = s_userID;
            return true;
          }
      }
      catch(e)
      {
        const myJson = e.message;
        func_ShowAlert(myJson);
        console.log(e.message);
        return (e);
      }
  }// End of isLoggedin

    // ----------------------------------------------
    // -----------UI: Show/Hide Form Field-----------
    // ----------------------------------------------
    function func_toggleElementState (me, s_element)
    {
        state = document.getElementById(s_element);
        if (me.checked == true)
        {
            state.disabled = false;
        }
        else
        {
            state.disabled = true;
        }
    }


// -----------------changed-----------------------
// ------  Show alert in an overlay      ---------
// -----------------------------------------------
function func_ShowAlert(s_Message='', b_visibility=false)
  {
    if (b_visibility == true)
    {
      document.getElementById('divStatus').style.visibility = 'visible';
      document.getElementById('divStatusText').innerText = s_Message;
      setTimeout(func_ShowAlert, 3000); // Call hideElement after 3 seconds
    }
    else
    {
      document.getElementById('divStatus').style.visibility = 'hidden';
      document.getElementById('divStatusText').innerText = '';
    }
    
  }



// -----------------changed-----------------------
// ------  Get the HTML table paging info---------
// - and display the pages links below the table -
// -----------------------------------------------
const getTableInfo = async (n_pageNumber) => 
  {
      try
      {
          const response = await fetch('http://localhost:8080/tableinfo');
          const myJson = await response.json(); //extract TEXT from the http response
          n_tableCnt = myJson['count'];
          n_tablePgs = myJson['pages'];
          n_itemsPerPage = myJson['itemsperpage'];
          s_pagination = createPaginationHTML(n_tablePgs,n_pageNumber);
          document.getElementById('results_line3').innerHTML = s_pagination;
      }
      catch(e)
      {
        const myJson = e.message;
        func_ShowAlert(myJson);
        console.log(e.message);
        return (e);
      }
  }// End of getTableInfo


// -----------------Changed-----------------------
// -- Call the API to get a page from the table --
// -----------------------------------------------
function func_getNextPage(objAnchor)
{
    n_pageNumber = Number(objAnchor.id.split("_")[1]);
    func_selector(n_pageNumber,false);
}


// -----------------changed-----------------------
// ------  Get the HTML table paging info---------
// - and display the pages links below the table -
// -----------------------------------------------
const getTableInfo2 = async (n_pageNumber) => 
  {
      try
      {
          const response = await fetch('http://localhost:8080/tableinfo');
          const myJson = await response.json(); //extract TEXT from the http response
          n_tableCnt = myJson['count'];
          n_tablePgs = myJson['pages'];
          n_itemsPerPage = myJson['itemsperpage'];
          s_pagination = createPaginationHTML(n_tablePgs,n_pageNumber);
          document.getElementById('results_line3').innerHTML = s_pagination;
      }
      catch(e)
      {
        const myJson = e.message;
        func_ShowAlert(myJson);
        console.log(e.message);
        return (e);
      }
  }// End of getTableInfo

// ---------------------------------------------------------------------------------
// --------------------- Create the paging HTML and retrun it as string ------------
// ---------------------------------------------------------------------------------
function createPaginationHTML(numPages, numActivePage) 
{
    const links = [];
    strHTML = '<nav aria-label="Page navigation"><ul class="pagination justify-content-center pagination-lg">';

    for (let i = 1; i <= numPages; i++) 
    {
        if (numActivePage == i)
        {
            strHTML += '<li class="page-item active"><a onclick="func_getNextPage(this);" id="jumppage_' + i + '" class="page-link" href="#results_line">' + i + '</a></li>';
        }
        else
        {
            strHTML += '<li class="page-item"><a onclick="func_getNextPage(this);" id="jumppage_' + i + '" class="page-link" href="#results_line">' + i + '</a></li>';

        }
    }
    strHTML += '</ul></nav>';
    
    return strHTML;
}

// ------------------------------------------------------
// ------------- Form elements validation ---------------
// ------------------------------------------------------
function func_validate(obj_input)
{

  Number((obj_input.value)<0 || Number(obj_input.value)>100)? obj_input.style.borderColor = 'red':obj_input.style.borderColor = 'lightgray';
  Number((obj_input.value)<0 || Number(obj_input.value)>100)? obj_input.value=0:obj_input.value=obj_input.value;

}
function validate(obj_input,obj_event) // Placeholder
{
  return 0;
}    

var evtSource;
g_j_streamData = {}

// --------------------\/ Streaming \/-------------------
// ------------------------------------------------------
// ------------------Open Streaming Connection ----------
// ------------------------------------------------------
function func_startStreamT(streamName, targetID)
{
    evtSource = new EventSource('http://127.0.0.1:5000/stream_status?streamName=status');
    evtSource.addEventListener(streamName, (event) => 
    {
        const listElement = document.getElementById('list');
        const newElement = document.getElementById(targetID);
        newElement.innerText = event.data;
        g_j_streamData = JSON.parse(event.data);
    }
    );
}
// ------------------------------------------------------
// ------------------Close Streaming Connection ---------
// ------------------------------------------------------
function func_closeStream()
{
    evtSource.close();
}
