
addListeners(document.querySelectorAll("tr"));

// add listener to all rows
function addListeners(rows) {
	let isChanged = false;
	for(let rowN in rows) {

		// don't mess with the header
		if (rowN == 0) {continue;}

		for(let _td of rows[rowN].children) {
			_td.addEventListener("dblclick", function() {
				editable(rows[rowN]);
				//_td.parentElement.focus();
			});
			/*_td.children[0].addEventListener("dblclick", function() {
				editable(rows[rowN]);
			});*/
		}

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
				return updateClaimTable(this);
			}

			return endEdit(this);

		});

		/*
		// take away the div when the cell is empty
		for (let td of rows[rowN].children) {
			if(td.innerText.length <= 2) {
				td.removeChild(td.children[0]);
			}
		}
		*/
	}
}

// function called after a double click on a row
function editable(row) {

	if(row.contentEditable == true) {
		return 
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

function updateClaimTable(row) {

	let xhttp = new XMLHttpRequest();

	xhttp.open("GET", "/update_claim/" + joinRowData(row), true);
	xhttp.send();
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4) {
			console.log(this.responseText);
			endEdit(row);
		}
	};
}

function joinRowData(row) {
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

		updateClaimTable(rows[rowN]);

	}
};

function deleteClaim(claimId) {

	let header = document.querySelector("header");
	let table = document.querySelector("main tbody");
	let htmlRow = document.querySelector(`main [table-id='${claimId}']`);

	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/erase_claim/" + claimId, true);
	xhttp.send();
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4) {
			console.log("server: ", this.responseText);
			console.log(table)
			table.removeChild(htmlRow);
			header.innerHTML = ""

		}
	};

}

function confirmClaimDelete() {
	let rows = document.querySelectorAll(".editable-row");

	if (rows.length != 1) {
		return document.getElementsByTagName("header")[0].innerHTML = 
		`                
		<div class="alert alert-warning alert-dismissible text-center fade show" role="alert">
			<button type="button" class="close" data-dismiss="alert">&times;</button>
			You need to select one claim at a time.
		</div>
		`
	} 

	row = rows[0];

	let claimId = row.getAttribute("table-id");

	//turn the row into an object

	let order = ['unit', 'customer', 'bl', 'charge', 'invoice', 'date', 'status', 'attachements', 'damage', 'comment'];
	claim = {};

	for(let i = 0; i < order.length; i++) {
		claim[order[i]] = row.children[i].innerText;
	}

	console.log(claim)


	let alertConfirmation = 
	` 
		<div class="alert alert-danger alert-dismissible text-center fade show" role="alert">
			<button type="button" class="close" data-dismiss="alert">&times;</button>
			<p>Are you sure you want to delete claim:</p>
			<table style="margin: auto;">
				<thead>
					<tr class="" classcontenteditable="false">
						<th scope="col" >Unit</th>
						<th scope="col" >Customer</th>
						<th scope="col" >Booking/BOL</th>
						<th scope="col" >Charges</th>
						<th scope="col" >Invoice</th>
						<th scope="col" >Date</th>
						<th scope="col" >Status</th>
						<th scope="col" >Damage</th>
						<th scope="col" style="width:10%;" >Comments</th>
					</tr>
				</thead>
				<tbody>
					<tr scope="row">
						<td class="align-baseline" meaning="unit">
							<div class="claim-cell" style="">
								${claim.unit}
							</div>
						</td>
			
						<td class="align-baseline" meaning="customer">
							<div class="claim-cell" style="">
								${claim.customer }
							</div>
						</td>
						<td class="align-baseline" meaning="bl">
							<div class="claim-cell" style="">
								${ claim.bl }
							</div>
						</td>
						<td class="align-baseline" meaning="charge">
							<div class="claim-cell " style="">
								${ claim.charge }
							</div>
						</td>
						<td class="align-baseline" meaning="invoice">
							<div class="claim-cell" style="">
								${ claim.invoice }
							</div>
						</td>
						<td class="align-baseline" meaning="date">
							<div class="claim-cell" style="">
								${ claim.date }
							</div>
						</td>
						<td class="align-baseline" meaning="status">
							<div class="claim-cell" style="">
								${ claim.status }
							</div>
						</td>
						<td class="align-baseline" meaning="damage">
							<div class="claim-cell" style="">
								${ claim.damage }
							</div>
						</td>
						<td class="align-baseline" meaning="commnet">
							<div class="claim-cell" style="">
								${ claim.comment }
							</div>
						</td>
					</tr>

					<tr>
						<td>	
						</td>
					</tr>
				</tbody>
				</table>
				<div style="margin:auto; padding-top:1em;">
					<button class="btn" onclick="deleteClaim(${claimId})">Delete</button>
				</div>
		</div>
	`
	document.getElementsByTagName("header")[0].innerHTML = alertConfirmation;

}

function sendFileToServer(files) {
	//alert("Work in progress");
	let file = files[0];

	console.log(file)

	let formData = new FormData();

	formData.append("file", file, file.name);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/add_file");
	xhttp.send(formData);
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4) {
			alert(this.responseText)
			console.log(this.response)
	   }
	}


}

//


