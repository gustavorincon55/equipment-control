
addListeners(document.querySelectorAll("tr"));

// add listener to all rows
function addListeners(rows) {
	let isChanged = false;
	for(let rowN in rows) {

		// don't mess with the header
		if (rowN == 0) {continue;}

		rows[rowN].addEventListener("dblclick", function() {
			editable(this);
		});

		rows[rowN].addEventListener("input", function() {
			isChanged = true;
		});

		console.log('line 108');

		rows[rowN].addEventListener("blur", function() {

			if (isChanged == true) {

				isChanged = false;
				return updateDataBase(this);
			}

			return endEdit(this);

		});

		// take away the div when the cell is empty
		for (let td of rows[rowN].children) {
			if(td.innerText.length <= 2) {
				td.removeChild(td.children[0]);
			}
		}

	}
}

// function called after a double click on a row
function editable(row) {

	if(row.contentEditable == true) {
		return ""
	}
	
	row.contentEditable = true;
	row.classList.add("editable-row");
}

function endEdit(row) {

	if (row.className != undefined) {
		row.classList.remove("editable-row");
	}
	
	return row.contentEditable = false;
}

function updateDataBase(row) {

	let xhttp = new XMLHttpRequest();

	xhttp.open("GET", "/update_claim/" + getRowData(row), true);
	xhttp.send();
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4) {
			console.log(this.responseText);
			endEdit(row);
		}
	};
}

function getRowData(row) {
	let data = "";

	data += "id=" + row.getAttribute("table-id") + "@@";
	//let tr = row.children;
	// get the data from the row and make an object.
	let order = ['unit', 'customer', 'bl', 'charge', 'invoice', 'date', 'status', 'attachements', 'damage', 'comment'];
	let orderI = 0;

	if(row.children.length == 10) {
		for(let td of row.children) {
			data += order[orderI] + "=";
			data += td.innerText;

			//skip putting a @@ as the last item.
			if(orderI === order.length - 1) {break;}
			data += "@@";

			orderI += 1;
		}
	} else { console.log("update the order variable with the header");}


	return data;
}


function saveAll() {
	rows = document.querySelectorAll("tr");

	for(let rowN in rows) {
		if(rowN == 0) { continue;}

		updateDataBase(rows[rowN]);

	}
};

//


