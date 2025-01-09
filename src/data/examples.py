query_examples = [
    {"input": "List all film titles.", "sql_query": "SELECT title FROM film LIMIT 5;"},
    {
        "input": "Find the first and last name of all customers.",
        "sql_query": "SELECT first_name, last_name FROM customer LIMIT 5;",
    },
    {
        "input": "Get the total number of staff members.",
        "sql_query": "SELECT COUNT(*) AS staff_count FROM staff LIMIT 5;",
    },
    {
        "input": "Get all categories of films.",
        "sql_query": "SELECT name FROM category LIMIT 5;",
    },
    {
        "input": "Retrieve all addresses of customers.",
        "sql_query": "SELECT address FROM address LIMIT 5;",
    },
    {
        "input": "List some films with their corresponding category names.",
        "sql_query": "SELECT f.title, c.name AS category FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON fc.category_id = c.category_id LIMIT 5;",
    },
    {
        "input": "Find the names of customers who have rented films with Brad Pitt.",
        "sql_query": "SELECT c.first_name, c.last_name FROM customer c JOIN rental r ON c.customer_id = r.customer_id JOIN inventory i ON r.inventory_id = i.inventory_id JOIN film_actor fa ON i.film_id = fa.film_id JOIN actor a ON fa.actor_id = a.actor_id WHERE a.first_name = 'Brad' AND a.last_name = 'Pitt' LIMIT 5;",
    },
    {
        "input": "Get the total sales per store address.",
        "sql_query": "SELECT a.address, SUM(p.amount) AS total_sales FROM store s JOIN address a ON s.address_id = a.address_id JOIN inventory i ON s.store_id = i.store_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY a.address LIMIT 5;",
    },
    {
        "input": "Find all staff members working at Alberta store",
        "sql_query": "SELECT s.first_name, s.last_name FROM staff s JOIN store st ON s.store_id = st.store_id JOIN address a ON st.address_id = a.address_id WHERE a.district = 'Alberta' LIMIT 5;",
    },
    {
        "input": "Get the names of customers who live in Los Angeles.",
        "sql_query": "SELECT c.first_name, c.last_name FROM customer c JOIN address a ON c.address_id = a.address_id JOIN city ci ON a.city_id = ci.city_id WHERE ci.city = 'Los Angeles' LIMIT 5;",
    },
    {
        "input": "Get the total number of rentals and the total sales by category.",
        "sql_query": "SELECT c.name AS category, COUNT(r.rental_id) AS rental_count, SUM(p.amount) AS total_sales \nFROM category c \nJOIN film_category fc ON c.category_id = fc.category_id \nJOIN film f ON fc.film_id = f.film_id \nJOIN inventory i ON f.film_id = i.film_id \nJOIN rental r ON i.inventory_id = r.inventory_id \nJOIN payment p ON r.rental_id = p.rental_id \nGROUP BY c.name \nORDER BY total_sales DESC \nLIMIT 5;",
    },
    {
        "input": "Find the staff members who have processed the most payments.",
        "sql_query": "SELECT s.first_name, s.last_name, COUNT(p.payment_id) AS payment_count FROM staff s JOIN payment p ON s.staff_id = p.staff_id GROUP BY s.staff_id ORDER BY payment_count DESC LIMIT 5;",
    },
    {
        "input": "List the films that are rented the most (including the rental count).",
        "sql_query": "SELECT f.title, COUNT(r.rental_id) AS rental_count FROM film f JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id ORDER BY rental_count DESC LIMIT 5;",
    },
    {
        "input": "Get the names of customers who have rented films in more than one store, with the store details.",
        "sql_query": "SELECT c.first_name, c.last_name, COUNT(DISTINCT i.store_id) AS store_count FROM customer c JOIN rental r ON c.customer_id = r.customer_id JOIN inventory i ON r.inventory_id = i.inventory_id GROUP BY c.customer_id HAVING store_count > 1 LIMIT 5;",
    },
    {
        "input": "Find the average length of films in each category.",
        "sql_query": "SELECT c.name AS category, AVG(f.length) AS avg_length \nFROM category c \nJOIN film_category fc ON c.category_id = fc.category_id \nJOIN film f ON fc.film_id = f.film_id \nGROUP BY c.name \nORDER BY avg_length DESC \nLIMIT 5;",
    },
]
