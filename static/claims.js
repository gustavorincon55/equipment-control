
//document.onload = 

addListeners(document.querySelectorAll("tr"));

// fix issue with chrome and empty div inside the table
eraseEmptyDiv(document.querySelectorAll("tr"));
console.log("loaded");


// add listener to all rows
function addListeners(rows) {
	let isChanged = false;

	for (let row of rows) {

		// don't mess with the header
		if (row.getAttribute("scope") == "row") {



			for (let _td of row.children) {
				_td.addEventListener("dblclick", function () {
					makeRowEditable(row);
				});

			}

			row.addEventListener("input", function () {
				isChanged = true;
			});

			row.querySelector('[type = file]').addEventListener("change", function () {
				sendFileToServer(this.parentNode.parentNode.parentNode)
			})

		}
	}

	let btn = document.querySelector("#closedClaimsBtn");
	btn.addEventListener("click", function () {
		showClosedClaims();
	})
}

// function called after a double click on a row
function makeRowEditable(row) {


	if (row.contentEditable == true) {
		return "";
	}

	//row.querySelectorAll("select")[0].classList.remove("d-none")
	//row.querySelectorAll("[meaning = 'status']")[0].classList.add("d-none")

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
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4) {
			console.log(this.responseText);
			return endEdit(row);
		}

	};
	//console.log("updateClaim", this)
}

function joinRowData(row) {

	let data = "";
	let country = document.querySelector("[country]");

	data += "id=" + row.getAttribute("claim_id") + "@@";
	data += "country=" + country.getAttribute("country") + '@@';
	//let tr = row.children;
	// get the data from the row and make an object.
	let order = ['unit', 'customer', 'bl', 'charge', 'invoice', 'date', 'status', 'attachements', 'damage', 'comment'];
	let orderI = 0;

	if (row.children.length == 10) {
		for (let td of row.children) {

			// cancell any "/". because it breaks the server on the url
			let text = td.innerText;

			if (text.split("/").length > 1) {
				text = text.split("/").join("-slash-");
			}

			data += order[orderI] + "=";
			data += text;

			//skip putting a @@ as the last item.
			if (orderI === order.length - 1) { break; }
			data += "@@";

			orderI += 1;
		}
	} else { console.log("update the order variable with the header"); }


	return data;
}


function saveAllEditables() {

	rows = document.querySelectorAll("[contentEditable = 'true']");

	for (let row of rows) {
		updateClaimTable(row);
	}
};

function deleteClaim(claimId) {

	let header = document.querySelector("header");
	let table = document.querySelector("#main-table tbody");
	let htmlRow = document.querySelector(`[claim_id='${claimId}']`);

	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", "/erase_claim/" + claimId, true);
	xhttp.send();
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4) {
			console.log("server: ", this.responseText);
			console.log(table);
			console.log(htmlRow);
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

	let claimId = row.getAttribute("claim_id");

	//turn the row into an object

	let order = ['unit', 'customer', 'bl', 'charge', 'invoice', 'date', 'status', 'attachements', 'damage', 'comment'];
	claim = {};

	for (let i = 0; i < order.length; i++) {
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
								${claim.customer}
							</div>
						</td>
						<td class="align-baseline" meaning="bl">
							<div class="claim-cell" style="">
								${ claim.bl}
							</div>
						</td>
						<td class="align-baseline" meaning="charge">
							<div class="claim-cell " style="">
								${ claim.charge}
							</div>
						</td>
						<td class="align-baseline" meaning="invoice">
							<div class="claim-cell" style="">
								${ claim.invoice}
							</div>
						</td>
						<td class="align-baseline" meaning="date">
							<div class="claim-cell" style="">
								${ claim.date}
							</div>
						</td>
						<td class="align-baseline" meaning="status">
							<div class="claim-cell" style="">
								${ claim.status}
							</div>
						</td>
						<td class="align-baseline" meaning="damage">
							<div class="claim-cell" style="">
								${ claim.damage}
							</div>
						</td>
						<td class="align-baseline" meaning="commnet">
							<div class="claim-cell" style="">
								${ claim.comment}
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

function sendFileToServer(form) {

	console.log(form);

	let file = form.children[0].children[0].children[0];
	let claim_id = form.getAttribute("claim_id");

	let formData = new FormData(form);
	formData.append("claim_id", claim_id);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/add_file");
	xhttp.send(formData);
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4) {
			alert(this.responseText)
			console.log(this.response)
			saveAllEditables();
			location.reload()
		}
	};


}

function getFileFromServer(file_data) {

	claim_id = file_data.getAttribute("claim_id");
	file_id = file_data.getAttribute("file_id");

	console.log(claim_id, file_id)
	let request = new XMLHttpRequest()

	request.open("GET", "/download_file/" + file_id + "/" + claim_id);
	request.send();
	request.onreadystatechange = function () {
		console.log(this.response)
	}
}

function deleteFileMode(modal_body) {

	console.log(modal_body)

	files = modal_body.querySelectorAll("a");

	for (let file of files) {

		file.className += " delete_file_mode";


		fileId = file.getAttribute("file_id");
		claimId = file.getAttribute("claim_id");
		console.log(fileId, claimId, "\n")

		file.addEventListener("click", function (event) {
			event.preventDefault();
			deleteFile(this);
		})
	}
	modal_header = modal_body.parentNode.children[0];
	console.log(modal_header)
	modal_header.innerHTML = '<h5 class="m-auto">CLICK TO ERASE</h5>'

	modal_footer = modal_body.parentNode.children[2];
	modal_footer.innerHTML =
		`
	<label type="button" class="btn btn-secondary m-auto" onclick="location.reload()" >
		Done
	</label>
	`

}

