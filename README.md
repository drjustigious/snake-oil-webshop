# snake-oil-webshop

### A sample Django project demonstrating the elements of a web shop service.

Following the fine tradition of snake oil trade, this web shop does not actually intend to sell anything useful. It is a tech demo and practice project attempting to capture some of the principles of modern web development using the Django framework.

![kuva](https://user-images.githubusercontent.com/44530293/117478006-522b6500-af67-11eb-941d-6a10622c6a29.png)
---

### Feature highlights:
- Search and sort products that are for sale.
- Click on a product to see its full details.
- Add products to your shopping cart without refreshing the page.
- Define new products when logged in as the store manager.

### Additional features:
- Three user roles implemented as Django permission groups.
  - Webmaster (Django staff agent)
  - Manager (shopkeeper)
  - Regular customer
- Web view to check and clear your shopping cart.
- Management scripts to generate demo users and products.
- All custom models exposed via Django Admin.
- Django tests for main features.

### Tech stack:
- MySQL 8
- Python 3.8
- Django 3.2
- Django Rest Framework 3.12
- Bootstrap 3
