// Prevent click event propagation to parents of objects
// with the class "clickstopper".
$(".clickstopper").click(function(e) {
    e.stopPropagation();
});


var snakeoil = {} || snakeoil;


snakeoil.humanizeKey = function(key) {
    /* Turn the given data field key into something
    *  more human-readable.
    */
    switch (key) {
        case "sku":
            return "Product code";
        case "name":
            return "Name";
        case "description":
            return "Description";
        case "created":
            return "Created";
        case "updated":
            return "Updated";
        case "price":
            return "Price";
        case "num_in_stock":
            return "In stock";
        default:
            return key;
    }
};


snakeoil.removeChildren = function(parentElement) {
    while (parentElement.firstChild) {
        parentElement.removeChild(parentElement.lastChild);
    }
};


snakeoil.addDataToTableRow = function(tableRow, data, strong=false) {
    let td = document.createElement("td");

    if (strong) {
        td.innerHTML = `<strong>${data}</strong>`;
    }
    else {
        td.innerHTML = data;
    }

    tableRow.appendChild(td);
};


snakeoil.addKeyValueRow = function(tableBody, key, value) {
    let tr = document.createElement("tr");
    snakeoil.addDataToTableRow(tr, key, strong=true);
    snakeoil.addDataToTableRow(tr, value);
    tableBody.appendChild(tr);
};


snakeoil.flashTextOnButton = function(button, textToFlash, flashTimeMillisecs=1500) {
    if (!button.oldInnerHtml)
        button.oldInnerHtml = button.innerHTML;
    button.innerHTML = `<span class="glyphicon glyphicon-circle-arrow-down"></span>&nbsp;${textToFlash}`;
    setTimeout(() => { button.innerHTML = button.oldInnerHtml; }, flashTimeMillisecs);
};


snakeoil.addToCart = function(button, productId) {
    /* Add a product with the given primary key to the cart. */
    snakeoil.flashTextOnButton(button, "Added!");

    const request = new Request(
        webShopUrls.addToCart,
        {
            method: 'POST',
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({pk: productId})
        }
    );

   fetch(request)
    .then(response => response.json())
    .then(data => {
        if (data.cart_summary) {
            // The transaction successfully updated the shopping cart.
            let shoppingCartLink = document.getElementById("shoppingCartNavLink");
            snakeoil.removeChildren(shoppingCartLink);
            shoppingCartLink.innerHTML = `<span class="glyphicon glyphicon-shopping-cart"></span>&nbsp;${data.cart_summary}&nbsp;`;
        }
        else {
            // There was some issue.
            console.log("An error occurred while adding items to cart.");
            console.log(data);
        }
    });
};


snakeoil.showProductDetails = function(product) {
    /* Populate the product details modal with the correct information
    *  and open the modal. This version is for the web shop view.
    */

    // Set the modal title to match the current product.
    let title = document.getElementById("productDetailsModalTitle");
    title.innerText = `${product.sku} - ${product.name}`;

    // Set the correct "add to cart" callback.
    addToCartButton = document.getElementById("productDetailsAddToCartButton");
    addToCartButton.onclick = function() {
        snakeoil.addToCart(productDetailsAddToCartButton, product.pk);
    }

    // Update the product etail fields.
    let tableBody = document.getElementById("productDetailsTableBody");
    snakeoil.removeChildren(tableBody);
    
    for (let key in product) {
        if (key == "pk") continue;
        let humanizedKey = snakeoil.humanizeKey(key);
        snakeoil.addKeyValueRow(tableBody, humanizedKey, product[key]);
    }

    $('#productDetailsModal').modal();
};


snakeoil.showManagedProductDetails = function(product) {
    /* Populate the product details modal with the correct information
    *  and open the modal. This version is for the product management view.
    */

    // Set the modal title to match the current product.
    let title = document.getElementById("productManagementDetailsModalTitle");
    title.innerText = `${product.sku} - ${product.name}`;

    // Update the product etail fields.
    let tableBody = document.getElementById("productManagementDetailsTableBody");
    snakeoil.removeChildren(tableBody);
    
    for (let key in product) {
        if (key == "pk") continue;
        let humanizedKey = snakeoil.humanizeKey(key);
        snakeoil.addKeyValueRow(tableBody, humanizedKey, product[key]);
    }

    $('#productManagementDetailsModal').modal();
};