function deleteFile(fileHtml) {
	fileId = fileHtml.getAttribute("file_id");
	claimId = fileHtml.getAttribute("claim_id");
	modal_body = fileHtml.parentNode;
	console.log(fileHtml);
	console.log(fileId, claimId, '\n\n');

	let request = new XMLHttpRequest();
	request.open("GET", `/delete_file/${fileId}/${claimId}`)
	request.send()
	request.onreadystatechange = function () {
		if (this.readyState == 4) {
			if (this.response == "deleted") {
				modal_body.removeChild(fileHtml);
			}
			console.log(this.response)
			buttonAndCounter = document.querySelectorAll(`.buttonAndCounter${claimId}`)[0];
			console.log(buttonAndCounter);
			buttonAndCounter.innerHTML = parseInt(buttonAndCounter.innerHTML) - 1;
			console.log(buttonAndCounter);

		}
	}
}

function editClaim() {

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

	let claimId = row.getAttribute("claim_id");

	return window.location.href = "/edit_claim/" + claimId;
}

function eraseEmptyDiv(rows) {
	for (let row of rows) {
		for (let td of row.children) {
			if (td.innerText == "") {
				td.innerHTML = "";
			}
		}
	}

	console.log("eraseEmptyDiv")
}

function showClosedClaims() {

	let table = document.querySelector("table");

	let request = new XMLHttpRequest();

	request.open("GET", "/claims_closed");
	request.send();

	request.onreadystatechange = function () {
		if (this.readyState == 4) {

			let claims = JSON.parse(request.responseText);

			console.log(claims)

			let html_claims = "";

			for (let claim of claims) {

				let modal_files = "";

				for (let file of claim.files) {

					modal_files +=
						`
					<a target="_blank" href="/download_file/${file.id}}/${claim.id}" style="width:90%"
					file_id="${file.id}" claim_id="${claim.id}"
					class="btn btn-outline-secondary modal_file">
					${file.file_name}
					</a> 
					`
				}

				html_claims +=
					`

				<tr scope="row" claim_id="${claim.id}" contenteditable="false" class="non_open">

				<td class="align-middle" meaning="unit">
					<div class="claim-cell">
						${ claim.unit}
					</div>
				</td>

				<td class="align-middle" meaning="customer">
					<div class="claim-cell">
						${ claim.customer}
					</div>
				</td>

				<td class="align-middle" meaning="bl">
					<div class="claim-cell">
						${ claim.bl}
					</div>
				</td>
				<td class="align-middle" meaning="charge">
					<div class="claim-cell ">
						${ claim.charge}
					</div>
				</td>

				<td class="align-middle" meaning="invoice">
					<div class="claim-cell">
						${ claim.invoice}
					</div>
				</td>

				<td class="align-middle" meaning="date">
					<div class="claim-cell">
						${ claim.date}
					</div>
				</td>

				<td class="align-middle status_${claim.status}" meaning="status">
					<div class="claim-cell">
						${ claim.status}
					</div>

				</td>

				<td class="align-middle" meaning="attachements">

					<form action="/add_file" method="POST" enctype="multipart/form-data" claim_id=${claim.id}>
						<div class="btn-group btn-group-toggle" max-widt="100%">

							<label class="btn btn-secondary" style="width:50%;">
								<input type="file" name="claim_file" class="btn btn-secondary" style="display: none;"
									placeholder="+">+
							</label>

							<!-- Button trigger modal -->

							<button type="button" class="btn btn-secondary buttonAndCounter${claim.id}"
								style="width:50%;" data-toggle="modal" data-target="#claim-${claim.id}">
								${claim.files.length}
							</button>

						</div>
					</form>

					<!-- Modal -->

					<div class="modal fade" id="claim-${claim.id}" tabindex="-1" role="dialog"
						aria-labelledby="claim-${claim.id}" aria-hidden="true">
						<div class="modal-dialog modal-dialog-centered" role="document">
							<div class="modal-content">
								<div class="modal-header">
									<h5 class="modal-title" id="claim-${claim.id}">Attachements</h5>
									<button type="button" class="close" data-dismiss="modal" aria-label="Close">
										<span aria-hidden="true">&times;</span>
									</button>
								</div>
								<div class="modal-body"> 
								
								${modal_files}
								
								</div>
								<div class="modal-footer">
									<label type="button" class="btn btn-danger"
										onclick="deleteFileMode(this.parentNode.parentNode.children[1])">
										Delete a file
									</label>

									<label type="button" class="btn btn-secondary" data-dismiss="modal">
										Close
									</label>

								</div>
							</div>
						</div>
					</div>
				</td>

				<td class="align-middle" meaning="damage">
					<div class="claim-cell">
						${ claim.damage}
					</div>
				</td>

				<td class="align-middle" meaning="commnet">
					<div class="claim-cell" style="width: 15em;">
						${ claim.comment}
					</div>
				</td>
			</tr>

				`

				//html_claims.push(html_claim);
			}

			table.innerHTML += html_claims
			addListeners(document.querySelectorAll("tr"));

		}
	}

	//delete the buttom
	let btn = document.querySelector("#closedClaimsBtn");
	btn.parentElement.removeChild(btn);

}

