// Function to add product to cart
function addToCart(productId, phone) {
    // Define the quantity as 1 for simplicity (can be modified as needed)
    let quantity = 1;

    // Create the data to send to the server
    const data = {
        productId: productId,
        phone: phone,
        quantity: quantity
    };

    // Send POST request to the server
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())  // Parse the response as JSON
    .then(data => {
        // Check if the product was successfully added to the cart
        if (data.success) {
            alert('Product added to cart!');
        } else {
            alert('Failed to add product: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the product to the cart.');
    });
}

